# WoZaiXiaoYuanPuncher-cloudFunction

我在校园自动打卡程序：[WoZaiXiaoYuanPuncher](https://github.com/HPShark/SNNU-Actions-WoZaiXiaoYuanPuncher) 的云函数版本

### 版本说明

核心代码来自于 [WoZaiXiaoYuanPuncher-cloudFunction](https://github.com/Chorer/WoZaiXiaoYuanPuncher-cloudFunction)。这个版本在原有代码的基础上做了一点修改，可以实现**腾讯云函数自动打卡 + 消息提醒**。只需要在云端部署函数，本地不需要做任何处理，打卡结果会自动发送到微信上。

默认这种打卡
![](https://gitee.com/Bean6560/images/raw/master/typora/daka.png)

## 如果你的打卡还要其他需要填写的问题 请手动抓包并更改index.py文件的answers值

### 视频教程

https://www.aliyundrive.com/s/pLASEs97EDy


### 更新情况
2022-4-17

* 增加打卡提交信息，感谢张佬

2022-4-15

* 去除是否打过卡验证，每次提交都会正常打卡

2022-3-5

* 增加邮编areacode信息

2022-2-11

* 采用坐标拾取功能，定位更加准确
* 增加leancloud的Class属性值填写，多用户可以使用一个leancloud账户，多个Class名称进行配置

2021-8-9

* 根据所在城市和学校名自动获取所有地址信息并进行存储，无需再进行抓包和手动配置
* 减少大量配置项

2021-8-8

* 云函数不支持通过读写文件的方式持久化存储数据，且云数据库收费，因此接入 leanCloud 存储数据

2021-8-4 

* 消息提醒服务从喵提醒改为 pushPlus，不需要再手动激活 48 小时
* 缓存 jwsession 到本地，避免频繁登录可能导致的账户出错问题
* 优化代码结构

### 使用方法

#### 0. 克隆项目到本地

手动点击GitHub页面绿色`code`➡`下载ZIP`

#### 1. 获取 pushPlus 的 token

微信搜索公众号“pushplus 推送加”，关注后即可生成属于自己的 token，后面需要用到

#### 2. 获取 leanCloud 的应用凭证

1）[注册 leanCloud 账号](https://console.leancloud.cn/apps) 

2）到控制台新建应用，应用名字随意，应用版本选择 **开发版**

3）进入应用，点击左侧的“数据存储 ➡ 结构化数据”，新建 Class：名称为“Info”，Class 访问权限为“所有用户”，下面的 ACL 权限选择“限制写入”


4）进入刚才创建的 Class，添加新列，值为“jwsession”，之后添加新行，注意这时候 objectId 会有一个值。如果你知道如何抓包获取自己的 jwsession，则可以填入 jwsession 值，否则不用管它。

5）点击左侧的“设置 ➡ 应用凭证”，记住 appId 和 masterKey（**请务必自己保管好，不要泄露**） 的值，待会需要用到


#### 3. 创建云函数


1）注册腾讯云账号并登录，进行实名认证 [函数服务 - Serverless - 控制台](https://console.cloud.tencent.com/scf/list?rid=1&ns=default)

2）到 https://console.cloud.tencent.com/scf/list?rid=1&ns=default ，选择 “新建” ➔ “从头开始”，“事件函数” “运行环境：python3.6”，提交方法选择“本地上传文件夹”，“高级配置”➔“环境配置”，内存选择“64MB”，初始化超时时间-“300”，执行超时时间“60”点击“完成”即可创建云函数

#### 4. 修改配置文件

到刚才新创建的云函数中，打开 `config.json` 配置文件进行修改。

1）“我在校园”账号配置项说明：

* `username`：“我在校园”的账号，一般是你的手机号码
* `password`：“我在校园”的密码，忘记了打开小程序重新设置就行（建议四个英文+四个数字 类似“wang1234” 复杂了可能不行,改完密码半小时内不要登录小程序）
* `location`：打卡位置的经纬度，[坐标拾取](https://api.map.baidu.com/lbsapi/getpoint/index.html)


2）“pushPlus” 账号配置项说明：

* `notifyToken`：之前你从 pushPlus 公众号那里获取的 token

3）“leanCloud” 账号配置项说明：

* `appId`：之前在 leanCloud 获取的 appId
* `masterKey`：之前在 leanCloud 获取的 masterKey
* `class_name`:Info ,一个用户对应一个Class，多用户请创建其他用户的Class,步骤在2.3) 如Class为Info_wang。
  
4）mark 配置项说明：
* `mark`：张三 这个可以随意配置，相当于知道给谁打卡的，到时候方便查看结果。

5）单用户和多用户填写示例
* 单用户：
  ```
  [
    {
        "wozaixiaoyaun_data":{
        "username": "15512345678",
        "password": "wzxywzxy",
        "location":"133.333333,33.333333"
        },
        "pushPlus_data":{
        "notifyToken" : "4d25976cc88888ae8f8688889780bfe1"
        },
        "leanCloud_data":{
        "appId":"p8888888888888888888888j-aaaaoHsz",
        "masterKey": "J888888888888888888kNX8R",
        "class_name": "Info"
        },
        "mark": "Bean"
    }
  ]
  ```
* 多用户：
    ```
    [
        {
            "wozaixiaoyaun_data":{
            "username": "15512345678",
            "password": "wzxywzxy",
            "location":"133.333333,33.333333"
            },
            "pushPlus_data":{
            "notifyToken" : "4d25976cc88888ae8f8688889780bfe1"
            },
            "leanCloud_data":{
            "appId":"p8888888888888888888888j-aaaaoHsz",
            "masterKey": "J888888888888888888kNX8R",
            "class_name": "Info"
            },
            "mark": "Bean"
        },
        {
            "wozaixiaoyaun_data":{
            "username": "16612345678",
            "password": "wzxywzxy",
            "location":"144.444444,34.444444"
            },
            "pushPlus_data":{
            "notifyToken" : "4d25976cc88888ae8f8688889780bfe1"
            },
            "leanCloud_data":{
            "appId":"p8888888888888888888888j-aaaaoHsz",
            "masterKey": "J888888888888888888kNX8R",
            "class_name": "Info_wang"
            },
            "mark": "小王"
        }
    ]
    ```

#### 5. 安装 leanCloud 库

到刚才新创建的云函数中，`ctrl + shift + ~` 新建终端，`cd src`进入 index.py 所在的文件夹中，通过如下命令安装 leanCloud 库：

```cmd
pip3 install leancloud -t .
```

可能会报错，主要是因为相关库版本不匹配的问题，不影响正常使用。看到 `successfully installed` 就说明安装成功了。

#### 6. 部署和测试

修改完成后点击`部署`并`测试`，如果没有收到信息，点击上方“日志查询”进行查看。如果微信有收到 pushPlus 公众号发来的信息，说明设置 ok。效果如下图所示：

1）模板消息：
![](https://raw.githubusercontent.com/bean661/utils/main/notify.png)


进入即可查看打卡的信息。

#### 7. 实现自动打卡

点击控制台左侧的“触发管理”，“创建触发器”新建一个云函数触发器。设置如下：

![](https://github.com/bean661/utils/raw/main/chufaqi.png)

触发时间使用的是 Cron 表达式，这里的意思是每天 6点、8 点各触发（打卡）一次，可以自己修改，按照自己学校规定的打卡时间段来设置。

最后提交就可以了，以后到点了就会自动打卡并把打卡结果发到你的微信上。

### Q & A

**1）云函数服务收费吗？**

免费。免费调用额度是 100 万次/月，正常用户最多调用 900 次/月，因此绝对够用

**2）都用云函数了，为什么不直接链接云数据库？**

云数据库没有免费额度，没必要为了存储一个 jwsession 花钱

**3）leanCloud 服务收费吗？**

免费。开发版的免费额度是 1GB/天，因此绝对够用

**4）收到消息说“登录失败，请检查账号信息”，应该怎么办？**

待优化功能。很可能是因为频繁登录导致的，这时候就别依赖云函数模拟登录获取 jwsession 了，请自己手动抓包获取 jwsession，填入 leanCloud 的 Class 中 

**5）不能自动定位吗？**

通过坐标拾取定位，无论如何，配置项已经非常少了。

**6）地址是否准确？**

脚本使用的是和小程序一样的高德地图 API，准确性基本没问题                      

**7）leanCloud 库可以选择其它安装路径吗？**

不建议。你需要通过 `sys.path` 修改导包路径，很麻烦，而且会遇到其它依赖导入路径出错的问题。所以最简单的方法就是直接安装在 `index.py` 的所在路径下。

### 鸣谢

* [@Chorer：WoZaiXiaoYuanPuncher](https://github.com/Chorer/WoZaiXiaoYuanPuncher-cloudFunction)

### 声明

- 此脚本仅做正常情况下免去手动打卡之用，**请勿瞒报、误报、漏报**
- 此脚本默认使用者不存在以下异常情况：位于风险地区、接触确诊病例、接触疑似病例、本人疑似患病、本人确诊患病等情况，**如与事实不符，请修改文件的相应字段**
- 如使用者存在以上异常情况，请**立即停止使用此脚本**，并在小程序中**如实填报**
- 使用者请务必不要泄露自己的 jwsession、masterKey、notifyToken
- 使用此脚本产生的任何问题**由使用者负责**，与作者无关
- ![](https://gitee.com/Bean6560/images/raw/master/typora/QQ%E5%9B%BE%E7%89%8720220417221246.jpg)
