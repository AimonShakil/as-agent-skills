---
name: interview-scheduler
description: End-to-end interview operations — finds a slot that works for the whole interview panel (from availability pasted in the prompt or from panelists' Gmail replies, requesting it by email when missing), creates the Zoom meeting, copies the candidate evaluation sheet from the Google Drive template and shares it with the panelists, and drafts/sends the candidate invitation and the panelist briefing emails. Use this whenever someone wants to schedule, set up, book, coordinate or arrange an interview, panel, loop, onsite, technical round or hiring call with a candidate — even if they only mention one piece ("find a time for the panel", "send the candidate the Zoom link", "make a scorecard for Sara's interview", "check when the interviewers are free").
---

# Interview Scheduler

Turn "schedule X's interview with this panel" into a finished, confirmed interview: an agreed slot, a Zoom link, an evaluation sheet each panelist can edit, and the right email in each person's inbox.

The coordinator is accountable for what reaches a candidate, so the skill does all the preparation and gathers every outgoing email into **one confirmation checkpoint** before anything is sent. Mistakes here are visible to external people (wrong time zone, wrong name, a scorecard shared with the candidate), and they can't be unsent.

## Tools this skill uses

| Step | Tool | If unavailable |
|---|---|---|
| Availability from email | Gmail `search_threads`, `get_thread` | Ask the coordinator to paste availability |
| Request availability | Gmail `create_draft` → `send_message` (draftId) | Give the coordinator the text to send |
| Slot matching | `scripts/find_common_slots.py` | Do the intersection by hand, showing the work |
| Zoom meeting | Zoom MCP connector (`create_meeting` or similar), when connected | Ask the coordinator for a join link (see Step 3) |
| Evaluation sheet | Drive `search_files`, `copy_file`, `share_file` | Stop and ask where the template is |
| Fill sheet header | `google-workspace` skill (Sheets editing) | Put the details in the file description using Drive `update_file` |
| Emails | Gmail `create_draft`, then `send_message` with `draftId` | — |

Load deferred tools with ToolSearch before calling them (e.g. `select:mcp__claude_ai_Gmail__create_draft`). Zoom tool names vary between connectors, so search for `zoom meeting` to find what's available.

## Step 0 — Gather the brief

Pull these from the prompt and the conversation. Ask once, in a single message, only for what's missing and needed. Don't ask for things you can find in Gmail or Drive.

- **Candidate**: full name, email, role/position, time zone (if unknown, ask; don't guess it from the email domain)
- **Panel**: name + email for each interviewer, plus each one's role in the interview (e.g. "system design", "hiring manager") if given
- **Interview**: round/type, duration (default 60 min), date window (default: next 5 business days), and the coordinator's time zone
- **Availability**: pasted in the prompt, or "check email"
- **Template**: name of the evaluation template if the coordinator knows it

Write the brief to `interview_brief.json` in the working directory (or outputs folder) so later steps and reruns use the same facts:

```json
{
  "candidate": {"name": "", "email": "", "role": "", "timezone": ""},
  "panel": [{"name": "", "email": "", "focus": ""}],
  "interview": {"round": "", "duration_min": 60, "window_start": "YYYY-MM-DD", "window_end": "YYYY-MM-DD", "coordinator_tz": ""},
  "availability": {},
  "slot": null, "zoom": null, "sheet": null
}
```

## Step 1 — Collect panel availability

**From the input.** Normalize what the coordinator pasted into explicit intervals with a time zone, e.g. `{"start": "2026-10-20T14:00", "end": "2026-10-20T17:00", "tz": "America/New_York"}`. If someone gives "Tue afternoon", resolve it against the date window and state how you read it ("Tue afternoon → Tue 20 Oct, 12:00–17:00 ET"), since a wrong reading is costly.

**From email.** For each panelist without availability in the input, search Gmail for recent replies about this interview, e.g. `from:<email> newer_than:14d (availability OR available OR interview OR "<candidate first name>")`. Open the matching thread with `get_thread` and extract the windows they offered. Note which message each window came from, so the coordinator can check it.

**Missing availability.** If a panelist has no availability anywhere, draft an availability request to them (template in `references/email-templates.md`, "Availability request"). Show the coordinator the drafts and send them only after the coordinator approves. Then **pause**: tell the coordinator who you're waiting on and that you'll continue once they reply (or once the coordinator pastes the answer). Don't schedule around a panelist you haven't heard from unless the coordinator says that panelist is optional.

## Step 2 — Pick the slot

Put the intervals into the brief and run:

```bash
python <skill-dir>/scripts/find_common_slots.py interview_brief.json
```

The script converts every interval to UTC, intersects them across all required panelists, keeps slots of the requested duration, and prints each candidate slot in UTC, the coordinator's zone and the candidate's zone. It also flags slots that fall outside 08:00–19:00 in the candidate's zone.

- **One or more slots:** propose the earliest reasonable slot (inside the candidate's working hours), plus up to two alternatives.
- **No overlap:** say so plainly, show the closest near-misses (the slot where everyone but one person is free), and ask whether to drop an optional panelist, extend the window, or request more availability. Don't invent a slot.

Have the coordinator confirm the slot before you create the meeting or the sheet. Those steps are cheap to redo, but emails built on a wrong slot are not.

## Step 3 — Create the Zoom meeting

If a Zoom connector is available, create a scheduled meeting:
- Topic: `Interview: <Candidate Name> — <Role> (<Round>)`
- Start: the confirmed slot in UTC (or with an explicit time zone), duration from the brief
- Settings when supported: waiting room on, join before host off, panelists as alternative hosts if the connector allows it

Record the join URL, meeting ID and passcode in the brief.

If no Zoom connector is connected, don't fake it and don't block the rest of the work. Ask the coordinator to create the meeting and paste the join link, and carry on with the sheet in the meantime. Never put a placeholder link like `zoom.us/j/XXXX` in an email draft. Hold the email drafts until the real link arrives.

## Step 4 — Create and share the evaluation sheet

1. **Find the template.** Search Drive for the template:
   `title contains 'Evaluation' and title contains 'Template' and mimeType = 'application/vnd.google-apps.spreadsheet'`.
   Broaden the search if nothing comes back (`'Scorecard'`, `'Interview Feedback'`). If more than one template matches, pick the one whose title names the role or round, or ask. If none exists, stop and ask the coordinator for the template, because a made-up scorecard would undercut a hiring process that relies on consistent rubrics.
2. **Copy it** with `copy_file`, titled `<Candidate Name> — <Role> — <Round> Evaluation — <YYYY-MM-DD>`. Keep it in the template's folder unless the coordinator names another.
3. **Fill the header** (candidate, role, round, date/time, panelists, Zoom link) using the `google-workspace` skill if Sheets editing is available. Otherwise, write those details into the file description with `update_file` and tell the coordinator that the header cells still need filling.
4. **Share** with each panelist as `writer` using `share_file`. Share only with panelists. The candidate must never get access to the evaluation sheet. Before every share call, check that the address isn't the candidate's.

Record the sheet URL and ID in the brief.

## Step 5 — Draft the emails

Use the templates in `references/email-templates.md`. Create Gmail drafts (`create_draft`); don't send yet.

- **Candidate invitation:** one email to the candidate. It contains the date/time **in the candidate's time zone** (with the coordinator's zone in brackets), duration, Zoom link + meeting ID + passcode, panel names and titles (if known), and what to prepare. Leave out the evaluation sheet, internal notes and panelists' email addresses.
- **Panelist briefing:** one email to all panelists (To: panelists; no candidate in To/Cc/Bcc). It contains the time in the coordinator's zone, Zoom link, evaluation sheet link, candidate name/role and any resume or profile link given, each panelist's focus area, and a feedback deadline (default: within 24 hours of the interview).

Before saving, read each draft's recipients again. The candidate's draft should list only the candidate (plus any Cc the coordinator asked for), and the panelist draft should not include the candidate.

## Step 6 — Confirmation checkpoint, then send

Show the coordinator one summary:

```
Interview: <Candidate> — <Role> (<Round>)
When:      <Day, DD Mon YYYY, HH:MM–HH:MM coordinator TZ>  /  <candidate TZ time>
Zoom:      <join URL>  (ID <id>, passcode <pc>)
Sheet:     <URL>  — shared (editor) with: <panelist emails>
Drafts:    1. To <candidate email> — "<subject>"   [view link]
           2. To <panelist emails> — "<subject>"   [view link]
Open items: <anything still missing, e.g. header cells not filled>
Send both drafts now? (yes / edit / hold)
```

Send only after an explicit yes, using `send_message` with each `draftId`. If the coordinator says "send the panel one only" or "hold", do exactly that. After sending, report what was sent and what's still open.

When running non-interactively (no coordinator to answer), stop at this checkpoint: leave the drafts unsent and present the summary.

## Reschedules and partial requests

- **Only part of the flow** ("just make the scorecard", "only find a time"): run those steps alone, reading anything already done from the brief or the conversation.
- **Reschedule:** reuse the existing sheet (rename it with the new date), update or recreate the Zoom meeting, and draft "Updated time" emails that clearly mark the previous time as cancelled.
- **Several candidates in one request:** handle each as its own brief and show one checkpoint per candidate, so one person's mistake can't spill into another's emails.
