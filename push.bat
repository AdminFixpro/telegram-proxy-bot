@echo off
echo 🔄 Adding changes...
git add .

echo 📝 Committing...
git commit -m "Auto update %date% %time%"

echo 🚀 Pushing to GitHub...
git push

echo ✅ Done! Files are up to date on GitHub.
pause
