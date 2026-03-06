import paho.mqtt.client as mqtt
import json
import threading


class MQTTClient:
    def __init__(self, broker_host='localhost', broker_port=1883, username=None, password=None):
        """
        初始化MQTT客户端
        :param broker_host: MQTT broker地址
        :param broker_port: MQTT broker端口
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        if username and password and username != '' and password != '':
            self.client.username_pw_set(username, password)
        self.connected = False

        # 设置回调函数
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        """连接成功回调"""
        if rc == 0:
            self.connected = True
            print(f"MQTT连接成功: {self.broker_host}:{self.broker_port}")
        else:
            self.connected = False
            print(f"MQTT连接失败，返回码: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.connected = False
        print("MQTT连接已断开")

    def connect(self):
        """连接到MQTT broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            # 在后台线程中运行网络循环
            self.client.loop_start()
            print(f"正在连接MQTT broker: {self.broker_host}:{self.broker_port}")
        except Exception as e:
            print(f"MQTT连接错误: {e}")

    def disconnect(self):
        """断开MQTT连接"""
        self.client.loop_stop()
        self.client.disconnect()

    def send_op_frp(self, device_id, operation):
        """
        向指定设备发送frp命令
        :param device_id: 设备ID，如 "A11"
        :param operation: true/false
        """
        topic = f"device/{device_id}/cmd"
        payload = None
        if operation == True:
            payload = json.dumps({"cmd": "frp on"})
        else:
            payload = json.dumps({"cmd": "frp off"})
        
        return self.send_data_device(topic, payload)
    def send_refresh_ip_cmd(self, device_id):
        """
        向指定设备发送刷新IP命令
        :param device_id: 设备ID，如 "A11"
        """
        topic = f"device/{device_id}/cmd"
        payload = json.dumps({"cmd": "refresh ip"})

        return self.send_data_device(topic, payload)
        
    def send_data_device(self, topic, payload):
        try:
            result = self.client.publish(topic, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"成功发送命令到 {topic}: {payload}")
                return True
            else:
                print(f"发送命令失败: {result.rc}")
                return False
        except Exception as e:
            print(f"发送MQTT消息错误: {e}")
            return False