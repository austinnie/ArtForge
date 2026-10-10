# -*- coding: utf-8 -*-
import os, mimetypes
import requests
from dotenv import load_dotenv

load_dotenv()

aid = os.getenv('WECHAT_APP_ID')
sec = os.getenv('WECHAT_APP_SECRET')

# 改这一行为你的真实图片路径
IMG = r"E:\SD_OpenVINO\ArtForge\cover.jpg"

# 1. 拿 token
r = requests.get(
    'https://api.weixin.qq.com/cgi-bin/token',
    params={'grant_type': 'client_credential', 'appid': aid, 'secret': sec}
).json()
print('token 返回:', r)
if 'access_token' not in r:
    print('❌ 拿 token 失败。常见原因：')
    print('   1. AppID/Secret 错')
    print('   2. 你的公网IP不在公众号 IP 白名单里')
    exit()
tok = r['access_token']

# 2. 检查图片
if not os.path.exists(IMG):
    print('❌ 图片不存在:', IMG)
    exit()

# 3. 上传成永久素材
mime = mimetypes.guess_type(IMG)[0] or 'image/jpeg'
with open(IMG, 'rb') as f:
    resp = requests.post(
        'https://api.weixin.qq.com/cgi-bin/material/add_material',
        params={'access_token': tok, 'type': 'image'},
        files={'media': (os.path.basename(IMG), f, mime)}
    ).json()

print('上传返回:', resp)
if 'media_id' in resp:
    print()
    print('👉 请把下面这行加到 .env:')
    print('WECHAT_THUMB_MEDIA_ID=' + resp['media_id'])