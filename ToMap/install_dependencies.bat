@echo off
echo ===================================
echo התקנת ספריות נדרשות לסקריפט גאוקודינג
echo ===================================

echo.
echo מתקין ספריות Python הדרושות...
pip install pandas numpy requests openpyxl

echo.
echo בדיקת התקנה...
python -c "import pandas; import numpy; import requests; print('כל הספריות הותקנו בהצלחה!')"

echo.
echo ===================================
echo ההתקנה הושלמה! עכשיו אפשר להריץ את הסקריפט
echo ===================================

pause
