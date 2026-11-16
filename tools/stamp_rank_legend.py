#!/usr/bin/env python3
"""Rank wording pass (Michael, Nov 16): put 'Rank: 1 = MOST Conservative.' once under each rank section heading
(Profile Rank history, Band history, Issue areas; session and official Rank tiles) and replace 'Moved up N places overall'
with 'Overall rank moved up N' on every officials page, including the hand-built 2025 session and 2026 pages.
tools/gen.py and tools/stamp_rank_chart.py apply the same functions (tools/rank_chart.py), so rebuilds match. Idempotent.

    python3 -B tools/stamp_rank_legend.py [SITE_ROOT]
"""
import os, sys, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
sys.path.insert(0, HERE)
import rank_chart
n = 0
for f in sorted(glob.glob(f'{ROOT}/officials/*.html') + glob.glob(f'{ROOT}/officials/20*/*.html')):
    t = open(f, encoding='utf-8').read(); u = rank_chart.add_legend(rank_chart.rank_wording(t))
    if u != t: open(f, 'w', encoding='utf-8').write(u); n += 1
print('changed files', n)
