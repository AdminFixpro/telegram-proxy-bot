@echo off
echo -------------------------------------------------
echo   🚀 Setting pip mirror to pypi.tuna.tsinghua.edu.cn
echo -------------------------------------------------
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo -------------------------------------------------
echo   🚀 Installing telethon and requests
echo -------------------------------------------------
pip install telethon requests

echo.
echo ✅ All done! Press any key to exit...
pause > nul
