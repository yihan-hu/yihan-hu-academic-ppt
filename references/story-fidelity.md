# Story and Case Fidelity

Use this reference when any of the following is true:

- the input includes an approved PPT Planner storyboard or production handoff;
- the talk is teaching, conceptual, tutorial, methods, onboarding, or failure-case driven;
- the user supplied an earlier deck specifically as a reference for flow, explanation order, or speaking style.

## Core boundary

The planner/user owns **what the audience encounters and in what order**. Academic PPT owns **how that approved content is laid out and rendered**.

Content semantics outrank visual abstraction. A cleaner-looking page is not an improvement if it removes the concrete event that teaches the point, changes the reveal order, or replaces a case with a summary.

## Protected handoff fields

When present, treat these planner fields as authoritative:

- `visible_title`;
- `on_slide_copy`;
- `case_setup`;
- `case_steps`;
- `protected_sequence`;
- `concept_revealed_after_case`;
- `must_preserve`;
- approved `speaker_notes`;
- source trace and evidence values.

The builder may shorten only content explicitly marked compressible or wording whose shortening preserves the same visible meaning.

## Case fidelity

A case is a sequence, not a label. Preserve enough concrete detail for the audience to experience the problem.

For a failure case, keep the relevant beats in order:

1. original task or situation;
2. first attempt;
3. concrete failure;
4. patch or attempted fix;
5. new failure, edge case, or cost;
6. heavier or alternative proposal when part of the story;
7. reframing question;
8. smaller/better solution or boundary decision;
9. concept or general rule revealed after the case.

Do not replace these beats with unordered peer cards, a generic pipeline, a single architecture diagram, or a slogan such as `Prompt gets too long`, `GPT over-engineers`, or `More control is not always better`.

If the full protected sequence does not fit legibly, split it across consecutive slides. Preserve the order across the split.

## No premature synthesis

Do not reveal the conclusion before the case earns it.

If `concept_revealed_after_case` is present, do not place that concept or its conclusion in the earlier slide title, subtitle, navigation label, callout, hero text, or opening graphic.

Prefer titles that identify what the audience is looking at:

- `A simple example`;
- `Prompt v1`;
- `What goes wrong?`;
- `Codex: fixing a failing test`;
- `A repeated-step problem`;
- `A more engineered solution`;
- `Another solution`.

Avoid premature takeaway titles such as:

- `More control is not always better`;
- `You do not need GPT's architecture`;
- `This is a paradigm shift`;
- `From answering to completing`;

unless the approved storyboard intentionally uses that claim after the supporting case has already been shown.

## Do not invent meta-slides

Do not add an orientation, synthesis, agenda, “cognitive shift”, “what this means”, or closing-slogan slide merely to make the deck feel polished. Add such a slide only when the user or approved storyboard calls for it, or when navigation is genuinely necessary for a long deck.

A title page may remain a plain title page. A wrap-up may remain a short set of take-home points.

## Reference-deck roles

A supplied prior deck may serve different roles. Infer the narrowest role supported by the user's request:

- `narrative reference`: sequencing, when definitions appear, example-before-concept rhythm, frequency of summaries, title tone;
- `speaking-style reference`: sentence length, transitions, stepwise explanation, numerical detail;
- `brand reference`: approved colors/logos/tokens;
- `layout reference`: geometry and slide composition only when the user explicitly asks to inherit it.

If the user says “参考这个的 flow / 方案”, treat it as a narrative reference by default. Do not silently copy its scientific claims, branding, or layout.

## Build-time audit

Before finalizing a teaching or case-driven deck, check:

- Does every important case still show the concrete task/failure/attempt sequence supplied by the planner or user?
- Did any protected chronological sequence become unordered cards or a generic framework?
- Is any concept or takeaway visible before its planned reveal?
- Did the builder invent an orientation/synthesis/meta slide not present in the approved story?
- Are visible titles descriptive or question-based where the story still needs to unfold?
- If content was dense, was it split rather than abstracted away?
- If a reference deck was supplied for flow, was its narrative cadence used without importing unrelated claims or visual identity?

Any failed item is a content-fidelity failure even if the slide is visually polished.
