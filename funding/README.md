# funding/

External funding for the X17 search, using the feasibility studies in this repo.

**Live page:** <https://dylan-neff.web.cern.ch/facilities/funding.html> (unlisted): overview with Dylan's checks (the LNL start
date moves them), a filterable scheme table with eligibility per person, a deadline timeline, people, and a to-find-out checklist.

**Read this first (2026-10-26):** [`OPTIONS.md`](OPTIONS.md). Dylan (US citizen; PhD Nov 2023; INFN-LNL incarico post-doc,
12 months renewable, from ~Dec 2026) is eligible for ERC and the MSCA European Fellowship. The ERC Starting Grant (2028 call,
~Oct 2027, or later) is the one sized for an experiment. MSCA PF 2027 (8 Sep 2027) is his only MSCA call for an Italian host. The incarico is not a researcher post, so
PRIN goes to Pierfrancesco (Dirigente di Ricerca) as PI, with INFN CSN3 for the hardware. US federal grants need a US employer:
the US routes are Templeton (2027), a US university PI, and Fulbright. Urgent: does the incarico exclude Dylan from the INFN
non-Italian fellowship (deadline ~15 Dec 2026)?

| file | what |
|---|---|
| `OPTIONS.md` | the schemes, who can apply, deadlines, sources |
| `schemes.py` | the data: schemes, eligibility per person, plan, to-do |
| `build_funding.py`, `funding_template.html` | → `out/funding.html` (standalone) and `out/funding_schemes.csv` |

Update: edit `schemes.py`, then

```bash
python3 funding/build_funding.py
cp funding/out/funding.html ~/PycharmProjects/dylan-cern-site/pages/facilities/funding.html
cd ~/PycharmProjects/dylan-cern-site && python3 scripts/build.py && rsync -t facilities/funding.html lxplus:/eos/user/d/dneff/www/facilities/
```
