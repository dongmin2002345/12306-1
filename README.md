## 模拟登录12306
使用requests模拟登录12306，已封装成类，目前仅有模拟登录功能，其他好玩的功能大家自行开发，示例代码:
```python
from auth import User
u = input("输入用户名:").strip()
p = input('输入用户密码:').strip()
user = User(u, p, auto_code=True)
```
传入账号密码示例化User会模拟登录，当登录成功后会在Cookies文件夹保留Cookie信息，下次使用同一账号登录优先使用本地Cookie。

User初始化可接受参数如下：
```python
class User(object):
    def __init__(self, user: str, password: str = None, auto_code: bool = True,
                 code_path: str = "code.jpg"):
        """初始化
        :param user: 用户名
        :param password: 密码，留空时寻找本地cookie
        :param auto_code: 调用API自动识别英文 默认True
        :param code_path: 验证码图片存储位置
        """
```

## 验证码
验证码识别不在本项目具体实现范围内，目前依赖第三方接口的深度学习算法实现，感兴趣朋友朋友可以[传送门](https://blog.csdn.net/weixin_41578580)至API作者博客。

## 其他
本项目仅为研究学习，不能用于其他非法目的。
