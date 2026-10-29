# V3 Study Suite progress

Last updated: 2026-10-24 (Europe/Istanbul).

## Completed components

- Inspected the V3 setup prompt, V2 guidelines and all five supplied HTML references; preserved originals.
- Implemented the reusable standard-library Python JSON-to-HTML builder and structural validator.
- Added documented TOML defaults/overrides, JSON schema reference, content and visual guidelines, future-use prompt and project operating rules.
- Implemented true-black responsive reader, stable semantic colors, navigation/scrollspy, search, Learn/Review, direct text/table edits, display and inline formula editors, image enlargement/zoom and clean Save Progress export.
- Embedded local figures; enforced image policy, source metadata, path containment, selected-section reconciliation and no-practice configuration.
- Built output/Demo_Study_Suite.html from synthetic content only. No real course summary generated.
- Ran ten builder tests, JS syntax check, structural validation, Edge and Firefox local-file browser regression suites, and desktop/mobile visual inspection.
- Fixed export bloat/empty styles, MathJax extension cleanup, heading synchronization, section-intro search and bottom-section scrollspy.
- Completed the Argon-review implementation follow-up: block-safe text hosts, shared multi-paragraph editors, selective search expansion, query-preserving filtered navigation, optional-intro handling, and delegated formula/figure controls. The rebuilt demo and expanded Edge/Firefox tests pass, including typing more notes after reopening newly inserted paragraphs.
- Updated usage/visual guidelines and verification documentation. Investigated the failed Flash review: the official CLI hit its 300-second print timeout with the turn still in progress. A focused Flash High recheck subsequently completed in 389 seconds with structured output, gate_verified=true, and no findings in the supplied editing/search fixes. Report and metadata are in ignored work/followup-review/FLASH_REVIEW.md and FLASH_RESULT.json. Local regression tests remain the executed behavioral verification.
- Created the private GitHub repository https://github.com/Gehrman-Sparrow42/study-suite, pushed main, and verified the remote SHA matches local implementation commit a5f8e1d4601fc7d40ecf02c91aa14652e5d2c326. GitHub reports isPrivate=true.
- Added first-class numeric week labels, stable course/section/block IDs, source hashes, portable changed-field snapshots and scripts/update.py scan/apply. New editions append authored weeks and reconcile personal notes without resummarizing prior weeks. Conflicting edits/revised sources stop; old editions are preserved.
- Added opt-in Auto-save: select an HTML file once per browser session, then edits write after a 700 ms pause. Writes serialize; edits made during a write trigger another save. Failed writes pause saving and retain notes. Browser recovery after 300 ms supports explicit restore on matching baseline, paragraphs and inline/display math. Unsupported browsers keep recovery/manual export.
- Added synthetic Weeks 1–5 and Weeks 1–6 demos and weekly workflow/schema documentation. New deterministic and browser tests pass at the current checkpoint.
- Integrated the focused Flash autosave review and recheck: confirmed/repaired visual paragraph/hard-break recovery, stale manual fallback export and misleading manual-save status during concurrent edits. Flushed recovery on all failed writes, normalized recovered newlines and removed redundant debounce restart. Rejected assumptions about RFC pointers and heading classes against the actual builder/template. Review artifacts are in ignored work/autosave-review/; final behavioral checks are recorded in TEST_RESULTS.md.

## Important architectural decisions

