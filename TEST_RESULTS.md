# Setup verification · 2026-10-18

## Executed checks

- Python 3.13.15: 28 deterministic tests passed (12 builder and 16 weekly-update tests), including paragraph-nesting rejection and omitted optional introductions.
- Node JavaScript syntax check: passed.
- Generated HTML structural validator: passed.
- Microsoft Edge 155 (installed Chromium browser): full browser regression passed.
- Playwright Firefox 153: full browser regression passed.
- Actual local-file HTML download, reopen and second download passed in both browsers.
- The demo includes the weekly snapshot and Auto-save runtime. Repeated edited export sizes remain equal in each tested browser; see ignored tests/artifacts/results.json for current measurements.
- All three delivered demos pass structural validation: the general demo, Weeks 1–5 and Weeks 1–6.
- Edge/Firefox weekly-update browser tests pass: six actual edited fields survive the Week 6 addition, then another edit survives the Week 7 addition.
- Edge/Firefox autosave/recovery tests pass. The picker is mocked in both browsers to exercise identical queue behavior; this does not claim native Firefox file-write support. Writes go to a real backing HTML and its content is checked.

## Browser behavior covered

- True-black background; desktop navigation and scrollspy; short last-section activation at the bottom.
- Learn/Review preserves content and hides only expanded explanations.
- Search across core text, section introduction, raw formulas and hidden/closed explanations; no-result feedback and restored detail state.
- Main title, section heading/navigation label, paragraph and table-cell editing.
- Real Enter/Backspace editing across body paragraphs and in core statements; actual download/reopen verifies the inserted text is still editable, then types more notes and exports again.
- Search opens only matching details, restores prior state as the query changes, retains queries on section jumps, and restores all section links in exports. Search also works with an absent optional introduction.
- Inline-formula deletion/Undo and deliberate DOM reconstruction; delegated formula and figure controls still open the correct dialogs.
- Display and inline LaTeX editing, actual MathJax rendering, and raw-source preservation after export/reopen.
- Embedded SVG image loads after reopening; lightbox zoom and Escape/Close behavior.
- Export resets search filters and dialogs, preserves chosen reading mode and all edited content, and strips MathJax artifacts without deleting the figure.
- Mobile drawer opens/closes, navigation reaches the selected section, table scrolls within its container, no page-wide overflow at 390 px and 320 px.
- Offline/CDN-blocked math shows raw source while editing and saving remain usable.
- Picker cancellation produces no success claim; successful write confirmation follows write/close; denied write falls back to a real download.
- No uncaught page JavaScript errors in the two main browser suites.

## Weekly update coverage

- Source hashing, new/changed/missing reports, renamed identical content and duplicate additions.
- Numeric week sorting and stable section/block identity across reordered sections.
- Browser/source three-way merge, same-change acceptance, conflict rejection, wrong-course/unrecognized-field rejection and untouched old inputs.
- Exclusive output publication, existing output refusal, asset validation before publication, source hashes and week/source linkage checks.
- Legacy HTML/incomplete snapshot refusal, script-ending escaping and a repeated Week 7 addition.
- Real browser Enter-edited paragraphs, heading, raw formula, table cell, figure caption and calculation step are saved to a real download, reconciled and reopened in Edge/Firefox. Search and mobile navigation reach new content; embedded figures remain intact.

## Auto-save and recovery coverage

- Initial connection, immediate first write, subsequent debounced edits and one picker call per connection.
- A deliberately held write followed by newer typing: serialized writes never overlap, and the final backing HTML contains the newest version.
- Denied writes pause Auto-save; reload reveals explicit browser recovery and restores the latest unsaved heading.
- Recovery restores paragraphs, raw inline math and a working formula editor. An undo back to baseline is recoverable even when it produces no remaining changed fields.
- Actual Enter/Shift+Enter edits in core statements retain paragraphs and hard line breaks after recovery. A deliberately delayed failed manual write followed by newer typing produces a real fallback download containing that newest edit.
- Picker cancellation keeps Auto-save off. Unsupported API reports recovery/manual export. Simulated storage quota failure reports recovery unavailable while text remains editable.
- Explicit Save Progress while Auto-save is connected confirms the write. A successful manual write with newer concurrent typing reports that newer edits still need saving; fallback downloads report a request rather than disk completion.
- Exported/reopened documents reset file connection state. File handles are not serialized. Mobile 390/320 px toolbar fits, with Auto-save and Save visible; the 390 px screenshot was inspected.
- OS-native selection/permission behavior remains outside executed automation. Existing real downloads/reopen tests and mocked picker ordering/error tests complement the real backing-file autosave writes.

