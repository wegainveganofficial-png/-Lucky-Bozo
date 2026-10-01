"""สร้าง index.html ใหม่จาก thai-lotto-archive (ข้อมูลสำรองที่ฝังในหน้า)
ใช้: git clone https://github.com/vicha-w/thai-lotto-archive && python3 scripts/build.py ../thai-lotto-archive/lottonumbers
"""
import os, sys, json, datetime
src = sys.argv[1]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ---- แก้ข้อมูลต้นทางที่ตรวจพบว่าผิด (ตรวจเทียบกับเว็บข่าวสลากแล้ว) ----
# 1) ข้างเคียงรางวัลที่ 1 คือเลขรางวัลที่ 1 บวก/ลบ 1 เสมอ จึงคำนวณใหม่ทุกงวด (ไฟล์ต้นทางปี 2550 เพี้ยน 5 งวด)
# 2) งวด 16 ม.ค. 2569 ออกจริงวันที่ 17 ม.ค. 2569 และไฟล์ต้นทางมีรางวัลที่ 2-5 เสีย
#    เก็บเฉพาะรางวัลที่ตรวจแล้ว (รางวัลที่ 1, 3 ตัวหน้า/ท้าย, 2 ตัว, ข้างเคียง) ส่วนรางวัลที่ 2-5 เว้นว่างไว้
DATE_FIX = {"2026-01-16": "2026-01-17"}
CLEAR_LOWER_PRIZES = {"2026-01-17"}
out = []
for f in sorted(os.listdir(src)):
    d = datetime.date.fromisoformat(f[:-4]); r = {}
    for l in open(os.path.join(src, f), encoding="utf-8").read().splitlines()[1:]:
        p = l.split()
        if p: r[p[0]] = p[1:]
    d_str = DATE_FIX.get(f[:-4], f[:-4]); d = datetime.date.fromisoformat(d_str)
    first = r["FIRST"][0]
    near = ["%06d" % (int(first) - 1), "%06d" % ((int(first) + 1) % 1000000)]
    s = "%d-1" % (d.month % 12 + 1) if d.day >= 26 else "%d-1" % d.month if d.day <= 8 else "%d-16" % d.month
    low = d_str in CLEAR_LOWER_PRIZES
    out.append({"d": d_str, "s": s, "f": first, "n": near, "t": r.get("TWO", [""])[0],
                "tf": r.get("THREE_FIRST", []), "tl": r.get("THREE_LAST", r.get("THREE", [])),
                "p2": [] if low else r.get("SECOND", []), "p3": [] if low else r.get("THIRD", []),
                "p4": [] if low else r.get("FOURTH", []), "p5": [] if low else r.get("FIFTH", [])})
out.sort(key=lambda x: x["d"])

# ---- ตรวจความสอดคล้องของข้อมูลทุกงวด ----
problems = []
for o in out:
    new_fmt = o["d"] >= "2015-09-01"
    chk = lambda ok, m: ok or problems.append((o["d"], m))
    chk(len(o["f"]) == 6 and o["f"].isdigit(), "รางวัลที่ 1")
    chk(len(o["t"]) == 2 and o["t"].isdigit(), "2 ตัวท้าย")
    chk((len(o["tf"]) == 2 and len(o["tl"]) == 2) if new_fmt else (len(o["tl"]) == 4 and not o["tf"]), "จำนวนเลข 3 ตัว")
    chk(all(len(x) == 3 and x.isdigit() for x in o["tf"] + o["tl"]), "รูปแบบเลข 3 ตัว")
    if o["p2"] or o["p3"] or o["p4"] or o["p5"]:
        chk([len(o[k]) for k in ("p2", "p3", "p4", "p5")] == [5, 10, 50, 100], "จำนวนรางวัลที่ 2-5")
        chk(all(len(x) == 6 and x.isdigit() for k in ("p2", "p3", "p4", "p5") for x in o[k]), "รูปแบบเลขรางวัลที่ 2-5")
print("ตรวจ %d งวด พบปัญหา %d รายการ" % (len(out), len(problems)))
for x in problems: print("  ", x)

# ---- สร้าง SQL สำหรับ Supabase ----
def arr(a): return "ARRAY[%s]::text[]" % ",".join("'%s'" % x for x in a) if a else "'{}'::text[]"
vals = ",\n".join("('%s','%s','%s',%s,'%s',%s,%s,%s,%s,%s,%s)" % (o["d"], o["s"], o["f"], arr(o["n"]), o["t"], arr(o["tf"]), arr(o["tl"]), arr(o["p2"]), arr(o["p3"]), arr(o["p4"]), arr(o["p5"])) for o in out)
schema_path = os.path.join(root, "supabase", "schema.sql")
if os.path.exists(schema_path):
    sql = open(schema_path, encoding="utf-8").read() + "\n-- เติมผลรางวัล (รันซ้ำได้ ข้อมูลที่ถูกแก้จะถูกอัปเดตตาม)\ninsert into public.lotto_draws (draw_date,draw_slot,first_prize,near_first,two_digit,three_front,three_back,prize2,prize3,prize4,prize5) values\n" + vals + "\non conflict (draw_date) do update set draw_slot=excluded.draw_slot, first_prize=excluded.first_prize, near_first=excluded.near_first, two_digit=excluded.two_digit, three_front=excluded.three_front, three_back=excluded.three_back, prize2=excluded.prize2, prize3=excluded.prize3, prize4=excluded.prize4, prize5=excluded.prize5;\n-- งวดที่ไฟล์ต้นทางลงวันที่ผิด (16 ม.ค. 2569 ที่ถูกต้องคือ 17 ม.ค. 2569)\ndelete from public.lotto_draws where draw_date = '2026-01-16';\n"
    open(os.path.join(root, "supabase", "lotto_draws.sql"), "w", encoding="utf-8").write(sql)
tpl = open(os.path.join(root, "scripts", "index.template.html"), encoding="utf-8").read()
open(os.path.join(root, "index.html"), "w", encoding="utf-8").write(tpl.replace("__DATA__", json.dumps(out, separators=(",", ":"))))
print(len(out), "draws ->", out[-1]["d"])
