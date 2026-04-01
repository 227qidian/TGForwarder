from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
import json
import subprocess
import threading
import time
import signal

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config

app = Flask(__name__)

# 脚本状态管理
script_status = {
    'forwarder': {'running': False, 'pid': None, 'output': []},
    'link_checker': {'running': False, 'pid': None, 'output': []}
}

# 读取配置
@app.route('/')
def index():
    return render_template('index.html', config=config.config)

# 保存配置
@app.route('/save_config', methods=['POST'])
def save_config():
    data = request.json
    config.update(data)
    return jsonify({'status': 'success'})

def kill_process_and_children(pid):
    """终止进程及其所有子进程"""
    try:
        # 先尝试使用进程组方式终止
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except:
        try:
            # 如果失败，直接终止主进程
            os.kill(pid, signal.SIGTERM)
        except:
            pass

# 启动转发脚本
@app.route('/start_forwarder')
def start_forwarder():
    if script_status['forwarder']['running']:
        return jsonify({'status': 'error', 'message': '脚本已在运行'})
    
    def run_forwarder():
        script_status['forwarder']['running'] = True
        script_status['forwarder']['output'] = []
        
        try:
            process = subprocess.Popen(
                ['python3', 'TGForwarder.py'],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                preexec_fn=os.setsid  # 创建新的进程组，方便终止
            )
            
            script_status['forwarder']['pid'] = process.pid
            script_status['forwarder']['output'].append('[系统] 脚本已启动，PID: %d' % process.pid)
            
            # 实时读取输出
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    script_status['forwarder']['output'].append(line)
                    if len(script_status['forwarder']['output']) > 100:
                        script_status['forwarder']['output'].pop(0)
            
            # 等待进程结束
            return_code = process.wait()
            script_status['forwarder']['output'].append('[系统] 脚本已退出，返回码: %d' % return_code)
            
        except Exception as e:
            script_status['forwarder']['output'].append('[错误] 运行异常: %s' % str(e))
        finally:
            script_status['forwarder']['running'] = False
            script_status['forwarder']['pid'] = None
    
    threading.Thread(target=run_forwarder, daemon=True).start()
    return jsonify({'status': 'success'})

# 停止转发脚本
@app.route('/stop_forwarder')
def stop_forwarder():
    if not script_status['forwarder']['running']:
        return jsonify({'status': 'error', 'message': '脚本未运行'})
    
    try:
        pid = script_status['forwarder']['pid']
        if pid:
            kill_process_and_children(pid)
            script_status['forwarder']['running'] = False
            script_status['forwarder']['pid'] = None
            return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '停止失败: ' + str(e)})

# 启动链接检测脚本
@app.route('/start_link_checker')
def start_link_checker():
    if script_status['link_checker']['running']:
        return jsonify({'status': 'error', 'message': '脚本已在运行'})
    
    def run_link_checker():
        script_status['link_checker']['running'] = True
        script_status['link_checker']['output'] = []
        
        try:
            process = subprocess.Popen(
                ['python3', 'TGNetDiskLinkChecker.py'],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                preexec_fn=os.setsid  # 创建新的进程组，方便终止
            )
            
            script_status['link_checker']['pid'] = process.pid
            script_status['link_checker']['output'].append('[系统] 脚本已启动，PID: %d' % process.pid)
            
            # 实时读取输出
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    script_status['link_checker']['output'].append(line)
                    if len(script_status['link_checker']['output']) > 100:
                        script_status['link_checker']['output'].pop(0)
            
            # 等待进程结束
            return_code = process.wait()
            script_status['link_checker']['output'].append('[系统] 脚本已退出，返回码: %d' % return_code)
            
        except Exception as e:
            script_status['link_checker']['output'].append('[错误] 运行异常: %s' % str(e))
        finally:
            script_status['link_checker']['running'] = False
            script_status['link_checker']['pid'] = None
    
    threading.Thread(target=run_link_checker, daemon=True).start()
    return jsonify({'status': 'success'})

# 停止链接检测脚本
@app.route('/stop_link_checker')
def stop_link_checker():
    if not script_status['link_checker']['running']:
        return jsonify({'status': 'error', 'message': '脚本未运行'})
    
    try:
        pid = script_status['link_checker']['pid']
        if pid:
            kill_process_and_children(pid)
            script_status['link_checker']['running'] = False
            script_status['link_checker']['pid'] = None
            return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': '停止失败: ' + str(e)})

# 获取脚本状态
@app.route('/get_status')
def get_status():
    return jsonify(script_status)

# 获取脚本输出
@app.route('/get_output/<script>')
def get_output(script):
    if script in script_status:
        return jsonify({'output': script_status[script]['output']})
    return jsonify({'output': []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

# 导出 app 供 Gunicorn 使用
application = app
