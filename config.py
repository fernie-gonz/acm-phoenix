import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

ADMINS = frozenset(['acm.at.ucr+webmaster@gmail.com'])
SECRET_KEY = 'MIIEpAIBAAKCAQEAwTs9CBbomFmsYmYzChcAT6FYm6szVtW2wlYaPRajiV7XvFaoZfBpDKDy2xsTaWkWdspR2juyyoVStJSuzLt7pIP7SX6ibDkbKtSthZJA5JAqhtvVF2BtR+yApLoM9hWEF4XQZDswMAGgYOBi+/C5FSqW/jPKoSaO+6dVgf+VKS9Nmp9G'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'acm-phoenix.db')
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8

CSRF_ENABLED=True
CSRF_SESSION_KEY="TNSDOSJBjVSszvLMelsRafiw/z/flEnxh2LeZYMXuiSXxCAm32h9d6hkZpJRbE7Lpbk46sJmNLqRzCVInBOezAwOzR3Dv0FHx2s9kwIDAQABAoIBACB3Fnr8dlnafycNKrggQzId1qhY7EhDofAmzUPEQPe8kpyXJrXx3YR8qjD77JgCSv7sYTI8Y365RbsHXBMT0ONENX0UpK9wLMtWbk0J1JNSUYLU/olt7w5tgvOqOrFBzi6xkeC1PR"

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = '6LfDW9YSAAAAAAjSp9n2mS7G1bMwrYH7EESVOLQe'
RECAPTCHA_PRIVATE_KEY = '6LfDW9YSAAAAAIJTT53vTrOzG5NdPhetB6Z8JLao'
RECAPTCHA_OPTIONS = {'theme': 'white'}
