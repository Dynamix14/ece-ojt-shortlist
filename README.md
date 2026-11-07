# ECE OJT shortlist (v2)

Seven face-to-face OJT companies from the Mapúa masterlist that explicitly list **ECE**, ranked by driving
distance from Taft, Malate — with the internship allowance each one actually pays, traced to a posting,
a review, or marked *not published*.

**Live:** https://dynamix14.github.io/ece-ojt-shortlist/

## Allowance summary

| Company | Allowance | Distance | Basis |
|---|---|---|---|
| APMC | not published | 4.7 km | no allowance in the MOA listing, no intern mentions pay |
| Security Bank | ₱9,000–10,000 / mo | 4.7 km | Prosple salary field on STAR postings (IE cohort, Feb 2026); Cebu cohort ₱5,000–7,000 |
| Edgepoint Towers | not published | 4.9 km | "pay information not provided" on their intern listing |
| Meinhardt PH | not published | 5.1 km | nothing anywhere; consultancy OJT in PH is usually unpaid |
| Coca-Cola EP Aboitiz | ₱17,000–20,000 / mo | 8.8 km | Indeed salary on their Santa Rosa plant IE intern |
| Meralco Power Academy | low, figure not published | 13.8 km | Prosple intern review — "a bit low considering the commute" |
| Lattice Semiconductor | "competitive stipend", no figure | 19.7 km | Prosple; full-time EE roles post ₱30–40k/mo |

Benchmark: Indeed lists the Philippine engineering intern at ₱15,307/mo average (₱18,255 Manila, n=3).
Small sample — a sniff test, not a rate card.

## Structure

- `data.json` — the seven companies: distance, roles, allowance + basis, intern reviews, contacts.
- `build.py` — renders `index.html` from `data.json` (no dependencies).
- `index.html` — the built site.

```bash
python3 build.py        # rebuild
python3 -m http.server  # preview at localhost:8000
```

## Method notes

- Distances: OSRM driving route from DLSU–Taft (14.5649, 120.9931), traffic-free. Add 40–100% at rush hour.
- Allowance figures come from the posting itself (Prosple salary field, Indeed salary line), not from estimates.
- Intern reality quotes Indeed / JobStreet intern reviews; "no first-hand account" means exactly that.
- Allowances vary by cohort and business unit — a 2025 posting is not a promise for 2027.
