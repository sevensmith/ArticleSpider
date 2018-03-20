import re
import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
headers = {
    'HOST': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com',
    'User-Agent': user_agent
}


def get_xsrf():
    response = requests.get('https://www.zhihu.com/signin', headers=headers)
    print(response.text)


def zhizhu_login(user, passwd):
    if re.match('^1\d{10}', user):
        print('iphone login')
        post_url = 'https://www.zhihu.com/api/v3/oauth/sig_nin'
        post_data = {
            '_xsrf': '',
            'username': user,
            'password': passwd
        }

if __name__ == '__main__':
    get_xsrf()