/**
 * MX17 comment backend, shared by two site pages:
 *   page "budget"   (default) facilities/budget.html          → tab "Comments"
 *   page "detector"           notes/mx17-detector-spec.html   → tab "Detector"
 *       (source: nTof_x17/docs/detector_spec/)
 *
 * Bound to the Google Sheet "MX17 run budget — collaborator feedback (v2)". Each comment becomes one row of its
 * page's tab (created on first use). The pages POST new comments and GET the list to show them. A request with no
 * `page` is the budget page, so the budget page needs no change.
 *
 * Deploy once (see budget/README.md, "Comments backend"):
 *   Extensions → Apps Script → paste this file → Deploy → New deployment → Web app,
 *   Execute as: Me, Who has access: Anyone → copy the /exec URL into FEEDBACK_ENDPOINT in budget/items.py.
 * After editing: Deploy → Manage deployments → edit → Version: New version, so the URL stays the same.
 *
 * To hide a comment, delete its row. To mark one handled, write anything in its "status" column (e.g. "done");
 * the page then shows it greyed out.
 */
const PAGES = {
  budget:   { sheet: 'Comments', kinds: ['general', 'item', 'new'],
              head: ['time', 'kind', 'item_id', 'item', 'subsystem', 'name', 'comment', 'price_eur', 'source', 'status', 'id'] },
  detector: { sheet: 'Detector', kinds: ['general', 'item', 'question', 'new'],
              head: ['time', 'kind', 'item_id', 'item', 'section', 'name', 'comment', 'value', 'source', 'status', 'id'] },
};

function page_(p) { return PAGES[p] ? p : 'budget'; }

function sheet_(page) {
  const P = PAGES[page];
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(P.sheet);
  if (!sh) {
    sh = ss.insertSheet(P.sheet, page === 'budget' ? 0 : ss.getNumSheets());
    sh.appendRow(P.head);
    sh.setFrozenRows(1);
  }
  return sh;
}

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

// text only: never let a comment become a formula
function clip_(s, n) {
  let t = String(s == null ? '' : s).slice(0, n).trim();
  if (/^[=+\-@]/.test(t)) t = "'" + t;
  return t;
}

function doGet(e) {
  const page = page_(e && e.parameter && e.parameter.page);
  const v = sheet_(page).getDataRange().getValues();
  const h = v.shift();
  const comments = v.filter(r => r[0] !== '').map(r =>
    Object.fromEntries(h.map((k, i) => [k, r[i] instanceof Date ? r[i].toISOString() : String(r[i])])));
  return out_({ ok: true, page, comments });
}

function doPost(e) {
  let d;
  try { d = JSON.parse(e.postData.contents); } catch (x) { return out_({ ok: false, error: 'bad request' }); }
  if (d.website) return out_({ ok: true });                       // honeypot field: bots fill it, people don't
  const page = page_(d.page);
  const P = PAGES[page];
  const kind = P.kinds.indexOf(d.kind) >= 0 ? d.kind : 'general';
  const text = clip_(d.comment, 4000);
  const name = clip_(d.name, 80);
  if (!text || !name) return out_({ ok: false, error: 'name and comment are required' });
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const id = Utilities.getUuid().slice(0, 8);
    const row = page === 'budget'
      ? [new Date(), kind, clip_(d.item_id, 40), clip_(d.item, 200), clip_(d.subsystem, 80), name,
         text, clip_(d.price, 40), clip_(d.source, 300), '', id]
      : [new Date(), kind, clip_(d.item_id, 40), clip_(d.item, 200), clip_(d.section, 80), name,
         text, clip_(d.value, 200), clip_(d.source, 300), '', id];
    sheet_(page).appendRow(row);
    return out_({ ok: true, page, id });
  } finally {
    lock.releaseLock();
  }
}
