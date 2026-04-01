#!/bin/bash

# TGForwarder 生产环境启动脚本

# 设置项目目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 创建日志目录
mkdir -p logs

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查 gunicorn 是否安装
if ! command -v gunicorn &> /dev/null; then
    echo "安装 Gunicorn..."
    pip3 install gunicorn
fi

# 启动 Gunicorn
echo "启动 TGForwarder 生产服务器..."
echo "访问地址: http://$(hostname -I | awk '{print $1}'):5000"
echo ""

# 使用配置文件启动
gunicorn backend.app:application -c gunicorn.conf.py

# 如果需要在后台运行，使用以下命令：
# gunicorn backend.app:application -c gunicorn.conf.py --daemon
