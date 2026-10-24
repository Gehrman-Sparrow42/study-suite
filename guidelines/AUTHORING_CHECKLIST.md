# High-yield authoring checklist

Use this before delivering or revising any course. Current user instructions take precedence.

## Content and language

- Retain the major concepts, source terminology, essential mechanisms and useful worked calculations. Reduce repetition and peripheral detail before removing teaching substance.
- Use simple English and short, direct sentences. Easier English should lower reading effort, not add beginner-level explanations.
- Assume basic algebra, logarithms, percentages, powers and routine unit notation. Do not explain fraction bars, multiplication or obvious arithmetic.
- Prefer compact bullets for parallel facts, distinctions and cautions; numbered steps for mechanisms and worked methods. Avoid creating another card merely to repeat its parent's summary.
- Each sentence should add a definition, mechanism, implication, condition, distinction or necessary source qualification. Cut instructions such as “read these points with the explanation above.”
- Read every worked example without its solution or neighboring cards: can the student identify the scenario, all supplied data/units, the requested result(s) and essential assumptions? State the problem before calculations; an answer-only summary fails this check. Check every example, including added illustrations and continuations of multi-part tasks.
- A shorter revision is not a fixed percentage target. Report measured word changes only when useful; do not claim measured study-time savings from a word count.

## Formula keys

- Explain domain-specific quantities, units, sign conventions, timing and validity conditions near the formula.
- Prefer a compact two-column key. Define repeated symbols once per related formula family; state when their meaning changes elsewhere.
- Distinguish genuine ambiguities: scaling exponent versus period count; cost index versus interest rate; current versus intensity; fixed versus total capital.
- Preserve assumptions needed for correct use in Review: payment timing, matching periods, model scope, contribution margin, cost boundary, concentration/voltage convention, etc.
- Skip legends for self-explanatory operators. Do not turn symbol definitions into elementary mathematics lessons.

## Learn and Review

- Learn shows the teaching explanation. Review keeps core statements, formulas/keys, essential conditions, mechanism/worked steps and concise takeaways.
- Ordinary explanatory `body` text already hides in Review. Plain-text bullet paragraphs can stay in that editable host without adding cards.
- When an explanation needs a separate structured bullet block, use `learn_only: true`. A list is not automatically a persistent takeaway.
- Verify what disappears and what stays visible. An active Review button alone is not proof that the shorter mode works.
- In Review, verify the actual problem statement and essential givens remain visible before the worked steps; move them out of any Learn-only body. Preserve missing-input/ambiguity notes rather than silently completing the source.
- Search may temporarily reveal a matching explanation; clearing search must restore Review visibility.

## Preservation and delivery

- Unless current instructions request a different scope, deliver both focused_learning and balanced_high_yield editions. Focused Learn is the complete first-reading path; detailed is the reference. Use the same inventory but separate authored JSON/config, coverage decisions, stable course IDs and HTML filenames. Do not derive depth by a word limit or a label-only config change.

- Inventory the supplied material and retain a coverage/omission record. Preserve original source files and existing HTML editions.
- Inspect the latest saved HTML snapshot before revising. Reconcile personal notes; stop for conflicting edits rather than replacing them.
- Preserve stable IDs and source provenance. Do not publish private course materials or generated exports with reusable project changes.
- For an explicitly requested in-place correction, inspect the saved snapshot, change only intended fields in the existing HTML and its source, and verify edit/export behavior. Do not force a new fix-specific HTML filename. New weeks and alternate reading scopes still preserve separate editions.
- Deliver a clearly named final edition plus its rebuildable JSON, config, selected assets and concise resume/coverage notes beside the course.
- Build and structurally validate. Browser-check actual Learn/Review content, formula rendering, text/formula edits, an edited bullet if applicable, real save/reopen, and a dense mobile section.
- Keep the final report brief: link the recommended edition, state meaningful changes/checks, and disclose only material limitations.
