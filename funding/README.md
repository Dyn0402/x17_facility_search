# funding/

External funding for the X17 search, using the feasibility studies in this repo.

**Live page:** <https://dylan-neff.web.cern.ch/facilities/funding.html> (unlisted): overview with Dylan's checks (the LNL start
date moves them) and the deadlines of the next eight months, a filterable scheme table (click a row for the deep dive: money,
rules, process, odds, effort, next step), a deadline timeline, a Money tab (salary options, size of each scheme), people, and a
to-find-out checklist.

**Read this first (2026-10-27):** [`OPTIONS.md`](OPTIONS.md) §1 and §6–§8. 30 schemes, from the call texts where published.
- **Act now:** the INFN fellowship for non-Italians (bando 29217) closes **12 Nov 2026** (letters 15 Nov). Dylan qualifies until he
  signs the incarico; €36 k gross a year for 2 years at LNL, against €28.8 k for 1 year.
- **Dylan's grants:** STARS@UNIPD Starting Grant (€175 k + PI salary, 30 months; a 2027 edition likely Dec–Mar, check), then the
  ERC StG 2028 (~Oct 2027; 8.8 % success in 2026), with MSCA PF 2027 (8 Sep 2027) for salary.
- **Apparatus:** INFN CSN3, PRIN 2027 (~Apr–Jun 2027) and Fondazione Cariparo's excellence call, with Pierfrancesco as PI.
  Travel: MSCA Staff Exchanges (15 Apr 2027). US: a US PI via the DOE open call or NSF 26-523 (both any time); Templeton 2027.

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
