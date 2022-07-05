# -*- encoding:utf-8 -*-
import datetime
import requests
import json
import utils
from urllib.parse import urlencode
import leancloud
import time


class leanCloud:
    # 初始化 leanCloud 对象
    def __init__(self, appId, masterKey, class_name):
        leancloud.init(appId, master_key=masterKey)
        self.obj = leancloud.Query(class_name).first()

    # 获取 jwsession
    def getJwsession(self):
        return self.obj.get('jwsession')

    # 设置 jwsession
    def setJwsession(self, value):
        self.obj.set('jwsession', value)
        self.obj.save()

    # 判断之前是否保存过地址信息
    def hasAddress(self):
        if self.obj.get('hasAddress') == False or self.obj.get('hasAddress') is None:
            return False
        else:
            return True

    # 请求地址信息
    def requestAddress(self, location):
        # 根据经纬度求具体地址
        url2 = 'https://restapi.amap.com/v3/geocode/regeo'
        res = utils.geoCode(url2, {
            "location": location
        })
        _res = res['regeocode']['addressComponent']
        print(_res)
        location = location.split(',')
        sign_data = {
            "answers": '["0"]',
            "latitude": location[1],
            "longitude": location[0],
            "country": '中国',
            "city": _res['city'],
            "district": _res['district'],
            "province": _res['province'],
            "township": _res['township'],
            "street": _res['streetNumber']['street'],
            "towncode": "0",
            "citycode": "0",
            "areacode": _res['adcode'],
            "timestampHeader":round(time.time())
        }
        return sign_data


class WoZaiXiaoYuanPuncher:
    def __init__(self, item):
        # 我在校园账号数据
        self.data = item['wozaixiaoyaun_data']
        # pushPlus 账号数据
        self.pushPlus_data = item['pushPlus_data']
        # leanCloud 账号数据
        self.leanCloud_data = item['leanCloud_data']
        # mark 打卡用户昵称
        self.mark = item['mark']
        # 初始化 leanCloud 对象
        self.leanCloud_obj = leanCloud(self.leanCloud_data['appId'], self.leanCloud_data['masterKey'],
                                       self.leanCloud_data['class_name'])
        # 学校打卡时段
        self.seqs = []
        # 打卡结果
        self.status_code = 0
        # 请求头
        self.header = {
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
            "content-type": "application/json;charset=UTF-8",
            "Content-Length": "2",
            "Host": "gw.wozaixiaoyuan.com",
            "Accept-Language": "en-us,en",
            "Accept": "application/json, text/plain, */*"
        }
        # signdata  要保存的信息
        self.sign_data = ""
        # 请求体（必须有）
        self.body = "{}"

        # 登录

    def login(self):
        # 登录接口
        loginUrl = "https://gw.wozaixiaoyuan.com/basicinfo/mobile/login/username"
        username, password = str(self.data['username']), str(self.data['password'])
        url = f'{loginUrl}?username={username}&password={password}'
        self.session = requests.session()
        # 登录
        response = self.session.post(url=url, data=self.body, headers=self.header)
        res = json.loads(response.text)
        if res["code"] == 0:
            jwsession = response.headers['JWSESSION']
            self.leanCloud_obj.setJwsession(jwsession)
            return True
        else:
            print("登录失败，请检查账号信息" + str(res))
            self.status_code = 5
            return False

    # 获取打卡列表，判断当前打卡时间段与打卡情况，符合条件则自动进行打卡
    def PunchIn(self):
        print("查询是否打卡")
        url = "https://student.wozaixiaoyuan.com/health/getHealthLatest.json"
        self.header['Host'] = "student.wozaixiaoyuan.com"
        self.header['content-type'] = "application/x-www-form-urlencoded"
        self.header['Content-Length'] = "0"
        self.header['JWSESSION'] = self.leanCloud_obj.getJwsession()
        self.session = requests.session()
        response = self.session.post(url=url, data=self.body, headers=self.header)
        res = json.loads(response.text)
        # 如果 jwsession 无效，则重新 登录 + 打卡
        if res['code'] == -10:
            print('jwsession 无效，尝试账号密码打卡')
            self.status_code = 4
            loginStatus = self.login()
            if loginStatus:
                print("登录成功")
                self.PunchIn()
            else:
                print("登录失败")
                self.sendNotification()
        elif res['code'] == 0:
            self.doPunchIn()

    # 打卡
    def doPunchIn(self):
        print('开始打卡')
        url = "https://student.wozaixiaoyuan.com/health/save.json"
        self.header['Host'] = "student.wozaixiaoyuan.com"
        self.header['content-type'] = "application/x-www-form-urlencoded"
        self.header['JWSESSION'] = self.leanCloud_obj.getJwsession()
        sign_data = self.leanCloud_obj.requestAddress(self.data['location'])
        self.sign_data = sign_data
        data = urlencode(sign_data)
        response = self.session.post(url, data=data, headers=self.header)
        response = json.loads(response.text)
        # 打卡情况
        if response["code"] == 0:
            self.status_code = 1
            print("打卡成功")
            if self.pushPlus_data['onlyWrongNotify'] == "false":
                self.sendNotification()
        else:
            print(response)
            print("打卡失败")
            self.sendNotification()

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
            return "❌ 打卡失败，发生未知错误"

    # 推送打卡结果
    def sendNotification(self):
        notifyResult = self.getResult()
        # pushplus 推送
        url = 'http://www.pushplus.plus/send'
        notifyToken = self.pushPlus_data['notifyToken']
        content = json.dumps({
            "打卡用户": self.mark,
            "打卡项目": "健康打卡",
            "打卡情况": notifyResult,
            "打卡信息": self.sign_data,
            "打卡时间": (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
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

def startdk():
    # 读取配置文件
    configs = utils.processJson("config.json").read()
    # 遍历每个用户的账户数据，进行打卡
    for config in configs:
        wzxy = WoZaiXiaoYuanPuncher(config)
        # 如果没有 jwsession，则 登录 + 打卡
        jwsession = wzxy.leanCloud_obj.getJwsession()
        if jwsession == "" or jwsession is None:
            print("使用账号密码登录")
            loginStatus = wzxy.login()
            if loginStatus:
                print("登录成功,开始打卡")
                wzxy.PunchIn()
            else:
                print("登录失败")
        else:
            print("检测到jwsession存在，使用jwsession打卡")
            wzxy.PunchIn()

if __name__ == '__main__':
    startdk()

def handler(event, context):
    startdk()
