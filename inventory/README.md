# MX17 hardware inventory

Started 2026-11-19. **One list of the physical hardware that exists**, for every facility study: what it is, who owns it,
where it is, its condition and whether a run may take it (ours / lent on request / returned, ask again / stays at its
facility). `inventory.py` is the source; `python3 inventory/inventory.py` writes `out/inventory.json` and the readable
table [`INVENTORY.md`](INVENTORY.md).

How it fits with the rest:
- **`budget/items.py`** prices what we *don't* have (buy or borrow options). Each asset's `budget` field names the
  items.py item that prices its replacement or the missing part.
- **A study's plan** keeps the run-specific part: what that run needs, by when, whom we ask. `lnl_x17/planning/plan.py`
  `HARDWARE` items carry `inv=[ids]`; its build reads this file and shows owner, location and condition on the LNL page's
  Hardware tab. New studies should do the same instead of copying facts.

Many locations and some owners are **(ask)**: fill them in as they are learnt (date the note). Never reuse an id.
