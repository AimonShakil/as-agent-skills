# Using domain-skill-blueprint to Design Your Domain Skills
This repository uses a two-skill workflow to build a domain-specific skill library.

The two skills have different jobs:

domain-skill-blueprint (Planner): Decides which skills to build. It analyzes your domain, standards, and operational context and produces a blueprint of all needed skills. You run this once at the start.
skill-creator (Builder): Builds one skill at a time. It takes a single row/spec from the blueprint and creates the actual skill, its reference dependencies, and its evals. You run this repeatedly, one session per skill.
Do not use skill-creator to decide what to build. Do not use domain-skill-blueprint to build a skill.

When to use domain-skill-blueprint
Use it when you need to answer: "What is the complete set of skills required for this domain?"

It is a planning skill. Its output is a document (e.g., blueprint.md), not executable skills.

What it produces
The blueprint document should contain for each proposed skill:

Skill Name
Purpose / Problem it solves
Inputs and Outputs
Parameters / Configuration
Risk Level (Low/Medium/High)
Reference Packs Required (e.g., references/handbook.md, references/regulation.md)
Scripts / Tools it can call
Human Checkpoints / Escalation Rules
Dependencies on other skills
Roadmap Order / Phase
Correct Workflow
Phase 0: Plan

Run /domain-skill-blueprint with your domain context, relevant professional standards, and company constraints.
Review and freeze the resulting blueprint.md. This is your spec.
Do not create any skills in this phase.
Phase 1: Build Foundations First

Build your reference packs before any skill. Typically: references/handbook.md, references/policy.md, references/domain-law.md, etc. Every skill will read these. A skill is only as good as its references.
Phase 2: Build One Skill Per Session

Start a new session for each skill, in the roadmap order defined in the blueprint.
Run /skill-creator and give it ONE skill's row from the blueprint as its complete brief.
Critical: You must paste the spec row into the prompt for skill-creator. Include purpose, inputs, outputs, parameters, risk level, reference packs, scripts, and checkpoints. If you don't, skill-creator will invent its own scope and your library will drift.

Template prompt for building:
  /skill-creator Build the [SKILL-NAME] skill from this spec: [paste its full row from blueprint.md plus governance notes]. It must read [list reference files], cite source in every answer, and follow escalation rules: [list]. Create 3+ evals from these real cases: [paste real anonymized examples].

Validate with real evals. Use 3+ real test prompts from your actual operations, checked against what a human expert would answer. Do not accept generic test cases.
Only move to the next skill when the current one passes its evals. Later-phase skills depend on early ones working.
Phase 3: Re-plan Only When Needed

Go back to domain-skill-blueprint ONLY if the plan itself needs to change - e.g., you need to add, drop, split, or merge a skill based on what you learned during building. Do not re-run it for normal building.
Common Mistakes to Avoid
Giving skill-creator a vague request like "build a skill for ". Always give it the blueprint row.[domain]
Building skills before reference packs are ready.
Building multiple skills in one session.
Using generic evals instead of your own real cases.
