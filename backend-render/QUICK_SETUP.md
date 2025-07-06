# ⚡ Quick Setup - הגדרה מהירה

## TL;DR - הגדרה ב-5 דקות

### 1. Supabase Setup
```bash
# לך ל-https://supabase.com
# צור פרויקט → SQL Editor → הרץ:
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    city TEXT,
    latitude FLOAT,
    longitude FLOAT,
    visited BOOLEAN DEFAULT FALSE,
    source_file TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Copy API Keys
מ-Supabase Settings → API:
- Project URL
- Service Role Key (לא anon!)

### 3. Render Environment Variables
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_here
```

### 4. Deploy
- Connect GitHub repo
- Root Directory: `backend-render`
- Build: `pip install -r requirements.txt`
- Start: `python main.py`

### 5. Test
```bash
# Visit your Render URL:
https://your-app.onrender.com/health
```

---

## Problem? Common Fixes:

**"Supabase configuration missing"**
→ הוסף Environment Variables ב-Render

**"Build failed"**
→ ודא שאין pandas ב-requirements.txt

**"503 Error"**
→ זה נורמלי - השרת "נרדם" חינם אחרי 15 דקות

---

**Need help?** ראה RENDER_DEPLOYMENT.md למדריך מפורט
