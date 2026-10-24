/* Raw formula source and editable DOM are the document's persistent state. */
(() => {
'use strict';
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
let dirty = false, activeFormula = null, mathQueue = Promise.resolve(), statusTimer;
let editVersion = 0, fileHandle = null, autoEnabled = false, autoTimer, recoveryTimer;
let writeQueue = Promise.resolve();
const status = text => {
 $('#status').textContent = text;
 clearTimeout(statusTimer);
 statusTimer = setTimeout(() => { $('#status').textContent = ''; }, 9000);
};
const markDirty = () => {
 dirty = true; editVersion++;
 $('#save-state').textContent = autoEnabled ? 'Changes waiting to auto-save…' : 'Unsaved HTML changes · browser recovery pending';
 clearTimeout(recoveryTimer); recoveryTimer = setTimeout(saveRecovery, 300);
 scheduleAutoSave();
};
const mobile = () => matchMedia('(max-width: 720px)').matches;
function setNavigation(open) {
  document.body.classList.toggle('nav-open', mobile() && open);
  document.body.classList.toggle('nav-closed', !mobile() && !open);
  $('#nav-toggle').setAttribute('aria-expanded', String(open));
  $('#scrim').hidden = !(mobile() && open);
}
$('#nav-toggle').onclick = () => setNavigation($('#nav-toggle').getAttribute('aria-expanded') !== 'true');
$('#scrim').onclick = () => { setNavigation(false); $('#nav-toggle').focus(); };
matchMedia('(max-width: 720px)').addEventListener('change', () => setNavigation(!mobile()));
setNavigation(!mobile());
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && mobile()) setNavigation(false);
});
function mode(value) {
  document.body.dataset.mode = value;
  $('#learn').setAttribute('aria-pressed', String(value === 'learn'));
  $('#review').setAttribute('aria-pressed', String(value === 'review'));
  requestAnimationFrame(scrollSpy);
}
$('#learn').onclick = () => mode('learn');
$('#review').onclick = () => mode('review');
function matchesContent(element, query) {
 return element.textContent.toLowerCase().includes(query) || [...element.querySelectorAll('[data-raw]')].some(e => e.dataset.raw.toLowerCase().includes(query)) || [...element.querySelectorAll('img')].some(e => e.alt.toLowerCase().includes(query));
}
function search() {
 const query = $('#search').value.trim().toLowerCase();
 document.body.classList.toggle('searching', Boolean(query));
 let count = 0;
 $$('.section').forEach(section => {
   const headingMatch = [...section.querySelectorAll('.section-heading, .section-intro')].some(e => matchesContent(e, query));
   let found = false;
   section.querySelectorAll('.block').forEach(block => {
     const match = !query || headingMatch || matchesContent(block, query);
     block.hidden = !match;
     if (match) { found = true; count++; }
   });
   section.hidden = !found;
   document.querySelector(`nav a[href="#${section.id}"]`).hidden = !found;
   // Search may reveal text inside a closed explanation without altering saved preference.
   section.querySelectorAll('details').forEach(detail => {
     if (query && !detail.hasAttribute('data-before-search')) detail.dataset.beforeSearch = String(detail.open);
     if (query) detail.open = detail.dataset.beforeSearch === 'true' || (!detail.closest('.block').hidden && matchesContent(detail, query));
     else if (detail.hasAttribute('data-before-search')) { detail.open = detail.dataset.beforeSearch === 'true'; delete detail.dataset.beforeSearch; }
   });
 });
 $('#search-status').hidden = !query;
 $('#search-status').textContent = count ? `${count} matching reading blocks. Search includes expanded explanations.` : 'No matching concepts. Try another term.';
 requestAnimationFrame(scrollSpy);
}
$('#search').addEventListener('input', search);
$$('nav a').forEach(link => link.onclick = () => {
 if (mobile()) setNavigation(false);
 const section = document.getElementById(link.hash.slice(1));
 section.setAttribute('tabindex', '-1'); section.focus({preventScroll:true});
});
let scrollScheduled = false;
function scrollSpy() {
 scrollScheduled = false;
 const sections = $$('.section').filter(s => !s.hidden);
 const atBottom = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 3;
 const current = atBottom ? sections.at(-1) : sections.filter(s => s.getBoundingClientRect().top <= (mobile() ? 160 : 125)).pop() || sections[0];
 $$('nav a').forEach(a => { if (current && a.hash === '#' + current.id) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); });
}
window.addEventListener('scroll', () => { if (!scrollScheduled) { scrollScheduled = true; requestAnimationFrame(scrollSpy); } }, {passive:true});
scrollSpy();
function syncHeading(target) {
 const heading = target.closest('.section-heading');
 if (heading) document.querySelector(`nav a[href="#${heading.closest('.section').id}"] .nav-title`).textContent = heading.querySelector('h2').textContent;
 if (target.matches('h1')) document.title = target.textContent;
}
document.addEventListener('input', event => {
 if (event.target.closest('[contenteditable]')) {
   markDirty();
   syncHeading(event.target);
 }
});
// Paste as text: copied web formatting must not introduce scripts, images or nested layouts.
document.addEventListener('paste', event => {
 if (!event.target.closest('[contenteditable]')) return;
 event.preventDefault();
 const selection = getSelection();
 if (!selection.rangeCount) return;
 const range = selection.getRangeAt(0); range.deleteContents();
 const node = document.createTextNode(event.clipboardData.getData('text/plain'));
 range.insertNode(node); range.setStartAfter(node); range.collapse(true); selection.removeAllRanges(); selection.addRange(range);
 syncHeading(event.target);
 markDirty();
});
function renderMath(element) {
 mathQueue = mathQueue.catch(() => {}).then(async () => {
   if (window.MathJax?.typesetClear) window.MathJax.typesetClear([element]);
   element.textContent = element.dataset.display === 'inline' ? '\\(' + element.dataset.raw + '\\)' : '\\[' + element.dataset.raw + '\\]';
   if (window.MathJax?.typesetPromise) {
     try { await window.MathJax.typesetPromise([element]); }
     catch { element.textContent = element.dataset.raw; }
   }
 });
 return mathQueue;
}
// Delegate to keep controls working if editing/undo reconstructs their nodes.
document.addEventListener('click', event => {
 const button = event.target.closest('.edit-formula');
 if (button) {
   activeFormula = button.closest('.math-unit').querySelector('.equation-render');
   $('#formula-source').value = activeFormula.dataset.raw;
   $('#formula-dialog').showModal(); $('#formula-source').focus();
 }
 const figure = event.target.closest('.figure-open');
 if (figure) {
   const stage = $('#image-dialog .image-stage'); stage.replaceChildren(figure.querySelector('img').cloneNode(true));
   stage.classList.remove('zoomed'); $('#zoom').textContent = 'Zoom in'; $('#image-dialog').showModal();
 }
});
$('#cancel-formula').onclick = () => $('#formula-dialog').close();
$('#apply-formula').onclick = () => {
 activeFormula.dataset.raw = $('#formula-source').value;
 renderMath(activeFormula); markDirty(); $('#formula-dialog').close();
};
$('#close-image').onclick = () => $('#image-dialog').close();
$('#zoom').onclick = () => { const zoomed = $('.image-stage').classList.toggle('zoomed'); $('#zoom').textContent = zoomed ? 'Fit figure' : 'Zoom in'; };
function authoredText(element) {
 // Preserve paragraph boundaries and raw inline formulas, not MathJax SVG text.
 function visit(node, root = false) {
   if (node.nodeType === Node.TEXT_NODE) return node.textContent;
   if (node.nodeType !== Node.ELEMENT_NODE) return '';
   if (node.matches('.math-unit')) return '\\(' + node.querySelector('[data-raw]').dataset.raw + '\\)';
   if (node.tagName === 'BR') return '\n';
   const value = [...node.childNodes].map(child => visit(child)).join('');
   if (['STRONG', 'B'].includes(node.tagName)) return '**' + value + '**';
   if (!root && node.tagName === 'LI') return '- ' + value.trim() + '\n';
   if (!root && node.tagName === 'UL') return '\n\n' + value.trim() + '\n\n';
   return !root && ['P', 'DIV'].includes(node.tagName) ? '\n\n' + value + '\n\n' : value;
 }
 return visit(element, true).replace(/\n{3,}/g, '\n\n').replace(/^\n+|\n+$/g, '').replace(/\u00a0/g, ' ');
}
function collectEdits() {
 const state = JSON.parse($('#suite-state').textContent);
 const expected = new Set(state.rendered_fields);
 const edits = {}, seen = new Set();
 let captureError = '';
 try {
   $$('[data-field]').forEach(element => {
     const pointer = element.dataset.field;
     if (!expected.has(pointer) || seen.has(pointer)) throw new Error('Editing structure changed.');
     seen.add(pointer);
     const baseline = pointer.split('/').reduce((value, key) => value[key], state.baseline);
     const value = element.matches('.equation-render') ? element.dataset.raw : authoredText(element);
     if (value !== baseline) edits[pointer] = value;
   });
   if (seen.size !== expected.size) throw new Error('An editable field was removed.');
 } catch {
   // The HTML still exports safely. An incomplete snapshot must never silently
   // overwrite source content on the next weekly update.
   captureError = 'Editing structure changed; reconcile visible HTML manually before updating.';
 }
 state.edits = edits;
 delete state.capture_error;
 if (captureError) state.capture_error = captureError;
 return {state, captureError};
}
function captureEdits(clone) {
 const {state, captureError} = collectEdits();
 clone.querySelector('#suite-state').textContent = JSON.stringify(state).replace(/</g, '\\u003c');
 return captureError;
}
function exportHTML() {
 const clone = document.documentElement.cloneNode(true);
 const captureError = captureEdits(clone);
 clone.querySelectorAll('.equation-render').forEach(element => { element.replaceChildren(); element.textContent = element.dataset.raw; });
 // Only MathJax-generated assets are replaceable. Never remove educational SVGs.
 clone.querySelectorAll('mjx-container, [id^="MJX-"], [id^="MathJax-"], .CtxtMenu_Menu, script[data-math-loader]').forEach(e => e.remove());
 clone.querySelectorAll('style:not(#suite-styles)').forEach(e => { if (e.textContent.includes('.CtxtMenu_')) e.remove(); });
 clone.querySelectorAll('script[src^="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/"]').forEach(e => e.remove());
 clone.querySelectorAll('[contenteditable]').forEach(e => {
   e.removeAttribute('autofocus');
   if (e.getAttribute('contenteditable') === 'true') e.setAttribute('spellcheck', 'false');
 });
 clone.querySelectorAll('[style]').forEach(e => { if (!e.getAttribute('style').trim()) e.removeAttribute('style'); });
 clone.querySelectorAll('.section,.block,nav a').forEach(e => e.removeAttribute('hidden'));
 clone.querySelectorAll('details[data-before-search]').forEach(e => { e.open = e.dataset.beforeSearch === 'true'; delete e.dataset.beforeSearch; });
 clone.querySelectorAll('dialog').forEach(e => e.removeAttribute('open'));
 clone.querySelector('.image-stage').replaceChildren();
 clone.querySelector('#formula-source').textContent = '';
 clone.querySelector('#search').setAttribute('value', '');
 clone.querySelector('#search-status').hidden = true;
 clone.querySelector('#status').textContent = '';
 clone.querySelector('#autosave').setAttribute('aria-pressed', 'false');
 clone.querySelector('#save-state').textContent = 'Auto-save off · HTML not connected';
 clone.querySelector('#restore-recovery').hidden = true;
 clone.querySelector('body').classList.remove('searching', 'nav-open', 'nav-closed');
 clone.querySelector('#scrim').hidden = true;
 return {html: '<!DOCTYPE html>\n' + clone.outerHTML, captureError};
}
const initialState = JSON.parse($('#suite-state').textContent);
const recoveryKey = 'study-suite-recovery:' + initialState.baseline.course_id + ':' + location.pathname;
function saveRecovery() {
 try {
   const {state, captureError} = collectEdits();
   if (captureError) throw new Error(captureError);
   if (Object.keys(state.edits).length || Object.keys(initialState.edits).length) {
     localStorage.setItem(recoveryKey, JSON.stringify({baseline:state.baseline, edits:state.edits, time:Date.now()}));
   } else localStorage.removeItem(recoveryKey);
   if (!autoEnabled && dirty) $('#save-state').textContent = 'Browser recovery stored · HTML still needs saving';
 } catch {
   if (!autoEnabled) $('#save-state').textContent = 'Recovery unavailable · use Save Progress to keep edits';
 }
}
function restoreText(element, text) {
 if (element.matches('.equation-render')) { element.dataset.raw = text; renderMath(element); return; }
 text = text.replace(/\r\n?/g, '\n');
 const fragment = document.createDocumentFragment();
 function appendLiteral(parent, value) {
   value.split('\n').forEach((line, index) => {
     if (index) parent.append(document.createElement('br'));
     parent.append(document.createTextNode(line));
   });
 }
 function appendText(parent, value) {
   const pattern = /\\\(([\s\S]*?)\\\)|\*\*([^*\n]+)\*\*/g;
   let end = 0;
   for (const match of value.matchAll(pattern)) {
     appendLiteral(parent, value.slice(end, match.index));
     if (match[2] !== undefined) {
       const strong = document.createElement('strong'); strong.textContent = match[2];
       parent.append(strong); end = match.index + match[0].length; continue;
     }
     const unit = document.createElement('span'); unit.className = 'math-unit inline-math'; unit.contentEditable = 'false';
     const equation = document.createElement('span'); equation.className = 'equation-render'; equation.dataset.raw = match[1]; equation.dataset.display = 'inline';
     const button = document.createElement('button'); button.className = 'edit-formula'; button.textContent = 'Edit'; button.setAttribute('aria-label', 'Edit inline formula');
     unit.append(equation, button); parent.append(unit); end = match.index + match[0].length;
   }
   appendLiteral(parent, value.slice(end));
 }
 if (element.tagName === 'DIV' && (element.classList.contains('explanation-body') || (element.classList.contains('editable-text') && text.includes('\n\n')))) {
   text.split(/\n\n+/).forEach(value => {
     const lines = value.split('\n');
     if (lines.length && lines.every(line => line.startsWith('- '))) {
       const list = document.createElement('ul');
       lines.forEach(line => { const item = document.createElement('li'); appendText(item, line.slice(2)); list.append(item); });
       fragment.append(list);
     } else { const p = document.createElement('p'); appendText(p, value); fragment.append(p); }
   });
 } else appendText(fragment, text);
 element.replaceChildren(fragment);
 element.querySelectorAll('.equation-render').forEach(renderMath);
 syncHeading(element);
}
try {
 const recovery = JSON.parse(localStorage.getItem(recoveryKey));
 if (recovery && JSON.stringify(recovery.baseline) === JSON.stringify(initialState.baseline) &&
     recovery.edits && JSON.stringify(recovery.edits) !== JSON.stringify(initialState.edits)) {
   const fields = new Map($$('[data-field]').map(element => [element.dataset.field, element]));
   if (Object.entries(recovery.edits).every(([pointer, value]) => fields.has(pointer) && typeof value === 'string')) {
     $('#restore-recovery').hidden = false;
     $('#restore-recovery').onclick = () => {
       // Reset to baseline first: a recovered undo must also remove older saved edits.
       fields.forEach((element, pointer) => restoreText(element, pointer.split('/').reduce((value, key) => value[key], initialState.baseline)));
       Object.entries(recovery.edits).forEach(([pointer, value]) => restoreText(fields.get(pointer), value));
       $('#restore-recovery').hidden = true; markDirty(); status('Browser recovery restored. Save it to your HTML or enable Auto-save.');
     };
   }
 }
} catch { /* Storage can be unavailable or contain an invalid recovery record. */ }
function scheduleAutoSave() {
 clearTimeout(autoTimer);
 if (autoEnabled) autoTimer = setTimeout(() => { writeFile(fileHandle, true).catch(() => {}); }, 700);
}
function setAutoSave(enabled) {
 autoEnabled = enabled;
 $('#autosave').setAttribute('aria-pressed', String(enabled));
 if (!enabled) clearTimeout(autoTimer);
}
function writeFile(handle, automatic = false) {
 const task = writeQueue.then(async () => {
   if (automatic && !autoEnabled) return;
   const version = editVersion;
   const {html, captureError} = exportHTML();
   $('#save-state').textContent = 'Writing HTML…';
   let writable;
   try {
     writable = await handle.createWritable(); await writable.write(html); await writable.close();
   } catch (error) {
     try { await writable?.abort(); } catch { /* Preserve the original write failure. */ }
     const connected = autoEnabled;
     setAutoSave(false);
     saveRecovery();
     $('#save-state').textContent = (connected || automatic ? 'Auto-save paused' : 'File save failed') + ' · edits remain in this tab';
     if (connected || automatic) status('File save failed. Auto-save paused. Reconnect Auto-save or use Save Progress to export.');
     throw error;
   }
   if (version === editVersion) {
     dirty = false; clearTimeout(recoveryTimer);
     try { localStorage.removeItem(recoveryKey); } catch { /* Disk write is already confirmed. */ }
     $('#save-state').textContent = (autoEnabled ? 'Auto-save on · saved ' : 'HTML saved ') + new Date().toLocaleTimeString();
   } else {
     // markDirty already scheduled the newer revision, possibly queued behind
     // this write. Do not restart its typing delay or enqueue a duplicate.
     dirty = true;
     $('#save-state').textContent = autoEnabled ? 'Newer edits waiting to auto-save…' : 'Newer edits unsaved · save again';
   }
   const warning = captureError ? ' Weekly-update snapshot needs manual reconciliation; your visible edits are in this HTML.' : '';
   // Routine automatic writes stay quiet so feedback does not cover reading text.
   if (!automatic || warning) {
     const message = version === editVersion ? (automatic ? 'Auto-saved to your selected file.' : 'Saved to your selected file.') :
       'An earlier version was saved. ' + (autoEnabled ? 'Newer edits are waiting to auto-save.' : 'Newer edits still need saving.');
     status(message + warning);
   }
 });
 writeQueue = task.catch(() => {});
 return task;
}
function pickFile() {
 const filename = (document.title.replace(/[^a-z0-9 _-]/gi, '').trim() || 'Study Suite') + '.html';
 return window.showSaveFilePicker({suggestedName:filename,types:[{description:'Study Suite HTML',accept:{'text/html':['.html']}}]});
}
$('#autosave').onclick = async () => {
 if (autoEnabled) { setAutoSave(false); $('#save-state').textContent = dirty ? 'Auto-save off · unsaved changes' : 'Auto-save off · last write kept'; return; }
 if (!window.showSaveFilePicker) {
   saveRecovery(); status('This browser cannot write directly to HTML. Browser recovery is automatic; use Save Progress to download your edited HTML.'); return;
 }
 try { fileHandle = await pickFile(); }
 catch (error) {
   status(error.name === 'AbortError' ? 'Auto-save setup cancelled. Your edits remain in this tab.' : 'Could not connect Auto-save. Use Save Progress or try connecting again.');
   return;
 }
 setAutoSave(true);
 try { await writeFile(fileHandle, true); status('Auto-save on. Changes will save after a short typing pause.'); }
 catch { /* The write path reports the failure and preserves recovery. */ }
};
$('#save').onclick = async () => {
 document.activeElement?.blur();
 if (autoEnabled) { clearTimeout(autoTimer); try { await writeFile(fileHandle); } catch { /* Already reported; keep recovery. */ } return; }
 const filename = (document.title.replace(/[^a-z0-9 _-]/gi, '').trim() || 'Study Suite') + '.html';
 if (window.showSaveFilePicker) {
   try {
     const handle = await pickFile();
     await writeFile(handle); return;
   } catch (error) {
     if (error.name === 'AbortError') { status('Save cancelled. Your edits remain in this tab.'); return; }
   }
 }
 try {
   // The picker/write may have yielded while the user continued editing.
   const {html, captureError} = exportHTML();
   const warning = captureError ? ' Weekly-update snapshot needs manual reconciliation; your visible edits are in this HTML.' : '';
   const url = URL.createObjectURL(new Blob([html], {type:'text/html;charset=utf-8'}));
   const a = document.createElement('a'); a.href = url; a.download = filename; document.body.append(a); a.click(); a.remove();
   setTimeout(() => URL.revokeObjectURL(url), 60000);
   // Browsers do not expose download completion. Keep dirty state until a confirmed write.
   $('#save-state').textContent = 'Download requested · confirm the HTML in Downloads';
   status('Download requested. Confirm the HTML is in Downloads before closing this tab.' + warning);
 } catch { status('Export failed. Keep this tab open and try again.'); }
};
window.addEventListener('beforeunload', event => { if (dirty) { saveRecovery(); event.preventDefault(); event.returnValue = ''; } });
mode(document.body.dataset.mode === 'review' && !$('#review').hidden ? 'review' : 'learn');
if ($$('.equation-render').length) {
 window.MathJax = {loader:{load:['ui/safe']},tex:{inlineMath:[['\\(','\\)']],displayMath:[['\\[','\\]']]},startup:{typeset:false,ready:() => { MathJax.startup.defaultReady(); MathJax.startup.promise.then(() => $$('.equation-render').forEach(renderMath)); }}};
 const script = document.createElement('script'); script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js'; script.async = true; script.dataset.mathLoader = 'true';
 script.onerror = () => { $$('.equation-render').forEach(e => { e.textContent = e.dataset.raw; }); status('Math renderer unavailable. Editable LaTeX is shown; reading and saving still work.'); };
 document.head.append(script);
}
})();
