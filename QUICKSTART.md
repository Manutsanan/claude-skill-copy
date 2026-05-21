# Quickstart

30 วินาทีจาก clone → ใช้งานจริง

```bash
# 1. Clone
git clone https://github.com/Manutsanan/claude-skill-copy.git ~/Project/claude-skill-copy

# 2. Bootstrap (idempotent — safe to re-run)
cd ~/Project/claude-skill-copy
./scripts/setup.sh

# 3. Verify
ls -la ~/.claude/skills/        # ควรเห็น symlinks 7 ตัว → repo
```

เปิด Claude Code ใน project ใดก็ได้ ลอง:

```
ใช้ skill debug ตรวจอะไรก่อนเริ่ม
```

ต้องเห็น Claude **ท่อง mantra 4 ข้อ verbatim** ก่อนทำอะไร

---

## ทดลองทุก skill (1 บรรทัดต่อ skill)

```
/sa วิเคราะห์ requirement หน้า login
/ux ทำหน้านี้ให้ responsive + ทันสมัย
/fe เขียน composable useCounter() ที่ persist localStorage
/debug หน้านี้กระพริบตอน reload — หา root cause
/migrate native <select> เป็น USelect ทั้งโปรเจกต์
/audit project นี้ — perf + dead code + dependency
```

---

## สิ่งที่ต้องรู้ 3 ข้อ

1. **Memory เริ่มเปล่า** — เป็นเรื่องปกติ จะสะสมเองตามการใช้งาน
2. **Skill auto-trigger** — ไม่ต้องเรียก `/skill-name` เอง พิมพ์ภาษาไทยปกติ Claude detect intent
3. **ใส่ CLAUDE.md ใน project ของคุณ** — บอก stack + convention เพื่อให้ skill เลือก default ถูก (ดู README.md section "Per-project CLAUDE.md")

---

ต้องการละเอียดกว่านี้ → [README.md](README.md)
