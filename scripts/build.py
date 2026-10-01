"""สร้าง index.html ใหม่จาก thai-lotto-archive (ข้อมูลสำรองที่ฝังในหน้า)
ใช้: git clone https://github.com/vicha-w/thai-lotto-archive && python3 scripts/build.py ../thai-lotto-archive/lottonumbers
"""
import os, sys, json, datetime
src = sys.argv[1]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = []
for f in sorted(os.listdir(src)):
    d = datetime.date.fromisoformat(f[:-4]); r = {}
    for l in open(os.path.join(src, f), encoding="utf-8").read().splitlines()[1:]:
        p = l.split()
        if p: r[p[0]] = p[1:]
    s = "%d-1" % (d.month % 12 + 1) if d.day >= 26 else "%d-1" % d.month if d.day <= 8 else "%d-16" % d.month
    out.append({"d": f[:-4], "s": s, "f": r["FIRST"][0], "n": r.get("NEAR_FIRST", []), "t": r.get("TWO", [""])[0],
                "tf": r.get("THREE_FIRST", []), "tl": r.get("THREE_LAST", r.get("THREE", [])),
                "p2": r.get("SECOND", []), "p3": r.get("THIRD", []), "p4": r.get("FOURTH", []), "p5": r.get("FIFTH", [])})
tpl = open(os.path.join(root, "scripts", "index.template.html"), encoding="utf-8").read()
open(os.path.join(root, "index.html"), "w", encoding="utf-8").write(tpl.replace("__DATA__", json.dumps(out, separators=(",", ":"))))
print(len(out), "draws ->", out[-1]["d"])
