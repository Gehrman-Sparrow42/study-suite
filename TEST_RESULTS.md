# Setup verification · 2026-10-18

## Executed checks

- Python 3.13.15: 12 deterministic builder tests passed, including paragraph-nesting rejection and omitted optional introductions.
- Node JavaScript syntax check: passed.
- Generated HTML structural validator: passed.
- Microsoft Edge 155 (installed Chromium browser): full browser regression passed.
- Playwright Firefox 153: full browser regression passed.
- Actual local-file HTML download, reopen and second download passed in both browsers.
- Final demo size: 38,326 bytes. The tested edited export and its second export were both 37,979 bytes in each browser: no accumulation between these cycles.

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

## Visual inspection and fixes

Inspected desktop overview, dense mechanism/formula section, phone overview, dense phone section and phone formula screenshots. Kept wide mechanisms and derivations, narrow-screen stacking, contained table/math overflow, and restrained typography. Changed the toolbar from translucent to opaque after seeing text behind controls; made status feedback temporary so it does not permanently cover reading material.

Export testing found and fixed empty runtime style attributes and duplicate MathJax context-menu styles across saves. Added cleanup for dynamically loaded MathJax extension scripts. Improved source-heading synchronization after paste and search matching for section introductions. Added bottom-of-page scrollspy handling.

The Argon review follow-up reproduced an Edge editing defect missed by text-replacement tests: Enter could create a div inside an editable p, and reopening moved the inserted content outside its editing host. Text remains in a legal block-level host now; body paragraphs share a single editor. Expanded tests pass in Edge and Firefox. The structural validator now rejects the affected p/block nesting. Source-note search clutter and query-clearing navigation were also corrected. Optional print styling and initial math-performance work remain deferred.

A bounded Flash High follow-up review of the fixes was attempted through the official CLI, which returned no structured task output. This is not recorded as a successful external review. The expanded local tests above were executed successfully; the review brief is retained in ignored work/followup-review/.

Flash High supplied a focused test checklist; Codex reviewed it, implemented tests, executed them locally and fixed confirmed issues. This was test-design assistance, not a claim that Flash executed tests. Local brief/result copies are under ignored work/.

## Limits

- The native OS save dialog was not driven end-to-end. Its success/cancel/denied-write branches were tested with a mocked picker API; actual fallback downloads and local-file reopening were tested in Edge and Firefox.
- Mobile checks use desktop browser emulation at phone widths, not physical iOS/Android hardware or Safari.
- Math rendering depends on the pinned MathJax CDN; raw LaTeX is the fallback when unavailable.
- Structural tests do not validate scientific truth, automatically detect English prose, prove complete source coverage or adjudicate image rights. Future course authoring includes those reviews.

Reproduce with commands in README.md. Screenshots, edited downloads and machine-readable results are in ignored tests/artifacts/. The clean delivered demo has none of the test edits.
