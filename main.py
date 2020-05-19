from auth import User

if __name__ == '__main__':
    u = input("输入用户名:").strip()
    p = input('输入用户密码:').strip()
    user = User(u, p, auto_code=True)
