# -*- coding: utf-8 -*-
"""results/ 폴더에 (1) 추천 빈도표 freq.csv, (2) 그림 fig1_overlap.png 를 만든다. analyze.py 와 같은 규칙·같은 data.csv 를 쓴다.
실행: python3 -I scripts/make_figures.py   (package 폴더 안에서)"""
import csv, os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = A.ROOT
for p in ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',):
    if os.path.exists(p): font_manager.fontManager.addfont(p); plt.rcParams['font.family'] = font_manager.FontProperties(fname=p).get_name()
plt.rcParams['axes.unicode_minus'] = False

# ---- 추천 빈도: 응답 10개 중 몇 개 응답이 그 원두 묶음을 포함했는가 (설명용 집계; 판정에는 쓰지 않음)
GROUPS = [
 ('에티오피아 예가체프', lambda r: '에티오피아' in r['c'] and '예가체프' in r['g']),
 ('에티오피아 구지·시다모', lambda r: '에티오피아' in r['c'] and bool(r['g'] & {'구지','시다모'})),
 ('케냐', lambda r: '케냐' in r['c']),
 ('파나마 게이샤', lambda r: '파나마' in r['c'] and '게이샤' in r['v']),
 ('르완다·부룬디', lambda r: bool(r['c'] & {'르완다','부룬디'})),
 ('에티오피아 게이샤 계열', lambda r: '에티오피아' in r['c'] and ('게이샤' in r['v'] or '게이샤 빌리지' in r['g'])),
 ('콜롬비아', lambda r: '콜롬비아' in r['c']),
]
resp, sent = A.load()
rows = []
for name, f in GROUPS:
    row = [name]
    for s in 'ABC':
        ids = [n for n in sorted(resp) if sent[n] == s]
        row.append(sum(1 for n in ids if any(f(r) for r in resp[n])))
    rows.append(row)
os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
with open(os.path.join(ROOT, 'results', 'freq.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
    w = csv.writer(fh); w.writerow(['원두 묶음', 'A 10개 응답 중', 'B 10개 응답 중', 'C 10개 응답 중']); w.writerows(rows)
print('추천 빈도(응답 10개 중 몇 개에 들어 있는가)'); [print(' ', r) for r in rows]

# ---- 그림 1: 같은 문장끼리(기준선) vs 문장이 다를 때
base, cross, out = A.run(resp, sent, A.same_main)
labels = ['A-B', 'A-C', 'B-C']
b = [out[p.replace('-', '')]['baseline'] for p in labels]
x = [out[p.replace('-', '')]['cross'] for p in labels]
BLUE, ORANGE = '#2a78d6', '#eb6834'; INK, MUTED = '#0b0b0b', '#52514e'
fig, ax = plt.subplots(figsize=(6.4, 3.8), dpi=200)
xs = range(3); w = 0.34
b1 = ax.bar([i - w/2 - 0.01 for i in xs], b, w, color=ORANGE, label='같은 문장끼리(기준선)')
b2 = ax.bar([i + w/2 + 0.01 for i in xs], x, w, color=BLUE, label='문장이 다른 응답끼리')
for bars in (b1, b2):
    for r in bars: ax.text(r.get_x() + r.get_width()/2, r.get_height() + 0.06, f'{r.get_height():.2f}', ha='center', va='bottom', fontsize=8.5, color=INK)
ax.set_xticks(list(xs)); ax.set_xticklabels(labels, color=INK)
ax.set_ylim(0, 5); ax.set_yticks(range(6)); ax.set_ylabel('같은 원두 개수의 평균 (최대 5)', color=MUTED, fontsize=9)
ax.tick_params(colors=MUTED, length=0)
for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color('#cfcfcc'); ax.yaxis.grid(True, color='#e6e6e3', lw=0.8); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=8.5, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2)
ax.set_title('문장을 바꿔도 같은 원두 개수는 거의 그대로였다', loc='left', fontsize=11, color=INK, pad=10)
fig.tight_layout(); fig.savefig(os.path.join(ROOT, 'results', 'fig1_overlap.png'), facecolor='#fcfcfb')
print('그림 저장: results/fig1_overlap.png')
