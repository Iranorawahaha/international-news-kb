#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际新闻知识库 - 增强版后端服务器
支持API接口、静态文件服务、SSE流式响应
"""

import json
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
import queue

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_PATH = PROJECT_ROOT / "data" / "news-data.json"
CONFIG_PATH = PROJECT_ROOT / "data" / "config.json"
SCRAPER_PATH = PROJECT_ROOT / "scripts" / "simple_scraper.py"  # 使用简化版抓取器

# 全局消息队列（用于SSE）
message_queue = queue.Queue()

class NewsRequestHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # API路由
        if path == "/api/data":
            self.handle_get_data()
        elif path == "/api/config":
            self.handle_get_config()
        elif path == "/api/health":
            self.handle_health_check()
        # 静态文件路由
        elif path in ["/", "/index.html"]:
            self.serve_file(PROJECT_ROOT / "index.html", "text/html")
        elif path == "/css/style.css":
            self.serve_file(PROJECT_ROOT / "css" / "style.css", "text/css")
        elif path == "/js/app.js":
            self.serve_file(PROJECT_ROOT / "js" / "app.js", "application/javascript")
        elif path == "/js/embedded-data.js":
            self.serve_file(PROJECT_ROOT / "js" / "embedded-data.js", "application/javascript")
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/api/refresh":
            self.handle_refresh()
        elif path == "/api/save-data":
            self.handle_save_data()
        elif path == "/api/parse-url":
            self.handle_parse_url()
        elif path == "/api/test-sources":
            self.handle_test_sources()
        else:
            self.send_error(404, "Not Found")

    def serve_file(self, file_path: Path, content_type: str):
        """提供静态文件服务"""
        try:
            if not file_path.exists():
                print(f"File not found: {file_path}")
                self.send_error(404, f"File not found: {file_path.name}")
                return

            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            print(f"Error serving file {file_path}: {e}")
            self.send_error(500, f"Internal Server Error: {e}")

    def handle_health_check(self):
        """健康检查接口"""
        self.send_json_response(200, {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })

    def handle_get_data(self):
        """获取新闻数据"""
        try:
            if DATA_PATH.exists():
                with open(DATA_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"meta": {}, "news": []}

            self.send_json_response(200, data)

        except Exception as e:
            print(f"Error loading data: {e}")
            self.send_json_response(500, {"error": str(e)})

    def handle_get_config(self):
        """获取配置信息"""
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}

            self.send_json_response(200, config)

        except Exception as e:
            print(f"Error loading config: {e}")
            self.send_json_response(500, {"error": str(e)})

    def handle_save_data(self):
        """保存新闻数据"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # 确保目录存在
            DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.send_json_response(200, {"success": True, "message": "数据已保存"})
            print(f"✅ Data saved: {len(data.get('news', []))} news items")

        except Exception as e:
            print(f"Error saving data: {e}")
            self.send_json_response(500, {"error": str(e)})

    def handle_refresh(self):
        """
        刷新数据（启动抓取任务）
        使用SSE（Server-Sent Events）流式返回进度
        """
        print("\n🔄 Starting refresh process...")

        # 设置SSE响应头
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        def send_sse_event(event_data):
            """发送SSE事件"""
            try:
                if isinstance(event_data, dict):
                    event_str = json.dumps(event_data, ensure_ascii=False)
                else:
                    event_str = str(event_data)

                message = f"data: {event_str}\n\n"
                self.wfile.write(message.encode('utf-8'))
                self.wfile.flush()
            except Exception as e:
                print(f"SSE send error: {e}")

        try:
            # 发送开始事件
            send_sse_event({
                'type': 'progress',
                'percent': 0,
                'message': '🚀 正在启动采集任务...'
            })

            # 检查抓取脚本是否存在
            if not SCRAPER_PATH.exists():
                send_sse_event({
                    'type': 'error',
                    'message': f'❌ 抓取脚本未找到: {SCRAPER_PATH}'
                })
                return

            # 启动抓取进程
            cmd = [
                sys.executable,
                str(SCRAPER_PATH),
                '--date', datetime.now().strftime("%Y-%m-%d")
            ]

            print(f"Running command: {' '.join(cmd)}")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(PROJECT_ROOT),
                text=True,
                bufsize=1,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )

            # 实时读取输出并转发给前端
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break

                line = line.strip()
                if line:
                    try:
                        # 尝试解析为JSON
                        data = json.loads(line)
                        send_sse_event(data)
                    except json.JSONDecodeError:
                        # 非JSON行，作为普通消息发送
                        send_sse_event({
                            'type': 'log',
                            'message': line
                        })

            # 检查进程退出码
            return_code = process.returncode
            if return_code != 0:
                error_output = process.stderr.read()
                send_sse_event({
                    'type': 'warning',
                    'message': f'⚠️ 抓取进程退出码: {return_code}'
                })
                if error_output:
                    send_sse_event({
                        'type': 'error',
                        'message': f'错误信息: {error_output[:500]}'
                    })

        except Exception as e:
            print(f"Refresh error: {e}")
            send_sse_event({
                'type': 'error',
                'message': f'❌ 刷新过程异常: {str(e)}'
            })

    def handle_parse_url(self):
        """解析URL（快速录入功能）"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            url = data.get('url', '')
            if not url:
                self.send_json_response(400, {'error': 'URL不能为空'})
                return

            # 简单的URL解析（实际项目中可以使用更复杂的解析）
            result = {
                'title': f'从URL提取的标题: {url[:50]}',
                'source': urlparse(url).netloc,
                'summary': '自动解析的内容摘要',
                'date': datetime.now().strftime("%Y-%m-%d"),
                'url': url
            }

            self.send_json_response(200, {'success': True, 'data': result})

        except Exception as e:
            print(f"Parse URL error: {e}")
            self.send_json_response(500, {'error': str(e)})

    def handle_test_sources(self):
        """测试信源连通性"""
        try:
            # 导入抓取器进行测试
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
            from simple_scraper import SimpleScraper

            scraper = SimpleScraper()
            results = scraper.test_source_connectivity()

            self.send_json_response(200, {
                'success': True,
                'results': results,
                'test_time': datetime.now().isoformat()
            })

        except Exception as e:
            print(f"Test sources error: {e}")
            self.send_json_response(500, {'error': str(e)})

    def send_json_response(self, status_code: int, data: dict):
        """发送JSON响应"""
        try:
            response_body = json.dumps(data, ensure_ascii=False).encode('utf-8')

            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', len(response_body))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_body)

        except Exception as e:
            print(f"Error sending JSON response: {e}")


def run_server(port=8080):
    """启动HTTP服务器"""

    # 检查端口是否被占用
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
    except OSError:
        print(f"⚠️ 端口 {port} 已被占用，尝试停止旧进程...")
        import signal
        os.system(f'pkill -f "python.*http.server.*{port}" 2>/dev/null')
        time.sleep(2)

    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, NewsRequestHandler)

    print(f"\n{'='*60}")
    print(f"🌐 国际新闻知识库服务器已启动")
    print(f"{'='*60}")
    print(f"📍 访问地址: http://localhost:{port}")
    print(f"📂 项目目录: {PROJECT_ROOT}")
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 服务器正在关闭...")
        httpd.shutdown()
        print("✅ 服务器已关闭")


if __name__ == '__main__':
    # 支持命令行参数指定端口
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