## Visual inspection and fixes

Inspected desktop overview, dense mechanism/formula section, phone overview, dense phone section and phone formula screenshots. Kept wide mechanisms and derivations, narrow-screen stacking, contained table/math overflow, and restrained typography. Changed the toolbar from translucent to opaque after seeing text behind controls; made status feedback temporary so it does not permanently cover reading material.

Export testing found and fixed empty runtime style attributes and duplicate MathJax context-menu styles across saves. Added cleanup for dynamically loaded MathJax extension scripts. Improved source-heading synchronization after paste and search matching for section introductions. Added bottom-of-page scrollspy handling.

The Argon review follow-up reproduced an Edge editing defect missed by text-replacement tests: Enter could create a div inside an editable p, and reopening moved the inserted content outside its editing host. Text remains in a legal block-level host now; body paragraphs share a single editor. Expanded tests pass in Edge and Firefox. The structural validator now rejects the affected p/block nesting. Source-note search clutter and query-clearing navigation were also corrected. Optional print styling and initial math-performance work remain deferred.

The original Flash High follow-up review ended at the official CLI's 300-second print timeout while its turn was still in progress. The old runner hid this behind a generic missing-output error. After diagnosing it, a focused recheck with an explicit 600-second budget completed in 389 seconds: structured output received, finish gate verified, no findings in the supplied editing/search corrections. The full report and metadata are retained in ignored work/followup-review/FLASH_REVIEW.md and FLASH_RESULT.json. This static review supplements the executed browser regressions; it does not independently run them or cover the entire system.

Flash High supplied a focused test checklist; Codex reviewed it, implemented tests, executed them locally and fixed confirmed issues. This was test-design assistance, not a claim that Flash executed tests. Local brief/result copies are under ignored work/.

Flash High also reviewed the autosave runtime (structured result, gate verified). Codex confirmed visual paragraph/hard-break loss during recovery and a stale snapshot in delayed manual-save fallback; both were corrected and covered by executed Edge/Firefox tests. Manual write failure now flushes recovery immediately, and write completion no longer restarts the newer edit's debounce. The claimed critical RFC-pointer crash was rejected: the builder intentionally generates bare schema paths, not RFC 6901 pointers. The report overstated permanent text loss/severity: raw newline text was retained, but visual formatting needed reconstruction. Existing edit timers and beforeunload recovery also made its manual-failure loss scenario less general than claimed. Full report/metadata: ignored work/autosave-review/FLASH_REVIEW.md and FLASH_RESULT.json.

A focused Flash High recheck also returned structured output with gate verified. Codex confirmed and corrected status clarity for concurrent manual edits, explicit saves while Auto-save is connected and failed-write fallback; the final browser tests exercise these paths. Added newline normalization and a DIV-only paragraph-wrapper guard. Rejected its assumed `h2.editable-text` structure because the template does not generate it; single paragraph prose does not require a p wrapper, other fields preserve breaks with BRs, and leading/trailing whitespace is already normalized by capture. Recheck artifacts: FLASH_RECHECK.md and FLASH_RECHECK_RESULT.json in the same ignored directory. These were bounded static reviews; the final status changes were verified locally, not independently re-reviewed a third time.

## Limits

