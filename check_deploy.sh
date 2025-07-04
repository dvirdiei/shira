#!/bin/bash
# בדיקת מוכנות לhעלאה ל-Render

echo "🔍 בודק מוכנות לhעלאה ל-Render..."
echo

# בדיקת קבצים נדרשים
echo "📁 בודק קבצים נדרשים:"

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt קיים"
else
    echo "❌ requirements.txt חסר!"
    exit 1
fi

if [ -f "Procfile" ]; then
    echo "✅ Procfile קיים"
else
    echo "❌ Procfile חסר!"
    exit 1
fi

if [ -f "runtime.txt" ]; then
    echo "✅ runtime.txt קיים"
else
    echo "❌ runtime.txt חסר!"
    exit 1
fi

if [ -f "main.py" ]; then
    echo "✅ main.py קיים"
else
    echo "❌ main.py חסר!"
    exit 1
fi

echo

# בדיקת מבנה תיקיות
echo "📂 בודק מבנה תיקיות:"

dirs=("database" "ToHtml" "PYTHON" "static" "templates")
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ תיקיית $dir קיימת"
    else
        echo "❌ תיקיית $dir חסרה!"
        exit 1
    fi
done

echo

# בדיקת קבצי JavaScript
echo "📜 בודק קבצי JavaScript:"

js_files=("ToHtml/data-loader.js" "ToHtml/map-markers.js" "ToHtml/user-actions.js" "ToHtml/found.js")
for file in "${js_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file קיים"
    else
        echo "❌ $file חסר!"
        exit 1
    fi
done

echo

# בדיקת קבצי Python
echo "🐍 בודק קבצי Python:"

py_files=("PYTHON/api_handlers.py" "PYTHON/routes.py" "PYTHON/__init__.py")
for file in "${py_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file קיים"
    else
        echo "❌ $file חסר!"
        exit 1
    fi
done

echo

# בדיקת קבצי CSS/HTML
echo "🎨 בודק קבצי עיצוב:"

if [ -f "static/style.css" ]; then
    echo "✅ style.css קיים"
else
    echo "❌ style.css חסר!"
    exit 1
fi

if [ -f "templates/index.html" ]; then
    echo "✅ index.html קיים"
else
    echo "❌ index.html חסר!"
    exit 1
fi

echo

# בדיקת קבצי נתונים
echo "💾 בודק קבצי נתונים:"

data_files=("database/found_addresses.csv" "database/not_found_addresses.csv" "database/future_use.csv" "database/deleted_addresses.csv")
for file in "${data_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file קיים"
    else
        echo "⚠️ $file חסר (ייווצר אוטומטית)"
    fi
done

echo
echo "🎉 הפרויקט מוכן להעלאה ל-Render!"
echo
echo "📋 השלבים הבאים:"
echo "1. צור repository חדש ב-GitHub"
echo "2. העלה את כל הקבצים"
echo "3. היכנס ל-render.com"
echo "4. צור Web Service חדש"
echo "5. חבר ל-GitHub repository"
echo "6. Deploy!"
echo
