# -*- coding: utf-8 -*-
"""data.csv(150줄)에서 같은 원두 규칙(3단계_설계.md 4번)으로 응답 쌍의 겹침을 세고, 5번 규칙으로 판정한다.
실행: python3 -I scripts/analyze.py   (package 폴더 안에서)  ->  results/ 폴더에 표를 저장하고 화면에 요약을 출력한다."""
import csv, itertools, os, statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THRESHOLD = 0.5   # 데이터를 모으기 전에 정한 기준(설계 5번)

def vals(s): return {x.strip() for x in s.split('/') if x.strip()}

def load():
    resp = defaultdict(list); sent = {}
    for r in csv.DictReader(open(os.path.join(ROOT,'data.csv'), encoding='utf-8-sig')):
        n = int(r['요청번호']); sent[n] = r['문장']
        resp[n].append(dict(c=vals(r['생산국']), g=vals(r['세부 지역']), v=vals(r['품종']), p=vals(r['가공 방식']),
                            key=(r['생산국'].strip(), r['세부 지역'].strip(), r['품종'].strip(), r['가공 방식'].strip())))
    assert len(resp) == 30 and all(len(x) == 5 for x in resp.values())
    return resp, sent

def same_main(a, b):
    if bool(a['v']) != bool(b['v']): return False          # 설계 4번 5항: 한쪽에만 품종이 적혀 있으면 다른 원두
    for k in 'cgvp':
        if a[k] and b[k] and not (a[k] & b[k]): return False  # 두 쪽 모두 적힌 칸만 비교, 하나라도 겹치면 같음
    return True

def same_strict(a, b): return a['key'] == b['key']          # 보조: 정리한 이름이 완전히 같을 때만

def overlap(x, y, same):
    """일대일 짝짓기에서 가능한 가장 큰 짝 수"""
    match = {}
    def try_(i, seen):
        for j in range(len(y)):
            if same(x[i], y[j]) and j not in seen:
                seen.add(j)
                if j not in match or try_(match[j], seen):
                    match[j] = i; return True
        return False
    return sum(1 for i in range(len(x)) if try_(i, set()))

def run(resp, sent, same):
    ids = {s: [n for n in sorted(resp) if sent[n] == s] for s in 'ABC'}
    base = {s: [overlap(resp[a], resp[b], same) for a, b in itertools.combinations(ids[s], 2)] for s in 'ABC'}
    cross = {p: [overlap(resp[a], resp[b], same) for a in ids[p[0]] for b in ids[p[1]]] for p in ('AB','AC','BC')}
    out = {}
    for p in cross:
        b = (st.mean(base[p[0]]) + st.mean(base[p[1]])) / 2
        m = st.mean(cross[p]); d = b - m
        out[p] = dict(baseline=b, cross=m, diff=d, verdict='달라졌다' if d >= THRESHOLD else '비슷하다', n=len(cross[p]))
    return base, cross, out

def hist(xs): return {k: xs.count(k) for k in range(6)}

def main():
    resp, sent = load(); os.makedirs(os.path.join(ROOT,'results'), exist_ok=True)
    rows = []
    for name, fn in (('주 규칙', same_main), ('보조 규칙(이름이 완전히 같을 때만)', same_strict)):
        base, cross, out = run(resp, sent, fn)
        print(f'\n=== {name} ===')
        for s in 'ABC': print(f'같은 문장끼리({s}) 쌍 {len(base[s])}개: 평균 겹침 {st.mean(base[s]):.2f}  분포 {hist(base[s])}')
        for p, o in out.items():
            print(f'{p[0]}-{p[1]}: 쌍 {o["n"]}개, 표현 간 평균 {o["cross"]:.2f}, 기준선 {o["baseline"]:.2f}, 차이 {o["diff"]:+.2f} -> {o["verdict"]}   분포 {hist(cross[p])}')
            rows.append([name, f'{p[0]}-{p[1]}', o['n'], round(o['cross'],3), round(o['baseline'],3), round(o['diff'],3), o['verdict']])
        v = [o['verdict'] for o in out.values()]
        print('가설 판정:', '세 쌍 모두 비슷하다 -> 가설 지지' if all(x == '비슷하다' for x in v) else '달라진 쌍이 있다 -> ' + ', '.join(p for p, o in out.items() if o['verdict'] == '달라졌다'))
    with open(os.path.join(ROOT,'results','summary.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['규칙','비교','쌍 수','표현 간 평균 겹침','기준선(두 문장 평균)','기준선-표현 간','판정']); w.writerows(rows)

if __name__ == '__main__':
    main()