- The native OS save dialog was not driven end-to-end. Its success/cancel/denied-write branches were tested with a mocked picker API; actual fallback downloads and local-file reopening were tested in Edge and Firefox.
- Mobile checks use desktop browser emulation at phone widths, not physical iOS/Android hardware or Safari.
- Math rendering depends on the pinned MathJax CDN; raw LaTeX is the fallback when unavailable.
- Structural tests do not validate scientific truth, automatically detect English prose, prove complete source coverage or adjudicate image rights. Future course authoring includes those reviews.

Reproduce with commands in README.md. Screenshots, edited downloads and machine-readable results are in ignored tests/artifacts/. The clean delivered demo has none of the test edits.


## 2026-10-19 Learn-only bullet regression

- `python -m unittest discover -s tests -p 'test_*.py'`: 30 pass, including strict boolean validation and rendered editable explanation bullets.
- `python tests/browser_learn_review.py --browser edge`: pass. Learn reveals expanded bullets; Review hides them while retaining formulas, tables and genuine takeaways. Search reveals a matching hidden explanation and clearing restores Review. A real downloaded HTML preserves edited bullet text, editability and Review visibility after reopening. Mobile checks at 390 and 320 px pass without page overflow.
- Firefox run blocked at launch by missing Playwright executable `firefox-1555`; no Firefox result claimed. Test supports `--browser firefox` or `--browser all` when installed.
- Existing default blocks and template runtime are unchanged; block visibility uses existing explanation/search/export behavior.


## 23 October 2026 — focused learning depth

31 unittest tests passed. New test builds a complete valid synthetic reader with config/focused.example.toml and confirms depth metadata does not cut authored content. py_compile and Ruff passed for changed Python files. No template or runtime interaction change. A private real-course focused edition additionally passed actual Learn/Review hiding, persistent process steps, search restoration, text edit/download/reopen, offline reading and 390/320 px layout checks in installed Edge; no page errors. Private coverage/verification records remain outside Git.


## 24 October 2026 — worked-problem authoring checks

Documentation-only rule change using existing summary/steps rendering. In the real course revision, 12/12 worked blocks passed problem-before-solution and Review-visibility checks. Structural validation, existing math rendering, problem-text edit/download/reopen, zero page errors and 390/320 px overflow checks passed. A structured source comparison confirmed that only worked summaries changed; all equations, solution steps, IDs and other content remained unchanged. No renderer code changed, so no unrelated runtime regression rerun.


## 24 October 2026 — in-place worked-example audit

11 delivered course HTMLs inspected; 9 affected files corrected, comprising 69 worked-block instances. All 11 passed structural checks and 390/320 px layout checks in Edge. Affected files passed task-before-solution and actual Review visibility checks for every worked block, plus problem-text edit/download/offline reopen. Existing suite-app and suite-styles contents were checked byte-for-byte unchanged; baseline comparisons allowed only worked-summary changes. No renderer or mathematical method was changed. No new independent scientific audit claimed for this editorial restatement.


## 24 October 2026 — readable lists and emphasis

32 unit tests passed, including escaped bold input and paragraph/list grouping. tests/browser_readability.py passes clean export without false edits, actual strong/list editing, Enter-created list items, Review/search behavior, browser recovery, real export/reopen and snapshot reconcile/rebuild with inline math. Existing Edge smoke/editing, failure/picker/offline, weekly update, autosave/recovery and Learn/Review tests pass. JavaScript syntax, Python compilation and Ruff checks pass. Actual course screenshots inspected at desktop and 390/320 px widths; compact figures remain zoomable. Firefox was not run. Private course outputs stay untracked.

2026-10-24 layout correction: 32 unit tests passed. Real detailed reader checked in Edge at 2559/1440/1000/768/390/320px: no page overflow, bounded main width, matching caption/image widths, readable 640px desktop image. Figure enlargement and sidebar closure passed. Layout detector returned no findings. Three existing private editions updated by replacing only suite-styles; snapshots/content retained.


2026-10-24 reference-led fluid layout: six viewport sizes including actual 2560x1440 widescreen, desktop navigation open/closed, no horizontal overflow or unused outer workspace strip; intrinsic grid reflows. 32 unit tests and browser_readability edit/recovery/download/reopen/rebuild passed. Full-window screenshots inspected. CSS-only export updates preserve snapshots.


