#!/bin/bash
echo "============================================"
echo "  电力用户画像知识图谱系统 V2.0"
echo "============================================"
echo ""

DIR="$(cd "$(dirname "$0")" && pwd)"

# 检查端口
if netstat -ano 2>/dev/null | grep -q ":8000 "; then
  echo " [警告] 端口 8000 已被占用"
fi

echo "[1/2] 启动 Django 后端..."
cd "$DIR"
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!
sleep 3

echo "[2/2] 启动 Vue 前端..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!
sleep 4

echo ""
echo "============================================"
echo "  系统启动完成！"
echo "  前端页面 : http://localhost:5186"
echo "  后端接口 : http://localhost:8000"
echo "  管理员   : admin / admin123"
echo "  测试用户 : user001 / pass123456"
echo "============================================"
echo "  按 Ctrl+C 停止所有服务"
echo "============================================"

cleanup() {
  echo "正在停止服务..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit 0
}
trap cleanup INT TERM
wait
