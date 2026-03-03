# 🚀 Deploy OpenClaw Skills - Quick Guide

## ⚡ Quick Deploy (3 Steps)

### 1. Run Migration
```bash
cd Bismillah
python run_openclaw_skills_migration.py
```

**Expected:** ✅ 3 tables created, 10 skills loaded

### 2. Test System
```bash
python test_openclaw_skills.py
```

**Expected:** ✅ All 11 tests passed

### 3. Restart Bot
```bash
python bot.py
```

**Expected:** ✅ Skill handlers registered

---

## 🧪 Test in Telegram

```
/openclaw_start
/openclaw_skills
/openclaw_skill skill_crypto_analysis
/openclaw_install skill_crypto_analysis
/openclaw_myskills
```

---

## ✅ Success Indicators

- [ ] Migration completed without errors
- [ ] 10 skills visible in `/openclaw_skills`
- [ ] Can install a skill
- [ ] Credits deducted correctly
- [ ] Installed skills shown in `/openclaw_myskills`
- [ ] Assistant uses new skill in conversation

---

## 📚 Documentation

- **User Guide:** OPENCLAW_SKILLS_GUIDE.md
- **Commands:** OPENCLAW_SKILLS_COMMANDS.md
- **Complete:** OPENCLAW_SKILLS_COMPLETE.md

---

## 🆘 Troubleshooting

### Migration fails
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Check file exists
ls migrations/011_openclaw_skills.sql
```

### Tests fail
```bash
# Check database connection
python -c "from services import get_database; get_database()"

# Check OpenClaw manager
python -c "from app.openclaw_manager import get_openclaw_manager"
```

### Bot doesn't start
```bash
# Check imports
python -c "from app.handlers_openclaw_skills import register_openclaw_skill_handlers"

# Check syntax
python -m py_compile app/handlers_openclaw_skills.py
```

---

## 🎉 You're Done!

Your bot now supports skill upgrades! 🚀

Users can:
- ✅ Browse 10 skills
- ✅ Install with credits
- ✅ Upgrade their assistant
- ✅ Manage skills

**Start promoting the new feature!** 📢
