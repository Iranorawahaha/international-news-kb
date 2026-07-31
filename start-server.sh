#!/bin/bash
# ============================================================
# 国际新闻知识库 - 快速启动脚本 v1.0
# 用法: ./start-server.sh [端口号]
# 示例: ./start-server.sh 8080
# ============================================================

# 配置
PROJECT_DIR="/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
PORT=${1:-8080}  # 默认端口8080
LOG_FILE="server.log"

echo "🚀 国际新闻知识库 - 启动中..."
echo "================================================"

# 检查端口是否被占用
if lsof -i :$PORT | grep -q "LISTEN"; then
    echo "⚠️  端口 $PORT 已被占用！"
    echo "   正在尝试终止旧进程..."
    lsof -i :$PORT | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ 旧进程已终止"
fi

# 进入项目目录
cd "$PROJECT_DIR" || exit 1

# 检查必要文件
if [ ! -f "scripts/server.py" ]; then
    echo "❌ 错误: 找不到 scripts/server.py"
    exit 1
fi

if [ ! -f "js/embedded-data.js" ]; then
    echo "⚠️  警告: 前端数据文件不存在"
    echo "   请先运行: python3 scripts/generate_data.py"
    exit 1
fi

# 获取本机IP地址
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

# 启动服务器（后台运行）
echo "📍 项目目录: $PROJECT_DIR"
echo "🌐 监听端口: $PORT"
echo "💻 本机访问: http://localhost:$PORT"
echo "🌍 局域网访问: http://$LOCAL_IP:$PORT"
echo ""
echo "⏳ 正在启动服务器..."

# 使用nohup确保终端关闭后服务继续运行
nohup python3 scripts/server.py $PORT > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# 等待启动
sleep 2

# 检查是否成功启动
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo ""
    echo "✅ 服务器启动成功！"
    echo "================================================"
    echo ""
    echo "📱 访问地址："
    echo "   • 本机: http://localhost:$PORT"
    echo "   • 局域网: http://$LOCAL_IP:$PORT"
    echo ""
    echo "📊 系统信息："
    echo "   • 进程PID: $SERVER_PID"
    echo "   • 日志文件: $LOG_FILE"
    echo ""
    echo "💡 使用提示："
    echo "   • 按 Ctrl+C 可停止此脚本（服务器继续运行）"
    echo "   • 查看日志: tail -f $LOG_FILE"
    echo "   • 停止服务器: ./stop-server.sh 或 kill $SERVER_PID"
    echo ""
    echo "🌐 将局域网地址发给同事即可共享访问！"
    echo ""
    
    # 保存PID到文件便于后续管理
    echo "$SERVER_PID" > .server.pid
    
    # 保持脚本运行（显示实时日志）
    echo "📝 实时日志（Ctrl+C退出日志查看，服务器继续运行）："
    echo "------------------------------------------------"
    tail -f "$LOG_FILE"
    
else
    echo "❌ 服务器启动失败！"
    echo "   请查看日志: cat $LOG_FILE"
    exit 1
fi
