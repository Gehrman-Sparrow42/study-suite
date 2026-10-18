/* Raw formula source and editable DOM are the document's persistent state. */
(() => {
'use strict';
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
let dirty = false, activeFormula = null, mathQueue = Promise.resolve(), statusTimer;
const status = text => {
 $('#status').textContent = text;
 clearTimeout(statusTimer);
 statusTimer = setTimeout(() => { $('#status').textContent = ''; }, 9000);
};
const markDirty = () => { dirty = true; status('Unsaved changes · use Save Progress to keep them.'); };
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
function search() {
 const query = $('#search').value.trim().toLowerCase();
 document.body.classList.toggle('searching', Boolean(query));
 let count = 0;
 $$('.section').forEach(section => {
   const headingMatch = [section.querySelector('.section-heading'), section.querySelector('.section-intro')].some(e => e.textContent.toLowerCase().includes(query));
   let found = false;
   section.querySelectorAll('.block').forEach(block => {
     const match = !query || headingMatch || block.textContent.toLowerCase().includes(query) || [...block.querySelectorAll('[data-raw]')].some(e => e.dataset.raw.toLowerCase().includes(query)) || [...block.querySelectorAll('img')].some(e => e.alt.toLowerCase().includes(query));
     block.hidden = !match;
     if (match) { found = true; count++; }
   });
   section.hidden = !found;
   // Search may reveal text inside a closed explanation without altering saved preference.
   section.querySelectorAll('details').forEach(detail => {
     if (query && !detail.hasAttribute('data-before-search')) detail.dataset.beforeSearch = String(detail.open);
     if (query) detail.open = true;
     else if (detail.hasAttribute('data-before-search')) { detail.open = detail.dataset.beforeSearch === 'true'; delete detail.dataset.beforeSearch; }
   });
 });
 $('#search-status').hidden = !query;
 $('#search-status').textContent = count ? `${count} matching reading blocks. Search includes expanded explanations.` : 'No matching concepts. Try another term.';
 requestAnimationFrame(scrollSpy);
}
$('#search').addEventListener('input', search);
$$('nav a').forEach(link => link.onclick = () => {
 $('#search').value = ''; search();
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
$$('.edit-formula').forEach(button => button.onclick = () => {
 activeFormula = button.closest('.math-unit').querySelector('.equation-render');
 $('#formula-source').value = activeFormula.dataset.raw;
 $('#formula-dialog').showModal(); $('#formula-source').focus();
});
$('#cancel-formula').onclick = () => $('#formula-dialog').close();
$('#apply-formula').onclick = () => {
 activeFormula.dataset.raw = $('#formula-source').value;
 renderMath(activeFormula); markDirty(); $('#formula-dialog').close();
};
$$('.figure-open').forEach(button => button.onclick = () => {
 const stage = $('#image-dialog .image-stage'); stage.replaceChildren(button.querySelector('img').cloneNode(true));
 stage.classList.remove('zoomed'); $('#zoom').textContent = 'Zoom in'; $('#image-dialog').showModal();
});
$('#close-image').onclick = () => $('#image-dialog').close();
$('#zoom').onclick = () => { const zoomed = $('.image-stage').classList.toggle('zoomed'); $('#zoom').textContent = zoomed ? 'Fit figure' : 'Zoom in'; };
function exportHTML() {
 const clone = document.documentElement.cloneNode(true);
 clone.querySelectorAll('.equation-render').forEach(element => { element.replaceChildren(); element.textContent = element.dataset.raw; });
 // Only MathJax-generated assets are replaceable. Never remove educational SVGs.
 clone.querySelectorAll('mjx-container, [id^="MJX-"], [id^="MathJax-"], .CtxtMenu_Menu, script[data-math-loader]').forEach(e => e.remove());
 clone.querySelectorAll('style:not(#suite-styles)').forEach(e => { if (e.textContent.includes('.CtxtMenu_')) e.remove(); });
 clone.querySelectorAll('script[src^="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/"]').forEach(e => e.remove());
 clone.querySelectorAll('[contenteditable]').forEach(e => { e.removeAttribute('autofocus'); });
 clone.querySelectorAll('[style]').forEach(e => { if (!e.getAttribute('style').trim()) e.removeAttribute('style'); });
 clone.querySelectorAll('.section,.block').forEach(e => e.removeAttribute('hidden'));
 clone.querySelectorAll('details[data-before-search]').forEach(e => { e.open = e.dataset.beforeSearch === 'true'; delete e.dataset.beforeSearch; });
 clone.querySelectorAll('dialog').forEach(e => e.removeAttribute('open'));
 clone.querySelector('.image-stage').replaceChildren();
 clone.querySelector('#formula-source').textContent = '';
 clone.querySelector('#search').setAttribute('value', '');
 clone.querySelector('#search-status').hidden = true;
 clone.querySelector('#status').textContent = '';
 clone.querySelector('body').classList.remove('searching', 'nav-open', 'nav-closed');
 clone.querySelector('#scrim').hidden = true;
 return '<!DOCTYPE html>\n' + clone.outerHTML;
}
$('#save').onclick = async () => {
 document.activeElement?.blur();
 const html = exportHTML();
 const filename = (document.title.replace(/[^a-z0-9 _-]/gi, '').trim() || 'Study Suite') + '.html';
 if (window.showSaveFilePicker) {
   try {
     const handle = await window.showSaveFilePicker({suggestedName:filename,types:[{description:'Study Suite HTML',accept:{'text/html':['.html']}}]});
     const writable = await handle.createWritable(); await writable.write(html); await writable.close();
     dirty = false; status('Saved to your selected file.'); return;
   } catch (error) {
     if (error.name === 'AbortError') { status('Save cancelled. Your edits remain in this tab.'); return; }
   }
 }
 try {
   const url = URL.createObjectURL(new Blob([html], {type:'text/html;charset=utf-8'}));
   const a = document.createElement('a'); a.href = url; a.download = filename; document.body.append(a); a.click(); a.remove();
   setTimeout(() => URL.revokeObjectURL(url), 60000);
   // Browsers do not expose download completion. Keep dirty state until a confirmed write.
   status('Download requested. Confirm the HTML is in Downloads before closing this tab.');
 } catch { status('Export failed. Keep this tab open and try again.'); }
};
window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
mode(document.body.dataset.mode === 'review' && !$('#review').hidden ? 'review' : 'learn');
if ($$('.equation-render').length) {
 window.MathJax = {loader:{load:['ui/safe']},tex:{inlineMath:[['\\(','\\)']],displayMath:[['\\[','\\]']]},startup:{typeset:false,ready:() => { MathJax.startup.defaultReady(); MathJax.startup.promise.then(() => $$('.equation-render').forEach(renderMath)); }}};
 const script = document.createElement('script'); script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js'; script.async = true; script.dataset.mathLoader = 'true';
 script.onerror = () => { $$('.equation-render').forEach(e => { e.textContent = e.dataset.raw; }); status('Math renderer unavailable. Editable LaTeX is shown; reading and saving still work.'); };
 document.head.append(script);
}
})();
