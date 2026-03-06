from flask import Flask, render_template, jsonify, request
import redis
import json
from datetime import datetime
import time
from core.mqtt_client import MQTTClient
from core.Config import Config

app = Flask(__name__)

config = Config('config.conf')

# 初始化MQTT客户端
mqtt_client = MQTTClient(broker_host=config.get_broker_host(),
                         broker_port=config.get_broker_port(),
                         username=config.get_broker_username(),
                         password=config.get_broker_password())
mqtt_client.connect()


def format_time_diff(seconds):
    """将秒数转换为 x时x分x秒 格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}时{minutes}分{secs}秒"
    elif minutes > 0:
        return f"{minutes}分{secs}秒"
    else:
        return f"{secs}秒"


def get_redis_data():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    data = []
    current_time = time.time()

    for key in r.keys('device:*'):
        device_id = key.replace('device:', '')
        value = r.get(key)
        try:
            value_dict = json.loads(value)
            timestamp = value_dict.get('timestamp', 0)
            time_diff = current_time - timestamp

            # 判断在线状态
            if time_diff > 60:
                status = f"离线 {format_time_diff(time_diff)}"
                status_color = "red"
            else:
                status = "在线"
                status_color = "green"

            # frp状态
            frp_status = "停止"
            frp_status_color = "red"
            frp_status_data = value_dict.get("frp_active", False)
            if frp_status_data == True:
                frp_status = "运行"
                frp_status_color = "green"
                
            
            data.append({
                'device_id': device_id,
                'local_ip': value_dict.get('local_ip', ''),
                'timestamp': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                'public_ip': value_dict.get('public_ip', {}).get('ip', ''),
                'get_time': datetime.fromtimestamp(value_dict.get('public_ip', {}).get('get_time', 0)).strftime(
                    '%Y-%m-%d %H:%M:%S'),
                'status': status,
                'status_color': status_color,
                'frp_status': frp_status,
                'frp_status_color': frp_status_color,
                'frp_status_data': frp_status_data
            })
        except:
            pass
    return data


@app.route('/')
def index():
    data = get_redis_data()
    return render_template('index.html', data=data)


@app.route('/api/data')
def api_data():
    data = get_redis_data()
    return jsonify(data)


@app.route('/api/refresh_ip', methods=['POST'])
def refresh_ip():
    """接收刷新IP请求并发送MQTT命令"""
    device_id = request.json.get('device_id')
    if not device_id:
        return jsonify({'success': False, 'message': '设备ID不能为空'})

    success = mqtt_client.send_refresh_ip_cmd(device_id)

    if success:
        return jsonify({'success': True, 'message': f'已向设备 {device_id} 发送刷新IP命令'})
    else:
        return jsonify({'success': False, 'message': 'MQTT命令发送失败'})

@app.route('/api/frp_ctl', methods=['POST'])
def frp_ctl():
    """接收刷新IP请求并发送MQTT命令"""
    device_id = request.json.get('device_id')
    if not device_id:
        return jsonify({'success': False, 'message': '设备ID不能为空'})
    
    # 操作禁用或者启用
    operation = request.json.get('operation')
    success = mqtt_client.send_op_frp(device_id, operation)

    if success:
        return jsonify({'success': True, 'message': f'已向设备 {device_id} 发送Frp命令'})
    else:
        return jsonify({'success': False, 'message': 'MQTT命令发送失败'})

if __name__ == '__main__':
    app.run(debug=True, port=6000)