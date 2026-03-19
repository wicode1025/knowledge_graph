@echo off
chcp 65001 >nul
echo ==========================================
echo   电力用户画像系统 - 启动中...
echo ==========================================

cd /d %~dp0

echo [后端] 启动 Django...
start "Django Backend" cmd /k "python manage.py runserver 8000"
echo   后端地址: http://localhost:8000

echo [前端] 启动 Vue...
cd frontend
start "Vue Frontend" cmd /k "npm run dev"
echo   前端地址: http://localhost:5173

cd ..

echo.
echo ==========================================
echo   系统启动完成!
echo ==========================================
echo 请在浏览器中访问: http://localhost:5173
echo.
echo 按任意键退出...
pause >nul
