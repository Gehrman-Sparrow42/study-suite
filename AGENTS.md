# Operating rules for Study Suite V3

- Read PROGRESS.md before resuming setup; keep it current at coherent milestones.
- This is a reading resource. No quiz, flashcard, question-bank, self-test or practice-question interface. Worked examples may explain concepts and calculations.
- Use existing templates and scripts for future courses. Codex authors content from all supplied sources; no API-key summarizer.
- Read guidelines/CONTENT_GUIDELINES.md, VISUAL_GUIDELINES.md, CONTENT_SCHEMA.md and AUTHORING_CHECKLIST.md before authoring a course.
- Use concise, simple English and useful bullets. Formula keys explain domain variables, units, signs and assumptions, not elementary arithmetic. Verify that Review actually hides expanded explanations while retaining essential conditions.
- Use English throughout. For a new course, normally author and deliver two separate editions together: focused_learning (recommended first reading) and balanced_high_yield (detailed reference). Core/cram is optional, not a third mandatory output. Current user instructions override this pair, then course config, then builder defaults.
- focused_learning keeps major concepts, causal explanations, important distinctions and essential applications while removing secondary catalogues, specialist detail and repeated examples. Learn must be a complete manageable reading path; Review is its refresher. Length follows course density, never a word count or fixed compression ratio. See guidelines/CONTENT_GUIDELINES.md.
- Inventory every input once and save edition-specific topic coverage maps with source locations and inclusion/omission decisions. Process in batches if needed, but produce one unified HTML per edition. Different depth labels require separately authored content; the builder does not summarize it.
- Give the two editions distinct stable course IDs, dated filenames and source JSON/config files. Preserve each edition's own saved edits separately. Never overwrite a detailed or personal edition to create the focused one.
- Save intermediate course work and a course-specific progress log in work/<course>/; do not commit private course inputs or generated course exports unless requested.
- Preserve true-black design, stable semantic colors, Learn/Review, browser text/formula edits, clean single-file export, embedded images and mobile navigation.
- Do not rewrite or delete original references or source materials. Keep browser-edited exports separate from rebuilt files.
- For new weeks, follow guidelines/WEEKLY_UPDATES.md. Scan the latest source registry, author only new material as a delta, preserve stable course/section/block IDs and reuse prior sections. Import the latest saved HTML snapshot with scripts/update.py; do not replace personal notes with a fresh build. Keep course-specific progress/coverage and new revision filenames. Stop for conflicting edits or revised processed files and reconcile explicitly.
- Build with scripts/build.py and validate with scripts/validate.py. After template/runtime changes run unit and browser tests, including export/reopen and mobile layouts.
- Review scientific content appropriately when a real course warrants it; setup's synthetic measurement demo does not constitute scientific course analysis.
- The private repository contains reusable source, tests, docs and the intentional synthetic demo. Keep logs, test downloads, screenshots, work/, credentials and real course materials out.