- Current user instructions override attached references: no quiz, flashcards, question banks, self-testing or practice-question sections. Worked calculations remain teaching components.
- Codex reads and interprets future courses; the builder is deterministic and uses no API key.
- Course JSON and selected local assets are separate from the reusable template. Final HTML embeds CSS, JS and images.
- Browser-edited DOM and raw formula data are the export source of truth. Saved snapshots can merge text/formula edits into the next weekly JSON. Ordinary builds still start from JSON; preserve edited editions separately and use the updater.
- Auto-save file handles stay in memory and require a user picker gesture each session. Browser recovery is separate local storage, never a claim that HTML was written. Downloads remain explicit and are not triggered on every edit.
- MathJax 3.2.2 is optional for rendering; raw LaTeX remains usable if CDN access fails. Only MathJax-generated artifacts are stripped.
- Depth/time/density settings guide authoring, not automatic summarization. English metadata is enforced; English prose is author-reviewed.
- Search temporarily reveals matching explanations and restores detail state. Export clears search/modal state and preserves the reading mode.
- Native picker success requires completed write/close. Download fallback reports a request, not unobservable disk completion.
- The original package and neighboring course folders remain outside the repository. Work logs, screenshots, browser downloads, caches and real-course inputs are ignored.

## Test results and known limitations

Current checkpoint: 28 Python tests pass. Edge/Firefox existing regression, weekly save/update/reopen and autosave/recovery tests pass. Weekly tests preserve six edited fields into Week 6 and append Week 7 after another edit. Autosave tests write an actual backing HTML through a mocked picker, hold a write open while editing, deny permission, reload/restore and check 390/320 px toolbar layout. See TEST_RESULTS.md for final verification and review results.

Native OS picker interaction is mocked in tests; actual download and reopen paths are tested. Mobile checks use 390/320 px browser viewports, not physical phones/Safari. Future real-course source coverage/scientific correctness and image permissions need authoring review.

The requested prompt filename was not present; the supplied `Codex_Study_Suite_V3_Setup_Prompt.md` was used.

## Remaining tasks

No required implementation components remain. At the final checkpoint, finish the current commit/push if publication has not yet completed; verify the remote as described below. Optional print styling and initial math-performance work remain deferred.

Decisions: saved HTML contains a baseline course plus only changed editable fields; source JSON stays plain authored content. Weekly additions reuse prior sections. Updates write new files; old source/export editions remain intact. Legacy HTML without a snapshot must be explicitly reconciled once rather than guessed. Optional print styling and math-startup performance work remain deferred.

Real course authoring is performed only on a separate user request. Private
course sources, coverage records and exports remain outside tracked files.

## Exact next steps for resuming

1. Work in `C:\Users\Berkay\Desktop\Ders\study-suite`; inspect `git status`, `git log -3 --oneline` and `git remote -v` first.
2. Check publication state with `gh repo view Gehrman-Sparrow42/study-suite --json isPrivate,url` and `git ls-remote origin refs/heads/main`.
3. Weekly + autosave implementation and two bounded Flash reviews are complete. Test artifacts: tests/artifacts/results.json, weekly-results.json and autosave-results.json. Reports and dispositions are in TEST_RESULTS.md and ignored work/autosave-review/. If interrupted before publication, review the staged diff, rerun only checks affected by further changes, commit intended files and push main; verify the remote SHA.
4. For the next course, follow README.md's new-course prompt, save staged work in `work/<course>/`, and reuse the template.


## 2026-10-19: bullet explanations in Learn/Review

Added optional validated block-level `learn_only` metadata. Expanded bullet explanations can now use the existing explanation visibility rules instead of being treated as persistent takeaways. They receive the Further explanation label, hide in Review, appear in matching search results and retain visibility behavior and editable notes after export/reopen. Existing blocks default to their previous behavior. Schema and authoring guidelines distinguish long bullet explanations from concise takeaways and keep essential assumptions visible.

Validation: 30 Python tests pass; new Edge browser regression verifies actual block hiding, persistent formulas/tables/takeaways, matching search and clearing, edited bullet export/reopen and 390/320 px modes/layout. Firefox regression is available via tests/browser_learn_review.py, but could not run in this environment because the current Playwright Firefox binary is absent. No template CSS/JS changed.


## 2026-10-19: concise authoring guidance

Clarified that high-yield course prose assumes basic algebra, logarithms and standard unit notation. Formula keys focus on domain variables, units, signs and model scope. Avoid duplicate explanations and elementary operator tutorials. This documentation-only change does not alter the reader/runtime.


## 2026-10-20: reusable high-yield authoring checklist

