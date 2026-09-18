#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""جست‌وجو در کتابخانهٔ سوابق شرعی شورای نگهبان (precedents.jsonl / .gz)
کاربرد:  python3 find_precedent.py "ربا" "تأخیر"            # همهٔ واژه‌ها باید باشند (AND)
         python3 find_precedent.py --hukm "خلاف شرع" "عدم النفع"
         python3 find_precedent.py --mozu "ربا و بانک" --limit 50 ""
         python3 find_precedent.py --regex "عدم\s*النفع|تفویت منفعت"
خروجی: شناسه، تاریخ نامه، شمارهٔ نامه، نوع، عنوان مصوبه، محل، حکم، عنوان فقهی، عین عبارت."""
import argparse, gzip, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
def load(path=None):
    for p in ([path] if path else []) + [os.path.join(HERE, "precedents.jsonl"), os.path.join(HERE, "precedents.jsonl.gz")]:
        if p and os.path.exists(p):
            op = gzip.open if p.endswith(".gz") else open
            with op(p, "rt", encoding="utf-8") as f:
                return [json.loads(l) for l in f if l.strip()]
    sys.exit("precedents.jsonl یافت نشد")
def norm(s):
    return (s or "").replace("ي", "ی").replace("ك", "ک").replace("‌", " ").replace("‌", " ")
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words", nargs="*")
    ap.add_argument("--regex"); ap.add_argument("--hukm"); ap.add_argument("--mozu"); ap.add_argument("--category")
    ap.add_argument("--limit", type=int, default=30); ap.add_argument("--full", action="store_true", help="متن کامل واحد")
    ap.add_argument("--file")
    a = ap.parse_args()
    rows = load(a.file)
    out = []
    for r in rows:
        if a.hukm and r["hukm"] != a.hukm: continue
        if a.mozu and r["mozu"] != a.mozu: continue
        if a.category and a.category not in r["category"]: continue
        hay = norm(" ".join([r["onvan_feqhi"], r["mekanism"], r["ebarat"], r["text"], r["title"], " ".join(r.get("kelidvaje") or [])]))
        if a.regex and not re.search(a.regex, hay): continue
        if any(norm(w) not in hay for w in a.words if w): continue
        out.append(r)
    out.sort(key=lambda r: r["letter_date"] or "", reverse=True)
    print(f"{len(out)} سابقه")
    for r in out[:a.limit]:
        print(f"\n■ {r['unitId']} | {r['letter_date']} | شمارهٔ نامه: {r['letter_no'] or '—'} | {r['letter_type']} | {r['category']}")
        print(f"  مصوبه: {r['title'][:100]} | محل: {r['mahal']}")
        print(f"  حکم: {r['hukm']} | عنوان فقهی: {r['onvan_feqhi']} | شاخه: {r['mozu']}")
        print(f"  سازوکار: {r['mekanism']}")
        print(f"  عین عبارت: «{r['ebarat']}»" if r['ebarat'] else "")
        if a.full: print("  متن: " + r["text"].replace("\n", " ⏎ ")[:1500])
if __name__ == "__main__":
    main()
