---
name: domain-skill-blueprint
description: Designs the foundational skill library for a business domain or function — given a domain name like HR, Finance, Sales, Legal, Procurement or Customer Support, it decides which Claude/agent skills to build, how much each should cover, how many are needed (a small composable core — typically 10–30 — not hundreds of one-offs), and how they chain into end-to-end workflows. Use this whenever someone asks "what skills do we need for <domain>", wants a skill map, skill catalog, skill inventory, agent capability blueprint or skills roadmap for a department, wants to know whether something deserves its own skill, or is planning an AI/agent rollout across a business function — even if they never say "blueprint".
---

# Domain Skill Blueprint

Turn a business domain name into a **small, composable library of core skills** plus the workflows that combine them.

The failure mode this skill exists to prevent: teams build one skill per request ("write offer letter for engineers", "write offer letter for sales", "write offer letter for interns"…) and end up with hundreds of brittle, overlapping skills nobody can find or maintain. A good library looks more like a well-designed API: a few dozen capabilities, each with a clear job, clear inputs/outputs, parameterized for variants, and composed into workflows at run time.

### Why small and composable (and what's only a heuristic)

The *principle* is well grounded; the *number* is not a standard. Be honest about that distinction in the output.

- **Grounded:** small single-purpose skills can each be tested, replaced and reused, failures stay localized, and each step starts with clean context; a task done once is just a prompt, a skill pays off only when the task repeats. Every installed skill also costs ~100 tokens of discovery metadata per turn, and near-duplicate descriptions cause misfires — so sprawl has a real price.
- **Heuristic:** "10–30 per domain" is a sizing rule of thumb for a department-level function, not an industry standard. There is no formal "industry-standard" count. Let the count *fall out of* the analysis (Step 5), then explain where it landed and why. Don't pad a narrow domain to reach 10 or cram a sprawling one under 30.

## Inputs

- **Domain** (required) — e.g. "HR", "Accounts Payable", "B2B Sales".
- **Optional context** — company size, industry, region/regulation, systems in use (Workday, SAP, Salesforce…), pain points, or a target skill count. If not given, assume a mid-size company (200–2,000 people), multi-region, and say so in the Assumptions section. Don't stall to ask questions; state assumptions and proceed — the user can correct them.

## The blueprint — follow these six steps in order

### Step 1 — Decompose the domain into value streams

Map the domain to 5–9 end-to-end value streams (the big "X-to-Y" lifecycles), then list the recurring processes under each. Anchor on recognized frameworks so the map is defensible rather than invented: APQC Process Classification Framework, SHRM/CIPD body of knowledge for HR, COSO/IFRS for finance, ITIL for IT, SCOR for supply chain, MEDDICC/Winning-by-Design for sales, etc. See `references/domain-maps.md` for starter maps of common domains — use it as a checklist, not a cage.

### Step 2 — Inventory candidate tasks

Under each process, list the concrete tasks a person or agent actually does (draft, review, classify, calculate, answer, reconcile, schedule, monitor). Aim for breadth: 40–100 candidates is normal. Most will *not* become skills — that's the point of the next step.

### Step 3 — Apply the build gate (when to build a skill)

Score each candidate cluster on these criteria. A task earns a skill only when it clears most of them:

| Criterion | Question | Why it matters |
|---|---|---|
| **Recurrence** | Does it happen weekly+ or across many people? | Skills amortize effort; rare tasks don't repay it. |
| **Procedural knowledge** | Does doing it well need steps, policies, templates or domain rules the base model doesn't reliably know? | If a plain prompt already does it well, a skill adds nothing. |
| **Consistency/risk** | Would variation cause compliance, legal, financial or reputational harm? | Skills enforce the "one right way". |
| **Defined I/O** | Can you name the inputs and the artifact/decision it produces? | Undefined outputs can't be tested or composed. |
| **Reusability** | Is it used by more than one workflow or team? | Shared capabilities are the backbone of a composable library. |
| **Testability** | Could you write 3 eval prompts with checkable outcomes? | If you can't test it, you can't improve it. |

Also name explicit **"don't build"** outcomes: things better handled by a plain prompt, a template in a shared drive, an existing system feature (e.g., the HRIS already does it), a deterministic script/automation with no judgment, or a human decision that shouldn't be delegated (terminations, final hiring decisions, pay decisions). Saying what *not* to build is half the value.