Added guidelines/AUTHORING_CHECKLIST.md and linked it from AGENTS.md, README.md and CONTENT_GUIDELINES.md. Consolidates simple concise English, useful bullets, compact domain-specific formula keys, shared definitions within formula families, no elementary math tutorials, actual Learn/Review visibility checks, save/reopen verification and personal-edit/source preservation. No renderer/runtime change. Applied and browser-verified in a local course revision; private source/output remains excluded from Git.


## 2026-10-23: private source-aligned course delivery

Applied the existing reader and authoring guidelines to a separately requested real course. Kept private inputs, generated HTML, coverage/source records, selected figures and independent scientific review in ignored work and the user-designated course folder. No reusable renderer or interaction changes. Course-specific Edge checks covered actual Learn/Review visibility, search restoration, MathJax, editable text/formula export/reopen, embedded images, offline reading and 390/320 px layouts. Detailed records remain with the private course source bundle.


## 2026-10-23: concise alternate reading path

Created a separately requested shorter private edition using the unchanged renderer. Preserved the detailed reference and source snapshot, used a distinct course ID, and recorded inclusion/omission decisions beside the course. Actual Learn/Review visibility, search restoration, text edit/export/reopen, offline reading and 390/320 px layout checks passed. Course files remain outside tracked changes.


## 2026-10-23: focused_learning preset and paired authoring

Added validated focused_learning depth metadata and an example config. Agent guidance, new-course prompt, authoring checklist and weekly-update workflow now default to delivering separately authored focused_learning and balanced_high_yield editions together. No word quota or compression ratio; source processing is shared, content selection, course IDs and edit snapshots are edition-specific. Core/cram stays optional, and standalone builder defaults remain compatible. No template/runtime change.

Validation: 31 Python tests pass, including a focused config build and preservation of authored content; changed Python compiles and Ruff checks pass. Private intermediate course example passes structure, actual Learn/Review, retained process steps, search reveal/restore, real edit/download/reopen, offline-reader and 390/320 px browser checks. Existing editions verified unchanged. Course files stay outside commits.


## 2026-10-24: worked-example problem statements

Authoring rules now require each worked example to state its task, essential givens/units and requested results before calculations, visibly in both Learn and Review. Answer-only leads and implied tasks fail the authoring checklist. Missing inputs and illustrative assumptions must remain explicit. The content schema documentation clarifies this use of the existing summary field; no renderer or schema behavior changed.

Applied to all 12 worked blocks in a privately delivered course revision, preserving earlier HTML/source editions and stable IDs. Course-specific checks verified actual Review visibility/order, unchanged equations and solution steps, MathJax, edited-problem save/reopen, and 390/320 px layouts. Private source and verification records remain outside Git.


## 2026-10-24: audit other delivered worked examples

Inspected the existing real-course readers for answer-first or incomplete worked problems. Corrected affected HTML and authored sources in place at the user's explicit request, preserving renderer/runtime and calculations. Short editions without worked blocks needed no change. Removed the redundant prior fix-specific HTML after confirming no unique saved edits and equal baseline content in the corrected original. No new HTML editions were created. Detailed inventory, per-block decisions and actual browser checks remain in ignored authoring work and private course records.


## 2026-10-24: readable explanations and direct subject prose

Added restricted safe **bold** emphasis and semantic body bullet groups inside the existing editable host. Saved-text capture and recovery preserve emphasis, lists and inline math; exported snapshots remain rebuildable. Text measure capped at 75ch and supporting figures made compact and zoomable. Authoring/visual rules now require structure chosen for comprehension, direct subject explanations without routine instructor narration, and actual screenshots after presentation improvements. Existing course-specific conventions and source uncertainties remain qualified.