2026-10-24 expanded Bionano overhaul: 33 unit tests, Python compile, Ruff, JS syntax and layout detector passed. New flow-step/edit/rebuild and native-disclosure tests passed. Topic folding/search restore and actual export/reopen while search was active passed. Existing Edge smoke, picker/offline, weekly source merges, autosave/recovery and Learn/Review/mobile regression suites passed; OS picker mocked with real backing writes/downloads. Actual three course editions checked at 2560/1920/1366/1000/390/320 widths. Firefox not rerun. Science unchanged beyond formatting/emphasis.


2026-10-24 composition correction: browser_layout.py passes unequal-height adjacency (24px follow-on gap), no overlaps across six viewport sizes, sidebar resize, disclosure resize, companion image alignment, and export stripping viewport-specific spans/reopen. 33 unit tests; browser_readability and existing Edge smoke, picker/offline, weekly, autosave and Learn/Review suites passed. Python compile, Ruff, JS syntax and layout scan passed. Full-window real-course composition inspected, not inferred from overflow checks. Firefox not rerun.


2026-10-24 Bioeng presentation remake: 33 unit tests; browser_readability (now includes multi-paragraph persistent summaries and compact comparisons), browser_layout passed. Both real editions checked at 2560/1920/1366/1000/390/320 with no page overflow/card overlap; full-window screenshots inspected. All worked summaries remain visible in Review. Clean export produced zero false snapshot edits; text/formula edits survived real download/offline reopen. MathJax online rendered four containers. Raw equations, worked steps and numeric tokens preserved against authored source. Firefox not rerun.


2026-10-25 all-course refresh: 11/11 final course HTMLs match current shared JS, pass structural validation and have clean saved snapshots. Economics 2 editions: 20 MathJax nodes each, 12 worked examples each; Biomedical 2: 6 formulas/5 worked each; Lab 2: 13 focused/17 detailed math nodes. Course workers verified widescreen, mobile 390/320, nav states, no overlaps/overflow, essential Review content and real edited/clean export-reopen. Three Microalgae editions pass parent five-width overlap/overflow checks; Bioeng Design builds remain byte-identical to prior verified editions. Separate guide: all 11 sections at five widths, dictionary, keyboard slider and terminal passed, original script and IDs retained. Parent 33 unit tests, browser_layout, browser_readability and local helper syntax passed. Firefox not rerun. Review evidence is bounded to presentation/preservation, not a new scientific audit.


2026-10-29 Smart Materials: single-file reader structure passed; six viewport widths (2560/1920/1366/1000/390/320), no overlap/page overflow, mobile nav, five supplied question prompts/answers visible in Review, search reveal/reset, embedded SVG enlargement/zoom, zero-false-edit clean snapshot, text edit and actual download/offline reopen passed with zero page errors. No display equations required. Source-bundle rebuild byte-identical; original four source hashes unchanged. 33 unit tests; Python compile and Ruff for authoring/QA helpers passed. Scientific-review delegation is now explicitly excluded from Study Suite tasks unless the user asks.

## 2026-10-30 — embedded study brief

- 36 unit tests pass, including HTML escaping, optional legacy compatibility, evidence/section-reference validation and weekly metadata preservation.
- Edge browser_learn_review.py passes hidden brief preservation through actual edited export/reopen, unchanged snapshot metadata, Learn/Review/search and mobile checks.
- Edge smoke and offline/picker-failure branches pass; actual downloads/reopen exercised, OS picker mocked. Evidence: ignored tests/artifacts/study-brief-smoke-results.json.
- Rebuilt synthetic demo passes structural validation. Modified Python files compile and Ruff checks pass with E402 enabled for path-bootstrap imports.
- Full dual-browser smoke invocation reached unavailable Playwright Firefox executable; Firefox not verified. Explicit Edge smoke completed successfully.
- External ChatGPT upload extraction was not tested. The hidden plain HTML brief and structured baseline are in the file, but receiving services may omit hidden text/scripts.

## 2026-10-30 — retrospective study-brief delivery