**Then put each survivor in the right container.** Not everything that passes the gate is a skill. A skill is a *procedure that needs judgment*. Sort what remains into four buckets, and count only the first:

| Container | What it holds | Examples | Lives where |
|---|---|---|---|
| **Skill** | A repeatable procedure with judgment, producing a defined output | `draft-job-description`, `reconcile-account` | Its own SKILL.md folder |
| **Reference pack** | Knowledge that skills *read* but nobody *runs*: voice, policies, personas, chart of accounts, playbooks, templates | brand voice, handbook, approval matrix | `references/` of the foundation skill that owns it, or a shared knowledge folder |
| **Connector** | Access to a system of record (read, or write when approved) | HRIS, ERP, CRM, ATS, bank portal | MCP server / integration |
| **Script** | Deterministic logic with no judgment: calculations, parsing, formatting | ratio calc, statement parser, UTM builder | `scripts/` inside the skill that calls it |

A common mistake is turning a reference pack into a skill (e.g. `apply-brand-voice`): if its only job is to supply rules other skills follow, it's knowledge, not a capability. Keep a foundation skill only when it does real work on its own (checking a draft against policy, looking up and citing an answer), and let it own the related reference pack.

### Step 4 — Size the scope (how much each skill covers)

Right-size each skill to **one coherent job-to-be-done**, named `verb-object` (e.g. `draft-job-description`, not `recruiting-helper` and not `write-senior-java-jd`).

- **Merge** candidates when they share >~60% of their procedure, knowledge and output shape — and handle the differences as *parameters* (role level, region, employment type, tone). Offer letters for every job family = one skill with parameters.
- **Split** when instructions diverge substantially, the tools/permissions differ (read-only analytics vs. writing to the HRIS), the risk level differs (an FAQ answer vs. an investigation report), or the SKILL.md would blow past ~500 lines.
- **Too narrow smell:** the name contains a specific role, region or customer. **Too broad smell:** the name is a department ("HR assistant") or you can't state a single output.

### Step 5 — Settle the count (how many you need) in three tiers

Derive the count rather than aiming at it. The per-stream allowance depends on domain shape — a small team can't maintain or test many skills, and in a narrow domain each "value stream" is often just one person's job:

| Domain shape | Foundation | Core per value stream | Typical result | What to do |
|---|---|---|---|---|
| Narrow sub-function (Treasury, Payroll, Recruiting-only, AP) | 1–2 | 1–2 (default 1) | 4–10 | Fine to come in under 10 — say so and explain. Prefer borrowing foundation skills from the parent function over rebuilding them. Add a second skill to a stream only if the two jobs have different inputs, cadences *and* outputs. |
| Department-level function (HR, Finance, Sales, Marketing, Support) | 3–6 | 1–4 | 10–30 | The normal case. |
| Very broad or heavily regulated (Legal, IT, "Operations", a whole business unit) | shared | per sub-domain | would exceed 30 | Split into sub-domains, each with its own library, sharing one foundation tier. Don't force it under 30 by over-merging different jobs. |

When torn between N and N+1 skills, choose N and list the extra one as "conditional — build if <trigger>". It's cheap to add a skill later and costly to maintain one nobody uses.

If the user is planning across several domains, point out which foundation skills (document drafting, data analysis, policy lookup, PII redaction) should be **shared enterprise-wide** rather than duplicated per domain.

Organize the library into tiers so composition is obvious:

1. **Foundation (cross-cutting) skills — ~1–6, per the table.** Reused by nearly every workflow in the domain: policy/knowledge lookup, domain-specific document drafting standards, data analysis/reporting, compliance/jurisdiction check, communication tone. Build these first; everything else leans on them.
2. **Core process skills.** One per high-value job-to-be-done that passed the gate, within the per-stream allowance above.
3. **Workflows (orchestrations) — not counted as skills.** Named sequences that chain foundation + core skills for an end-to-end outcome (e.g. "new-hire onboarding"). Keep workflows as compositions so a change to one skill improves every workflow that uses it.

Sanity-check the result against the table: a low count for a broad domain usually means you merged genuinely different jobs or skipped a value stream; a high count usually means variants that should be parameters, or tasks that failed the gate. Run a consolidation pass before finalizing, report what you merged, and state in one line where the count landed relative to the domain shape and why.