Applied to the three existing private reader editions in place. Selected parallel information uses labelled bullets; the diagram precedes a two-column methods table, with secondary risks separated. No new controls or decorative redesign. Validation: 32 Python tests, syntax/Ruff checks, new browser formatting/edit/recovery/export/rebuild test, existing Edge editing/search/picker/offline, weekly update, autosave/recovery and Learn/Review regressions passed. Three actual readers pass 390/320 px layout, semantic-list/emphasis visibility and compact figure zoom checks. Screenshots and private source logs remain in ignored course work. Mechanical design warnings were checked against actual computed styles and the required semantic-border design; no unrelated style overhaul.

## 2026-10-24: coherent desktop reading column
Removed the ultrawide offset beside navigation and bounded the main reader to 1040px. Figure headings and content share card text insets; images and captions share a readable width up to 640px. Applied CSS only to three existing private readers and three shipped demos, preserving authored content and saved state. Guides require full-window checks, since isolated card crops hid the spacing defect. Edge layout checks at 2559, 1440, 1000, 768, 390 and 320px passed, plus figure modal and sidebar closure; 32 unit tests and layout detector passed. Actual desktop/mobile captures remain in ignored work.


## 2026-10-24: fluid reference-led reading experience
Supersedes the fixed 1040px column from the preceding checkpoint. User selected the supplied Bionano reader as the broader viewing reference. Intrinsic card grid fills available space, reflows on resize/sidebar changes, and bounds prose within cards. Semantic titles replace repetitive visible category labels; section dividers, full-width comparisons/synthesis, calmer heading scale and quiet metadata establish hierarchy. Images follow their card measure. Applied styles in place to three private readers and three demos without changing content/snapshots. Guidelines and authoring rules capture reference direction. Edge tested at 2560x1440, 1920x1080, 1366x768, 1000x750 and mobile 390/320, with sidebar open/closed. No overflow, available width used; 32 tests and real editing/recovery/export/rebuild test passed. Layout scan clean.


## 2026-10-24: Bionano becomes primary reference; process flows and topic folding
User explicitly strengthened the direction from borrowing a few ideas to future suites being substantially closer to Bionano than earlier outputs. Updated AGENTS and visual/content/schema/checklist guidance accordingly. Added optional process presentation=flow with ordered editable steps, decorative arrows and distinct final stage; native individual explanation disclosures; accessible section fold buttons. Search reveals/restores disclosure and topic state, navigation opens destination, exports restore pre-search topic state. No fixed-height clipping. Current three Microalgae editions rebuilt in place using stable saved snapshots/source identity and three-way reconciliation. Five detailed and two focused process chains now use the flow presentation with existing wording and selective emphasis. No new scientific claims. Shipped demos regenerated. 33 unit tests; Edge editing/recovery/actual download/reopen/rebuild including edited flow stages and topic/search export restoration; existing smoke, picker/offline, weekly update, autosave and Learn/Review tests all passed. Three private editions pass six widths including 2560x1440. Firefox not rerun this milestone. Private screenshots/logs stay ignored.


## 2026-10-24: fix empty lanes and orphan figure composition
The user correctly rejected the prior screenshot: equal rows stranded the figure below a tall left card. Implemented measured card packing inside groups separated by wide comparisons/takeaways; ResizeObserver updates natural-height spans on resize, image/math load, edits and disclosures. Export removes transient measurements and rebuilds them in the new viewport. Added explicit alongside placement for related figures: preceding text cards stack beside the figure, avoiding merely moving an empty lane to the other side. Applied the meaningful companion group to the existing sustainability section and rebuilt all three course editions plus demos. Guides explicitly reject large empty lanes despite passing overflow tests. New browser layout test checks short-card follow-on position, no overlap, companion alignment, resize/navigation/disclosure and clean export/reopen. 33 unit tests and existing Edge smoke/offline/picker, weekly update, autosave/recovery, Learn/Review and formatting/export/rebuild suites passed. Actual three readers pass six widths; final 2560x1440 screenshot inspected. No course claims or calculations changed.


