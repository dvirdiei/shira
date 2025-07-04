@echo off
echo 🔍 בודק מוכנות להעלאה ל-Render...
echo.

echo 📁 בודק קבצים נדרשים:
if exist "requirements.txt" (echo ✅ requirements.txt קיים) else (echo ❌ requirements.txt חסר! & pause & exit)
if exist "Procfile" (echo ✅ Procfile קיים) else (echo ❌ Procfile חסר! & pause & exit)
if exist "runtime.txt" (echo ✅ runtime.txt קיים) else (echo ❌ runtime.txt חסר! & pause & exit)
if exist "main.py" (echo ✅ main.py קיים) else (echo ❌ main.py חסר! & pause & exit)

echo.
echo 📂 בודק מבנה תיקיות:
if exist "database\" (echo ✅ תיקיית database קיימת) else (echo ❌ תיקיית database חסרה! & pause & exit)
if exist "ToHtml\" (echo ✅ תיקיית ToHtml קיימת) else (echo ❌ תיקיית ToHtml חסרה! & pause & exit)
if exist "PYTHON\" (echo ✅ תיקיית PYTHON קיימת) else (echo ❌ תיקיית PYTHON חסרה! & pause & exit)
if exist "static\" (echo ✅ תיקיית static קיימת) else (echo ❌ תיקיית static חסרה! & pause & exit)
if exist "templates\" (echo ✅ תיקיית templates קיימת) else (echo ❌ תיקיית templates חסרה! & pause & exit)

echo.
echo 🎉 הפרויקט מוכן להעלאה ל-Render!
echo.
echo 📋 השלבים הבאים:
echo 1. צור repository חדש ב-GitHub
echo 2. העלה את כל הקבצים
echo 3. היכנס ל-render.com
echo 4. צור Web Service חדש
echo 5. חבר ל-GitHub repository
echo 6. Deploy!
echo.
pause