### Step 6 — Sequence the workflows

For each value stream, show the end-to-end workflow as an ordered chain of skills with the hand-off artifact between steps and where a **human checkpoint** sits (approvals, sensitive decisions). Every core skill should appear in at least one workflow; a skill that appears in none is a sign it isn't needed. Then produce a phased build roadmap: foundation first, then the skills that unlock the most workflows or the highest-volume pain points.

## Output format

Use this structure (Markdown). Tables over prose wherever possible — the reader is going to use this as a build plan.

```
# <Domain> Core Skill Library

## Executive summary
2–4 sentences: how many skills, how they're tiered, the 3 to build first and why.

## Assumptions & scope
Company profile assumed, regions/regulations, systems, what's out of scope.

## 1. Value-stream map
Table: value stream | key processes | reference framework

## 2. Build-gate results
Short table of the notable candidates and verdicts (Build / Merge into X / Don't build — why).
Include a "Don't build" list with the alternative (template, system feature, script, human-only).
Then a short container table: what became a reference pack, connector or script instead of a skill.

## 3. The core skill library
### Tier 1 — Foundation skills
### Tier 2 — Core process skills (grouped by value stream)
Table per tier: # | skill-name | purpose (one line) | inputs | output | parameters (variants handled) | risk level | used by workflows

## 4. Workflows (compositions)
For each: numbered chain → `skill-a` → `skill-b` → [HUMAN: approve] → `skill-c`, with hand-off artifacts.

## 5. Consolidation log
What was merged/parameterized and why (shows the count is deliberate).

## 6. Build roadmap
Phase 1 / 2 / 3 with skills, rationale, and success metric per phase.

## 7. Governance notes
Ownership, eval set per skill (3+ prompts), data-privacy/PII handling, review cadence, plus the regulated-domain defaults below where they apply.

## 8. Questions to validate with a domain expert
5–10 specific, answerable questions about the assumptions most likely to change the library
(e.g. "Does Treasury or Controllership own hedge documentation? If Controllership, drop X.").
For each, say which skill(s) the answer would add, drop or reshape.
```

**Why section 8 matters:** the person asking is often not a specialist in the domain — they're planning the AI rollout and will take this to the people who do the work. Give them the exact questions that would most change the plan, so the expert review is fast and focused rather than a vague "please check this".

### Governance defaults for regulated or high-stakes domains

When the domain handles money, legal obligations, personal data or regulated records (finance, HR, legal, healthcare, procurement), include these defaults in section 7 and reflect them in the skill designs. They exist because auditors and regulators treat agent actions like any other user's actions:

- **Draft, don't execute (at first).** Agents prepare drafts, proposals and pending records; people post, pay, sign, send externally and approve. Revisit after controls over the agent are designed and tested.
- **Calculations in scripts, not in the model's head.** Anything numeric that someone will rely on runs in a deterministic script the skill calls, so results are reproducible and checkable.
- **Skills are controlled artifacts.** A skill that supports a key control (e.g. a SOX control) is version-controlled and changes go through review, like any program change.
- **Least privilege and segregation of duties.** The agent's system accounts get read-only or draft-only roles; never a create-plus-approve combination.
- **Evidence by default.** Outputs record their sources, query/run time and control totals so a reviewer can re-perform them.

Keep skill names kebab-case, `verb-object`, unique, and free of role/region/customer specifics. After the document, offer to scaffold any skill from the library (e.g., with the skill-creator skill) or to tailor the library to the user's actual systems and policies.

## Quality bar — check before you hand it over

- The count fits the domain shape (Step 5 table), and the consolidation log justifies it — no padding, no over-merging.
- The output doesn't present the 10–30 range or any count as an "industry standard".
- Every core skill clears the build gate and appears in at least one workflow.
- Variants are parameters, not separate skills.
- High-risk decisions have human checkpoints and are never fully delegated.
- Regulatory/jurisdiction concerns relevant to the domain are named (e.g., GDPR, EEOC/Title VII, FLSA for HR; SOX for finance).
- The "don't build" list exists and is specific.
- Knowledge-only items (voice, policies, personas, templates) are reference packs, not skills.
- Section 8 lists specific expert-validation questions tied to the skills they would change.