## 2026-10-24: Bioengineering Design readers remade
Updated both existing private editions in place from reconciled source: 8 sections/29 blocks in Midterm Essentials, 6/21 in Focused Learning. Applied current Bionano-led engine plus authored labelled bodies, selective emphasis, design/production visual flows and compact related comparisons. Preserved IDs, raw equations, numeric tokens and all worked solution strings; no pre-existing saved edits. Extended safe persistent summaries to blank-line paragraphs and supported existing compact flag on small comparison cards, allowing clear problem/given/find/boundary layouts and tables beside process chains. Guides and synthetic demos updated. 33 unit tests, browser formatting/recovery/export/rebuild and packing checks passed. Real editions pass six widths/no overlaps, Review problem visibility, zero-false-edit clean export, text/formula edit and actual download/offline reopen; online MathJax rendered four containers. Screenshots inspected at 2560x1440; private artifacts stay out of Git.


## 2026-10-25: refresh all delivered course readers
Inventoried 11 final course HTMLs across five course folders plus the separate interactive in-silico guide. Three course-scoped native workers refreshed Engineering Economics (2), Biomedical (2), Bioeng Lab 3 (2), with exclusive course ownership and no shared-code edits. Both Bioeng Design files were byte-identical to current verified builds; three Microalgae editions received the latest reader without factual-source changes. All 11 now have exact current shared JS, valid structure and clean saved snapshots. Revisions include authored lists/emphasis, real flows, persistent worked problems, compact comparisons and meaningful companions. Worker preservation reports retain original equations, worked solution steps, IDs, numeric evidence, source metadata and caveats; lab copied renderers updated after checking for custom behavior. Separate guide received a scoped presentation adapter with original JS and DOM IDs preserved; all eleven tabs and dictionary/slider/terminal interactions passed. No new scientific claims or source research. Reviewed representative 2560x1440 screenshots; workers checked 390/320 layouts, Learn/Review, real edited/clean export-reopen, formula rendering and retained features. Parent ran 33 unit tests, packing and formatting/recovery/export/rebuild browser tests, static all-file checks and five-width Microalgae overlap checks. Private manifests/screenshots live under work/refresh-all; course materials were not published. Checklist now warns against ID-only edition matching and discarding specialized reader tools.


## 2026-10-25: requested seven-stage laboratory production chain
Expanded the existing opening pipeline block in both Lab 3 editions in place: f/2 preparation, Neubauer counting/dilution correction, inoculum/final volume, cultivation monitoring, biomass harvest, pigment extraction/clarification and quantified outputs. Retained organism/target basis and existing source conditions; all other authored blocks and equations/solutions unchanged. Both source JSONs updated after snapshot reconciliation (0 edits). Stage labels now match their actions, correcting the focused overview's old positional labels. Checklist adds a reusable stage-label/action audit and end-to-end lab overview requirement. Actual Edge 2560x1440 and 390/320, Review visibility, seven stages and real export/reopen checks recorded under ignored work/bioeng-lab-chain.


## 2026-10-29: scoped Smart Materials elective reader and reviewer-policy exception
Delivered one concise English reader in the Smart Material course folder (11 sections/23 blocks), per the user's low-depth mixed exam scope: teacher introduction covered normally; only the five supplied textile questions explained with nearby variation reasoning; membrane teaching content pending its official questions. Four inputs inventoried/hashed unchanged, 60 teacher pages reviewed with visuals, textile question visuals inspected. Source bundle includes coverage/question map, exact source registry, SVG asset and standalone renderer; rebuild byte-identical. Actual Edge six-width overlap/overflow, navigation, Review prompts/answers, search reveal/reset, figure zoom, clean snapshot, edited actual download/offline reopen passed; 33 unit tests and helper syntax/lint passed. Private course sources/outputs are excluded from Git.

During the task the user disabled scientific-review subagents for Study Suite work. Global guidance, reviewer skill and project rules now exclude automatic invocation; factual checks stay with the primary author. The earlier draft review had already completed; no further reviewer was launched. Personal guidance/skill synced, validated, checked and pushed to the private backup (5d75eb6). Mixed-scope/pending-question authoring rule documented.

