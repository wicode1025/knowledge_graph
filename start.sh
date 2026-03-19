#!/bin/bash

# 电力用户画像系统启动脚本

echo "=========================================="
echo "  电力用户画像系统 - 启动中..."
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 启动后端
echo -e "${YELLOW}启动 Django 后端...${NC}"
python manage.py runserver 8000 > /dev/null 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}后端已启动 (PID: $BACKEND_PID)${NC}"
echo "  后端地址: http://localhost:8000"

# 启动前端
echo -e "${YELLOW}启动 Vue 前端...${NC}"
cd frontend
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}前端已启动 (PID: $FRONTEND_PID)${NC}"
echo "  前端地址: http://localhost:5173"

echo ""
echo "=========================================="
echo -e "${GREEN}系统启动完成!${NC}"
echo "=========================================="
echo "请在浏览器中访问: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
