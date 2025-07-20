from fastapi import FastAPI, HTTPException, Request, Form, Depends, Query
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
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

# V2PH 下载表单页面
@app.get("/v2ph_form", response_class=HTMLResponse)
async def v2ph_form(request: Request):
    return templates.TemplateResponse("v2ph.html", {"request": request})


# V2PH 表单提交接口
@app.post("/submit_v2ph")
async def submit_v2ph(request: Request, url: str = Form(...), cookie: Optional[str] = Form(None)):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Cookie": cookie or "frontend=51b5e210fe57889b68dafc0ad4460b71; frontend-rmu=R%2BEXGOuKte0uolfGJL%2BV15F76CZmnQ%3D%3D; frontend-rmt=Uu63tB%2FQbSzgzudPwlkRMQCcq9LiQgm1V8BaWsTDlb8lqCIgyHsyDxn5CTk0ag8k"
    }
    try:
        resp = requests.get(url, headers=headers, verify=False, timeout=15)
        if resp.status_code != 200:
            raise Exception(f"无法抓取 HTML，状态码：{resp.status_code}")
        html = resp.text
        # 构造模拟 Request 对象调用 download_v2ph
        return await download_v2ph_data({
            "html": html,
            "url": url,
            "cookie": headers["Cookie"],
            "user_agent": headers["User-Agent"],
            "title": url.split("/")[-1].split(".")[0]
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


async def download_v2ph_data(payload: dict):
    try:
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
            "Cookie": "frontend=51b5e210fe57889b68dafc0ad4460b71; frontend-rmu=R%2BEXGOuKte0uolfGJL%2BV15F76CZmnQ%3D%3D; frontend-rmt=Uu63tB%2FQbSzgzudPwlkRMQCcq9LiQgm1V8BaWsTDlb8lqCIgyHsyDxn5CTk0ag8k; _ga_170M3FX3HZ=GS2.1.s1750330712$o5$g1$t1750330719$j53$l0$h0; _ga=GA1.2.170908555.1749708166; _gid=GA1.2.919017545.1750330720; _gat_UA-140713725-1=1"
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