- 14 existing delivered readers updated in place; exact hidden-only reverse comparison passes.
- Edge compares rendered reading text, editable fields and images before/after: all identical. Hidden metadata remains hidden.
- 13 standard reader actual Save Progress/download/offline reopen checks preserve the brief and prior edit maps; Learn/Review and 2560/390/320 widths pass without page overflow. No page errors.
- One specialized guide: hidden text/JSON checked and original code/markup preserved exactly; no native HTML-export claim.
- 16 matching JSON source renders retain correct edition-specific briefs. Standard source-bundle renderer copies updated only after matching known shared versions.
- Helper Python syntax and Ruff pass. Private inventory, preservation manifest and verification live in ignored work/study-brief-retrofit. External upload extraction remains unverified.

## 2026-10-30: context-only study briefs

Removed the tutor-behavior field and rendered instruction section from all 14 delivered readers and the reusable builder/demo. Course context, reported exam boundaries, evidence/uncertainty and labelled topic-priority opinions remain; imperative priority wording is now descriptive. Receiving assistants choose their own teaching approach. Updated 16 matching source JSONs, three bundled builders and future-authoring rules. Checks: 37 unit tests, helper syntax/lint, all source renders, exact visible-content preservation and the existing 14-reader Edge/13-export verification. Private artifacts stay outside tracked files.

## 2026-10-30 — mixed-scope new-course delivery

- Five inputs inventoried and preserved; 86 teacher pages visually surveyed, question-relevant PDF parameters checked and native PPTX question evidence matched.
- One reader, 18 sections/29 blocks: teacher introduction, two exact five-question sets, third set pending.
- Edge at 2560/1920/1366/1000/390/320: no page overflow/card overlap; mobile navigation, Learn/Review, ten prompts/answers, search restoration, folding and source-condition note pass.
- Actual clean export has zero false edits; bullet and table edits survive a real download and offline reopening. Hidden context-only study brief preserved; no page errors.
- All original hashes unchanged; standalone source bundle rebuild equals actual delivered HTML byte-for-byte.
- 37 unit tests, JS syntax and helper Python syntax/Ruff pass. Full-window screenshots and private evidence retained in ignored work/microbial. Temporary QA exports removed.

## 2026-10-31: contents scroll following

- New tests/browser_navigation.py: Edge, 24 long synthetic entries; follows active section down/up, preserves main scroll during sidebar browsing and wheel-at-edge, avoids same-section snapback, reveals current entry on desktop/mobile reopening, and survives real export/reopen.
- Actual two private editions: section 15 remains visible in contents at 1366×768; reading position unchanged by sidebar-only scroll. Screenshots inspected; source rebuilds byte-identical and snapshots preserved.
- 37 unit tests; Edge smoke plus offline/math and mocked picker branches; Learn/Review/search/export/mobile; layout; readability/edit/recovery pass. JS syntax, Python compile and Ruff pass. Firefox not run.

## 2026-10-31: all delivered readers navigation refresh

- 19 standard readers: actual Edge desktop/mobile follow, independent panel scrolling, reopen, real download/offline reopen and first/last active-link checks pass; snapshots/baselines preserved.
- Custom guide: all 11 desktop tabs and mobile active-tab reveal pass; existing section-switch semantics retained.
- All six renderer JS copies and custom-guide inline scripts pass node --check; private patch/verification helpers compile and pass Ruff.
- Fourteen standard course files, one specialized guide and four older bundled renderer pairs updated. Two Bioinformatics editions, the shared template and three demos already current. Private evidence and before-copies: ignored work/navigation-all.

## 2026-10-31: separate historical-topic supplements

Four existing private editions pass exact prior-section preservation, source/HTML identity, structural validation, six-width Edge layout, Review problem/given/solution visibility and real edited download/offline reopening with study context. Two standalone source-bundle rebuilds match exactly. Arithmetic sanity checks and helper compilation/Ruff pass. No shared renderer change, no new scientific-review claim and no Firefox run. Evidence retained in ignored work/exam-integration-2026-10-31.
