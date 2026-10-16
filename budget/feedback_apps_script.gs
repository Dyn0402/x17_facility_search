/**
 * MX17 run budget: comment backend for facilities/budget.html.
 *
 * Bound to the Google Sheet "MX17 run budget — collaborator feedback (v2)". Each comment becomes one row of the
 * "Comments" tab (created on first use). The page POSTs new comments and GETs the list to show them.
 *
 * Deploy once (see budget/README.md, "Comments backend"):
 *   Extensions → Apps Script → paste this file → Deploy → New deployment → Web app,
 *   Execute as: Me, Who has access: Anyone → copy the /exec URL into FEEDBACK_ENDPOINT in budget/items.py.
 *
 * To hide a comment, delete its row. To mark one handled, write anything in its "status" column (e.g. "done");
 * the page then shows it greyed out.
 */
const SHEET = 'Comments';
const HEAD = ['time', 'kind', 'item_id', 'item', 'subsystem', 'name', 'comment', 'price_eur', 'source', 'status', 'id'];

function sheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET);
  if (!sh) {
    sh = ss.insertSheet(SHEET, 0);
    sh.appendRow(HEAD);
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

function doGet() {
  const v = sheet_().getDataRange().getValues();
  const h = v.shift();
  const comments = v.filter(r => r[0] !== '').map(r =>
    Object.fromEntries(h.map((k, i) => [k, r[i] instanceof Date ? r[i].toISOString() : String(r[i])])));
  return out_({ ok: true, comments });
}

function doPost(e) {
  let d;
  try { d = JSON.parse(e.postData.contents); } catch (x) { return out_({ ok: false, error: 'bad request' }); }
  if (d.website) return out_({ ok: true });                       // honeypot field: bots fill it, people don't
  const kind = ['general', 'item', 'new'].indexOf(d.kind) >= 0 ? d.kind : 'general';
  const text = clip_(d.comment, 4000);
  const name = clip_(d.name, 80);
  if (!text || !name) return out_({ ok: false, error: 'name and comment are required' });
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const id = Utilities.getUuid().slice(0, 8);
    sheet_().appendRow([new Date(), kind, clip_(d.item_id, 40), clip_(d.item, 200), clip_(d.subsystem, 80), name,
                        text, clip_(d.price, 40), clip_(d.source, 300), '', id]);
    return out_({ ok: true, id });
  } finally {
    lock.releaseLock();
  }
}
