#!!!项目的说明还没写完,对Django不是很懂的朋友不要轻易安装哦

### 本项目涉及到的技术及相关库
1. python
2. django
3. mysql
4. html,css,zepto.js
5. weui,weui.js
6. django-ckeditor
7. smart_selects,
8. nginx
9. uwsgi

### 启动及运行方法
##### 打开django配置文件
```
mao>settings.py
```
##### 配置SECRET_KEY的值
```
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['','127.0.0.1']

```
##### 配置mysql数据库
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gaomao',
        'USER':'root',
        'PASSWORD':'',#填写你的数据库密码
        'HOST':'',
        'PORT':'3306',
        'CONN_MAX_AGE':60*10,
        'OPTIONS':{
            'init_command':"SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```
##### 配置微信认证，支付等相关选项
```
#微信登录支付相关配置，还有微信支付商户账号等
WECHAT_TOKEN = ''
EncodingAESKey =''
WECHAT_APPID = ''
WECHAT_SECRET=''
WECHAT_MCH_ID=''
WECHAT_API_KEY=''
WECHAT_REDIRECT_URL=''
```
