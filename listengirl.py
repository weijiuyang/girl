from fastapi import FastAPI, HTTPException, Request, Form, Depends, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import urllib.parse
import os
import sys
import re
import random
import datetime
from utils import *
import requests
import shutil
from fastapi.middleware.cors import CORSMiddleware
from config import *
from typing import Optional
import asyncio

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()
# app.mount("/static", StaticFiles(directory="/home/vajor/OneDrive/girl/static"),  name="static")
app.mount("/static", StaticFiles(directory="/home/vajor/OneDrive/girl/static", follow_symlink=True), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.v2ph.com"],  # 允许 v2ph.com 发请求
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.post("/download_v2ph")
async def download_v2ph(request: Request):
    try:
        payload = await request.json()
        html = payload.get("html", [])
        import re

        # 提取所有 data-src 中以 https://cdn.v2ph.com/photos/ 开头的图片链接
        image_urls = re.findall(r'data-src="(https://cdn\.v2ph\.com/photos/[^"]+)"', html)
        print(f"📸 提取到 {len(image_urls)} 个图片链接")
        # image_urls = payload.get("image_urls", [])
        user_agent = payload.get("user_agent", "")
        url = payload.get("url", "")
        cookie = payload.get("cookie", "")
        title = payload.get("title", "")
        print("📥 接收到 V2PH 下载请求：")
        # print(html)
        print(f"共 {len(image_urls)} 张图片")
        print(f"User-Agent: {user_agent}")
        print(f"Cookie: {cookie}")
        print(f"title: {title}")
        
        public, public_no, girlname, public_name, keywords  = ai_key(title)
        
        description = ""
        website = "v2ph"
        database_save(title, url, public, public_no, public_name, girlname, keywords, description, website)
        headers = {
            "User-Agent": user_agent,
            "Cookie": cookie
        }
        os.makedirs(f"/home/vajor/OneDrive/images/albumn/{title}", exist_ok=True)

        curtitle = f"/home/vajor/OneDrive/images/albumn/{title}"
        preimage = f"/home/vajor/OneDrive/images/preview/{title}.jpg"
        print(curtitle)
        count = len([f for f in os.listdir(curtitle)])
        print(f"📂 当前已有图片数量：{count}")
        proxies = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.v2ph.com/album/ae4849mz.html?page=2&hl=zh-Hans",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Cookie": "_gid=GA1.2.919017545.1750330720; frontend-rmu=H5K%2Fh4shZvZnA25IDhyrapNGQv0pUw%3D%3D; frontend-rmt=tqjBX5hsablEQOx%2FMP%2FrECPBHv%2FjRjbEasNHMplPcaHcnW15DnBlmLlEWMEN8Hvz; _ga_170M3FX3HZ=deleted; __stripe_mid=157226d2-4787-426f-8d99-63dbe81ed13323d3b2; frontend=14d8636f9038aee6ec9836f6a1966c5e; _ga_170M3FX3HZ=GS2.1.s1750476001$o9$g0$t1750476001$j60$l0$h0; cf_clearance=vjf159VjewhAqenSALeUjtrLFPF_q82mwyqVDYwI6x8-1750476710-1.2.1.1-nVot9biFJ7v7LDHK8.RU7zOnb_u986msYnLkPdA6iKg9KOXkbvHnILZzug6xC1o90eT3rrx311w1PJuUFh4sl4GtZWxPuqR5cVe1rYWRXjFHLIiNtfGERPzOnAkaHTrUUJk28e6iZSeyBaMnfZdJcavNdEPq_znVYO4yQa_AIX8FrDmDSOfZyBYq3veY8ylzXuw6x3PE3filmvtQO2LDM8ExfAiAtrEUVee1dYrkKQlqiG4LFim_c11CylXQXPRwn3WyudHP9s5v2r47Wm3b958.Plbln3sqsBlEf9Jk5mx7m1pUdsrNqQjVFOHePhaLTfj9uiGrQd2MOhqOG.vxXol7fcP7dUs34ehSYhNEMug; _ga_170M3FX3HZ=GS2.1.s1750476001$o9$g1$t1750477250$j6$l0$h0; _ga=GA1.1.170908555.1749708166"
            }
        headers['Cookie'] = cookie
        session = requests.Session()
        

        for url in image_urls:
            print(url)
            count += 1
            response = session.get(url, proxies=proxies, headers=headers, verify=False, timeout=10)
            with open(f"{curtitle}/{count}.jpg", "wb") as f:
                f.write(response.content)
            
        response = session.get(url, proxies=proxies, headers=headers, verify=False, timeout=10)
        with open(f"{preimage}", "wb") as f:
            f.write(response.content)
        
        return JSONResponse(content={"status": "ok", "count": len(image_urls)})

    except Exception as e:
        print(f"❌ 处理 v2ph 下载请求失败: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="::", port=3334)
    uvicorn.run(
        "getweb:app",  # 文件名:FastAPI实例名
        host="0.0.0.0",
        port=3333,
        reload=True  # 启用自动重载
    )


