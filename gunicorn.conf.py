# Gunicorn 配置文件
import os
import multiprocessing

# 绑定地址和端口
bind = "0.0.0.0:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 每个工作进程的最大请求数
max_requests = 1000
max_requests_jitter = 50

# 超时时间（秒）
timeout = 120

# 保持连接时间
keepalive = 5

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 进程名称
proc_name = "tgforwarder"

# 守护进程模式（后台运行）
daemon = False

# 工作目录
chdir = os.path.dirname(os.path.abspath(__file__))

# 预加载应用
preload_app = True

def on_starting(server):
    """服务器启动时创建日志目录"""
    if not os.path.exists("logs"):
        os.makedirs("logs")
