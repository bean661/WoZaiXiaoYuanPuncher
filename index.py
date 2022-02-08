import requests
import json
import os
import utils
import time
from urllib.parse import urlencode
class WoZaiXiaoYuanPuncher:
    def __init__(self,check_item):
        self.username = check_item['WZXY_USERNAME']
        self.password = check_item['WZXY_PASSWORD']
        self.location = check_item['location']
        self.pushPlus_notifyToken = check_item['pushPlus_notifyToken']
        self.mark = check_item['mark']
        # JWSESSION
        self.jwsession = None
        # 打卡结果
        self.status_code = 0
        # 登陆接口
        self.loginUrl = "https://gw.wozaixiaoyuan.com/basicinfo/mobile/login/username"
        # 请求头
        self.header = {
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.13(0x18000d32) NetType/WIFI Language/zh_CN miniProgram",
            "Content-Type": "application/json;charset=UTF-8",
            "Content-Length": "2",
            "Host": "gw.wozaixiaoyuan.com",
            "Accept-Language": "en-us,en",
            "Accept": "application/json, text/plain, */*"
        }
        # 请求体（必须有）
        self.body = "{}"
        # sign_data
        self.sign_data = "{}"
    # 登录
    def login(self):
        username, password = self.username, self.password
        url = f'{self.loginUrl}?username={username}&password={password}'
        self.session = requests.session()
        # 登录
        response = self.session.post(url=url, data=self.body, headers=self.header)
        res = json.loads(response.text)
        if res["code"] == 0:
            print("使用账号信息登录成功")
            jwsession = response.headers['JWSESSION']
            self.jwsession = jwsession
            return True
        else:
            print(res)
            print("登录失败，请检查账号信息")
            self.status_code = 5
            return False

    # 执行打卡
    def doPunchIn(self,sign_data):
        print("正在打卡...")
        url = "https://student.wozaixiaoyuan.com/health/save.json"
        self.header['Host'] = "student.wozaixiaoyuan.com"
        self.header['Content-Type'] = "application/x-www-form-urlencoded"
        self.header['JWSESSION'] = self.jwsession
        data = urlencode(sign_data)
        self.session = requests.session()
        response = self.session.post(url=url, data=data, headers=self.header)
        response = json.loads(response.text)
        # 打卡情况
        # 如果 jwsession 无效，则重新 登录 + 打卡
        if response['code'] == -10:
            print(response)
            print('jwsession 无效，将尝试使用账号信息重新登录')
            self.status_code = 4
            loginStatus = self.login()
            if loginStatus:
                self.doPunchIn(self.sign_data)
            else:
                print(response)
                print("重新登录失败，请检查账号信息")
        elif response["code"] == 0:
            self.status_code = 1
            print("打卡成功")
        elif response['code'] == 1:
            print(response)
            print("打卡失败：今日健康打卡已结束")
            self.status_code = 3
        else:
            print(response)
            print("打卡失败")

    # 获取打卡结果
    def getResult(self):
        res = self.status_code
        if res == 1:
            return "✅ 打卡成功"
        elif res == 2:
            return "✅ 你已经打过卡了，无需重复打卡"
        elif res == 3:
            return "❌ 打卡失败，当前不在打卡时间段内"
        elif res == 4:
            return "❌ 打卡失败，jwsession 无效"
        elif res == 5:
            return "❌ 打卡失败，登录错误，请检查账号信息"
        else:
            return "❌ 打卡失败，发生未知错误，请检查日志"

    # 推送打卡结果
    def sendNotification(self):
        notifyTime = utils.getCurrentTime()
        notifyResult = self.getResult()
        # pushplus 推送
        url = 'http://www.pushplus.plus/send'
        notifyToken = self.pushPlus_notifyToken
        content = json.dumps({
            "打卡用户":self.mark,
            "打卡项目": "健康打卡",
            "打卡情况": notifyResult,
            "打卡信息":self.sign_data,
            "打卡时间": notifyTime,
        }, ensure_ascii=False)
        msg = {
            "token": notifyToken,
            "title": "⏰ 我在校园打卡结果通知",
            "content": content,
            "template": "json"
        }
        body = json.dumps(msg).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, data=body, headers=headers).json()
        if r["code"] == 200:
            print("消息经 pushplus 推送成功")
        else:
            print("pushplus: " + r)
            print("消息经 pushplus 推送失败，请检查错误信息")

    # 请求地址信息
    def requestAddress(self):
        # 根据经纬度求具体地址
        url2 = 'https://restapi.amap.com/v3/geocode/regeo'
        res = utils.geoCode(url2, {
            "location": self.location
        })
        print(res)
        return res

    # 保存地址信息
    def getLocationData(self, res):
        _res = res['regeocode']['addressComponent']
        location = self.location.split(',')
        sign_data={
            "answers": '["0"]',
            "latitude": location[1],
            "longitude": location[0],
            "country": '中国',
            "city": _res['city'],
            "district": _res['district'],
            "province": _res['province'],
            "township": _res['township'],
            "street": _res['streetNumber']['street'],
        }
        self.sign_data =sign_data
        return sign_data
    # 返回地址信息
def task(check_item):
    #读取配置文件
    configs = check_item
    wzxy = WoZaiXiaoYuanPuncher(configs)
    addr = wzxy.requestAddress()
    sign_data = wzxy.getLocationData(addr)
    print("正在使用账号信息登录...")
    loginStatus = wzxy.login()
    if loginStatus:
        wzxy.doPunchIn(sign_data)
    else:
        print("登陆失败，请检查账号信息")
    wzxy.sendNotification()
def main_handler(event,context):
    with open(os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="utf-8") as f:
        datas = json.loads(f.read())
    print(datas)
    _check_item = datas.get("user_info", [])[0]
    print(len(datas.get("user_info", [])))
    for check_item in datas.get("user_info", []):
        task(check_item)
        time.sleep(20)
if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="utf-8") as f:
        datas = json.loads(f.read())
    print(datas)
    _check_item = datas.get("user_info", [])[0]
    print(len(datas.get("user_info", [])))
    for check_item in datas.get("user_info", []):
        task(check_item)
        time.sleep(20)

