# 本模块实现12306用户登录、信息获取
import os
import re
import time
import json
import base64
import requests


class User(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'Referer': 'https://kyfw.12306.cn/otn/resources/login.html',
        'Host': 'kyfw.12306.cn'
    }

    def __init__(self, user: str, password: str = None, auto_code: bool = True,
                 code_path: str = "code.jpg"):
        """初始化
        :param user: 用户名
        :param password: 密码，留空时寻找本地cookie
        :param auto_code: 调用API自动识别英文 默认True
        :param code_path: 验证码图片存储位置
        """
        self.user = user
        self.password = password
        self.auto_code = auto_code
        self.code_path = code_path
        self.client = requests.session()
        if not self.from_disk_get_cookie():
            if not password:
                raise FileNotFoundError('本地不存在Cookie需传入密码！')
            else:
                self.login()
        jar = self.from_disk_get_cookie()
        self.client.cookies.update(jar)
        self.initApi()

    def from_disk_get_cookie(self):
        """读取本地Cookie文件为字典
        :return: dict 或 None
        """
        path = 'Cookies/' + self.user
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        else:
            return

    def login(self):
        """使用账号密码登录12306并保存Cookie至本地
        :return:
        """
        p1 = {
            'algID': 'y6fvmhGlLP',
            'hashCode': 'WRXET1wCtYsDWujgBBDiq2A4aqJOy-G6t5VK5OI0wNY',
            'FMQw': 0,
            'q4f3': 'zh-CN',
            'VPIf': 1,
            'custID': 133,
            'VEek': 'unknown',
            'dzuS': 0,
            'yD16': 0,
            'EOQP': 'c227b88b01f5c513710d4b9f16a5ce52',
            'jp76': '52d67b2a5aa5e031084733d5006cc664',
            'hAqN': 'MacIntel',
            'platform': 'WEB',
            'ks0Q': 'd22ca0b81584fbea62237b14bd04c866',
            'TeRS': '709x1280',
            'tOHY': '24xx800x1280',
            'Fvje': 'i1l1o1s1',
            'q5aJ': '-8',
            'wNLf': '99115dfb07133750ba677d055874de87',
            '0aew': self.headers['User-Agent'],
            'E3gR': '92271eade53193a7130e280652b8e939',
            'timestamp': int(time.time() * 1000)
        }
        r1 = self.client.get('https://kyfw.12306.cn/otn/HttpZF/logdevice',
                             params=p1, headers=self.headers)
        exp = re.search(r'exp":"(\d+)",', r1.text).group(1)
        dfp = re.search(r'dfp":"(.+?)"', r1.text).group(1)
        self.client.cookies.update({'RAIL_DEVICEID': dfp, 'RAIL_EXPIRATION': exp})

        p2 = {'login_site': 'E', 'module': 'login',
              'rand': 'sjrand', str(int(time.time() * 1000)): ''}
        r2 = self.client.get('https://kyfw.12306.cn/passport/captcha/captcha-image64', params=p2)
        image = re.search(r'image":"(.+?)",', r2.text).group(1)
        imgdata = base64.b64decode(image)
        with open(self.code_path, 'wb') as f:
            f.write(imgdata)
        if not self.auto_code:
            os.system('open ' + self.code_path)
            position = {
                1: '49,48', 2: '124,52', 3: '200,43', 4: '259,47',
                5: '50,113', 6: '101,102', 7: '198,112', 8: '250,127'
            }
            capchat = input('请输入图1-8正确答案(多个答案空格分隔): ').strip().split()
            capchat = list(map(lambda x: position[int(x)], capchat))
        else:
            capchat = self.getVerifyResult(self.code_path)
        answer = ','.join(capchat)

        p3 = {'answer': answer, 'rand': 'sjrand', 'login_site': 'E'}
        r3 = self.client.get('https://kyfw.12306.cn/passport/captcha/captcha-check',
                             headers=self.headers, params=p3)
        j3 = r3.json()
        if j3.get('result_message') != '验证码校验成功':
            raise RuntimeError('【验证码异常】: ' + j3.get('result_message'))

        r4 = self.client.post('https://kyfw.12306.cn/passport/web/login',
                              data={'username': self.user,
                                    'password': self.password,
                                    'appid': 'on', 'answer': answer},
                              headers=self.headers)
        j4 = r4.json()
        if j4.get('result_message') != '登录成功':
            raise RuntimeError('【登录失败】: ' + j4.get('result_message'))
        uamtk = j4['uamtk']
        self.client.cookies.update({'uamtk': uamtk})

        r5 = self.client.post('https://kyfw.12306.cn/passport/web/auth/uamtk',
                              headers={'User-Agent': self.headers['User-Agent'],
                                       'Referer': 'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin',
                                       'Origin': 'https://kyfw.12306.cn',
                                       'Host': 'kyfw.12306.cn'},
                              data={'appid': 'otn'})
        j5 = r5.json()
        if j5.get('result_message') != '验证通过':
            raise RuntimeError('【验证失败】: ', j5.get('result_message'))
        tk = j5['newapptk']

        r6 = self.client.post('https://kyfw.12306.cn/otn/uamauthclient',
                              data={'tk': tk},
                              headers=self.headers)
        j6 = r6.json()
        if j6.get('result_message') != '验证通过':
            raise RuntimeError('【验证失败】: ', j6.get('result_message'))

        r7 = self.client.post('https://kyfw.12306.cn/otn/index/initMy12306Api',
                              headers=self.headers)
        r7.encoding = r7.apparent_encoding
        j7 = r7.json()
        if j7.get('status') is not True:
            raise RuntimeError('【登录失败】: 疑似12306登录接口失效')
        cookie = requests.utils.dict_from_cookiejar(self.client.cookies)
        with open('Cookies/' + self.user, 'w') as f:
            json.dump(cookie, f)
        return True

    def initApi(self):
        """获取用户数据，验证登录Cookie是否有效
        :return:
        """
        url = 'https://kyfw.12306.cn/otn/index/initMy12306Api'
        r = self.client.post(url)
        if '"status":true' in r.text:
            print('登录成功:', r.json()['data']['user_name'])
        else:
            if self.password:
                print('Cookie过期，正在重新获取Cookie...')
                self.login()
                self.initApi()
            else:
                raise RuntimeError('Cookie过期，请输入密码登录...')

    @staticmethod
    def getVerifyResult(path: str):
        """调用API接口获取验证码结果
        :param path:
        :return:
        """
        url = "http://littlebigluo.qicp.net:47720/"
        position = {
            1: '49,48', 2: '124,52', 3: '200,43', 4: '259,47',
            5: '50,113', 6: '101,102', 7: '198,112', 8: '250,127'
        }
        ret = []
        file = open(path, 'rb')
        response = requests.post(url, data={"type": "1", },
                                 files={'pic_xxfile': file})
        file.close()
        for i in re.findall("<B>(.*)</B>", response.text)[0].split(" "):
            ret.append(position[int(i)])
        return ret
