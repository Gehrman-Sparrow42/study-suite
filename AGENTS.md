# Operating rules for Study Suite V3

- Read PROGRESS.md before resuming setup; keep it current at coherent milestones.
- This is a reading resource. No quiz, flashcard, question-bank, self-test or practice-question interface. Worked examples may explain concepts and calculations.
- Use existing templates and scripts for future courses. Codex authors content from all supplied sources; no API-key summarizer.
- Read guidelines/CONTENT_GUIDELINES.md, VISUAL_GUIDELINES.md and CONTENT_SCHEMA.md before authoring a course.
- Use English throughout. Default balanced_high_yield; preserve major concepts and source vocabulary. Current user instructions override course config, which overrides defaults.
- Inventory every input and save a topic coverage map with source locations and inclusion/omission decisions. Process in batches if needed, but produce one final HTML.
- Save intermediate course work and a course-specific progress log in work/<course>/; do not commit private course inputs or generated course exports unless requested.
- Preserve true-black design, stable semantic colors, Learn/Review, browser text/formula edits, clean single-file export, embedded images and mobile navigation.
- Do not rewrite or delete original references or source materials. Keep browser-edited exports separate from rebuilt files.
- Build with scripts/build.py and validate with scripts/validate.py. After template/runtime changes run unit and browser tests, including export/reopen and mobile layouts.
- Review scientific content appropriately when a real course warrants it; setup's synthetic measurement demo does not constitute scientific course analysis.
- The private repository contains reusable source, tests, docs and the intentional synthetic demo. Keep logs, test downloads, screenshots, work/, credentials and real course materials out.
