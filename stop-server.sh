#!/bin/bash
# ============================================================
# 国际新闻知识库 - 停止服务器脚本
# 用法: ./stop-server.sh
# ============================================================

echo "🛑 正在停止国际新闻知识库服务器..."
echo ""

# 方法1：从.pid文件读取
if [ -f ".server.pid" ]; then
    PID=$(cat .server.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID 2>/dev/null
        echo "✅ 已停止进程 (PID: $PID)"
        rm -f .server.pid
    else
        echo "⚠️  进程已不存在 (PID: $PID)"
        rm -f .server.pid
    fi
fi

# 方法2：通过端口查找并终止
PORT=8080
PIDS=$(lsof -t -i :$PORT 2>/dev/null)
if [ -n "$PIDS" ]; then
    for pid in $PIDS; do
        kill $pid 2>/dev/null && echo "✅ 已停止进程 (PID: $pid)"
    done
else
    echo "ℹ️  未找到监听端口 $PORT 的进程"
fi

echo ""
echo "✨ 服务器已停止"
echo "   如需重新启动: ./start-server.sh"
