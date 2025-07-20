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
class ImageData(BaseModel):
    image: str
    liked: bool = None
    name: str
    girl: Optional[str] | None

class FormData(BaseModel):
    address: str
    albumn_no: str
    girlname: str
    albumn: str
    albumn_name: str

def sort_key(s):
    match = re.search(r'_([0-9]+)', s)
    if match:
        return int(match.group(1))
    match = re.search(r'([0-9]+)', s)
    if match:
        return int(match.group(1))
    return 0  # 如果没有找到匹配项，返回0

def process_infos(condition, website=None, date=None, girl=None, albumn=None, orderby=None, limit=None, exclude_girls=None):
    print(condition)
    print(date)
    cursor = connection.cursor()

    # 构建 SQL 查询
    sql = "SELECT ROWID, address, albumn, girlname, keywords, description, albumn, albumn_no, albumn_name,score, link, website FROM girl WHERE 1=1 AND website != 'xgmn'"
    if website:
        sql += f' AND website="{website}"'
    if date:
        sql += f' AND date LIKE "{date}%"'
    if girl:
        if isinstance(girl, str):  # 使用 isinstance 替代 type 检查
            sql += f' AND girlname="{girl}"'
        elif isinstance(girl, list):  # 处理列表情况
            # 将列表转换为安全的SQL IN子句
            girl_list = [f'"{g}"' for g in girl]  # 为每个名字加引号
            sql += f' AND girlname IN ({",".join(girl_list)})'
    if exclude_girls:
        exclude_list = [f'"{g}"' for g in exclude_girls]
        sql += f' AND girlname NOT IN ({",".join(exclude_list)})'
    if albumn:
        sql += f' AND albumn="{albumn}"'
    if condition:
        sql += f' AND {condition}'
    if orderby:
        sql += f' ORDER BY  {orderby} DESC '
    else:
        # 如果没有指定排序方式，默认按随机顺序排序
        sql += ' ORDER BY RANDOM()'
    if limit:
        sql += f' LIMIT {limit}'


    print("Executing SQL:", sql)

    # 执行查询
    cursor.execute(sql)
    result = cursor.fetchall()

    # 处理查询结果
    newinfos = []
    if result:
        for info in result:
            # print(info)
            rowid, address, albumn, name, keywords, description, albumn, albumn_no, albumn_name,score, link, website = info

            if name in abandon_list:
                continue
            newinfos.append({
                'address': address,
                'albumn': albumn,
                'albumn_name': albumn_name,
                'albumn_no': albumn_no,
                'name': name,
                'keywords': keywords,
                'description': description,
                'link':link,
                'website':website,
            })
    cursor.close()
    return newinfos

def main_condition():
    return "score >= 60"

def index_condition():
    return "score = 50"

def star_condition():
    return "score > 70"

@app.get("/user/{name}")
async def user_page(name: str):
    return JSONResponse(content={"User": name})

@app.get("/new")
async def new():
    return RedirectResponse(url='/')

@app.get("/")
@app.get("/today")
async def today(request: Request, offset: int = 0, find_left: bool = False, find_right: bool = False):
    print(keygirl_list)
    base_date = datetime.datetime.now().date()
    max_look_days = 300
    min_required = 1

    if not find_left and not find_right:
        final_date = base_date - datetime.timedelta(days=offset)
        final_date_str = final_date.strftime("%Y-%m-%d")
        keygirl_infos = process_infos(index_condition(), date=final_date_str, girl=keygirl_list, orderby="ROWID", limit=900)
        todayinfos = process_infos(index_condition(), date=final_date_str, exclude_girls=keygirl_list)
        return templates.TemplateResponse("xiutaku.html", {
            "request": request,
            "infos": todayinfos,
            "offset": offset,
            "delete_flag": True,
            "date": final_date_str,
            "keygirl_infos": keygirl_infos
        })

    step = -1 if find_left else 1
    look_count = 1
    final_offset = offset
    final_date_str = ""
    todayinfos = []
    keygirl_infos = []

    while look_count < max_look_days:
        candidate_offset = offset + step * look_count
        final_date = base_date - datetime.timedelta(days=candidate_offset)
        final_date_str = final_date.strftime("%Y-%m-%d")

        keygirl_infos = process_infos(index_condition(), date=final_date_str, girl=keygirl_list, orderby="ROWID", limit=90)
        todayinfos = process_infos(index_condition(), date=final_date_str, exclude_girls=keygirl_list)
        print(len(keygirl_infos))
        print("1111111111")
        if len(todayinfos) + len(keygirl_infos) >= min_required:
            final_offset = candidate_offset
            break

        look_count += 1

    if final_offset != offset:
        return RedirectResponse(url=f"/today?offset={final_offset}")
    return templates.TemplateResponse("xiutaku.html", {
        "request": request,
        "infos": todayinfos,
        "offset": final_offset,
        "delete_flag": True,
        "date": final_date_str,
        "keygirl_infos": keygirl_infos
    })

    
@app.get("/main")
async def main(request: Request):
    newinfos = process_infos(main_condition())
    return templates.TemplateResponse("xiutaku.html", {"request": request, "infos": newinfos, "delete_flag": True})

@app.post("/delete_infos")
async def delete_infos(request: Request, data: dict):
    infos = data['infos']
    print(infos)
    for info in infos:
        delete_path = os.path.join(path, info)
        cursor = connection.cursor()
        try:
            sql = f'UPDATE girl SET is_exist=0, score=0 WHERE address = "{info}" AND score = 50'
            # print("Executing SQL:", sql)
            cursor.execute(sql)
            connection.commit()
            try:
                shutil.rmtree(delete_path)
            except Exception as e:
                print(f"删除文件夹失败: {e}")
        finally:
            cursor.close()

    newinfos = process_infos(main_condition())
    return templates.TemplateResponse("xiutaku.html", {"request": request, "infos": newinfos})

@app.get("/")
async def index(request: Request):
    newinfos = process_infos(index_condition())
    return templates.TemplateResponse("xiutaku.html", {"request": request, "infos": newinfos,"delete_flag": True})

@app.get("/star")
async def star(request: Request):
    newinfos = process_infos(star_condition())
    return templates.TemplateResponse("xiutaku.html", {"request": request, "infos": newinfos})

@app.get("/girl/{girl}")
async def girl(request: Request, girl: str):
    infos = process_infos(main_condition(), girl=girl, orderby="score")
    recent_infos = process_infos(main_condition(), girl=girl, orderby="ROWID", limit = 3)
    print(recent_infos)
    return templates.TemplateResponse("xiutaku.html", {"request": request, "infos": infos,  "girl":girl, "recent_infos":recent_infos})

@app.get("/girlfav/{girl}")
async def girlfav(request: Request, girl: str):

    favorite_list = []
    final_girlfavpath = os.path.join(girlfavpath, girl)
    print(final_girlfavpath)
    for root, dirs, files in os.walk(final_girlfavpath):
        for file in files:
            file_path = os.path.join(root, file)
            # print(file_path)
            # print(favoritepath)
            file_path = file_path.replace(final_girlfavpath, '')
            file_path = file_path.strip(r'/')

            # print(file_path)
            favorite_list.append(file_path)
    # print(favorite_list)
    return templates.TemplateResponse("favorite.html", {"request": request,  "images": favorite_list,})

@app.get("/girls")
async def girls(request: Request):
    girls = [f.replace('.webp', '') for f in os.listdir(girlspath) if f.endswith(".webp")]
    print(girls)
    return templates.TemplateResponse("allgirls.html", {"request": request, "girls": girls})

@app.get("/albumn/{albumn}")
async def albumn(request: Request, albumn: str):
    newinfos = process_infos(main_condition(), albumn=albumn)
    return templates.TemplateResponse("xiutaku.html", {"request": request, "infos": newinfos})

@app.get("/randoalbumn")
async def randoalbumn():
    newinfos = process_infos(index_condition(),limit=1)
    one = random.choice(newinfos)
    print(one)
    address = one['address']
    return RedirectResponse(url=f'/xiutakugirl/{address}')

@app.get("/site/{website}")
async def get_website_info(request: Request, website: str):
    valid_websites = {"khd", "xgmn", "cosplaytele", "buondua", "xiutaku"}
    if website not in valid_websites:
        return {"error": "Invalid website"}
    
    newinfos = process_infos(index_condition(), website=website)
    return templates.TemplateResponse("xiutaku.html", {
        "request": request,
        "infos": newinfos,
        "delete_flag": True
    })

@app.get("/favorite")
async def favorite(request: Request):
    print('favorite')
    favorite_list = []
    for root, dirs, files in os.walk(favoritepath):
        for file in files:
            file_path = os.path.join(root, file)
            # print(file_path)
            # print(favoritepath)
            file_path = file_path.replace(favoritepath, '')
            file_path = file_path.strip(r'/')

            # print(file_path)
            favorite_list.append(file_path)
    # print(favorite_list)
    return templates.TemplateResponse("favorite.html", {"request": request,  "images": favorite_list,})

@app.get("/xiutakugirl/{name}")
async def xiutakugirl(request: Request, name: str, selected_image: str = Query(None), showtype: str = Query(None)):
    print(name)
    imagesdir = urllib.parse.unquote(name)
    if selected_image:
        print(selected_image)
        selected_image = os.path.join(name, selected_image)
    if showtype:
        print(showtype)
    else:
        showtype = 'albumn'
    cursor = connection.cursor()
    try:
        sql = 'SELECT albumn, girlname, keywords, description, albumn_no, albumn_name, score, link, website FROM girl WHERE address = ?;'
        cursor.execute(sql, (name,))
        result = cursor.fetchone()

        if result:
            albumn, girl, keywords, description, albumn_no, albumn_name, score, link, website = result

        imagesdir = os.path.join(path, name)
        # print(imagesdir)
        images = os.listdir(imagesdir)
        images = sorted(images, key=sort_key)  # 排序

        images = [(os.path.join(name, image), 1 if image.startswith("*") else 0) for image in images if not image.startswith('.')]  # 过滤隐藏文件
        # star_images = [image for image in images if  image.startswith('*')]  # 过滤隐藏文件

        # images = [(os.path.join(name, _), redis_connections['redphoto'].get(os.path.join(name, _))) for _ in images]
        # images = [(os.path.join(name, _), os.path.join(name, _)) for _ in images]

        # print(images)
        count = len(images)
        destination_web = f"{showtype}.html"
        print(destination_web)
        return templates.TemplateResponse(destination_web, {
            "request": request,
            "images": images,
            "girl": girl,
            "albumn": albumn,
            "albumn_no": albumn_no,
            "albumn_name": albumn_name,
            "name": name,
            "count": count,
            "keywords": keywords,
            "description": description,
            "selected_image": selected_image,
            "link": link,
            "website":website, 
        })
    finally:
        cursor.close()


@app.post("/like_image")
async def like_image(data: ImageData):
    print(ImageData)
    image = data.image
    name = data.name
    girl = data.girl
    print(image)
    print(name)
    print(path)
    first, last = image.split('/')
    if not last[0] == '*':
        last = '*' + last
        starimage = '/'.join([first, last])
        nostarlimage = image
        starpath = os.path.join(path, starimage)
        nostarpath = os.path.join(path, image)
    else:
        last = last[1:]
        nostarlimage = '/'.join([first, last])
        starimage = image
        nostarpath = os.path.join(path, nostarlimage)
        starpath = os.path.join(path, image)


    print(starpath, nostarpath)

    final_girlfavpath = os.path.join(girlfavpath, girl)

    if os.path.exists(starpath):
        os.rename(starpath, nostarpath)  
        favoriteimage = os.path.join(favoritepath, starimage)
        girlfavimage = os.path.join(final_girlfavpath, starimage)

        # remove 符号链接
        if os.path.exists(favoriteimage):  # 检查符号链接是否存在
            os.unlink(favoriteimage)  # 删除符号链接
        if os.path.exists(girlfavimage):  # 检查符号链接是否存在
            os.unlink(girlfavimage)  # 删除符号链接
    else:
        os.rename(nostarpath, starpath)  
        favoriteimage = os.path.join(favoritepath, starimage)
        favorite_dir = os.path.dirname(favoriteimage)
        os.makedirs(favorite_dir, exist_ok=True)

        girlfavimage = os.path.join(final_girlfavpath, starimage)
        girlfav_dir = os.path.dirname(girlfavimage)
        print(girlfav_dir)
        os.makedirs(girlfav_dir, exist_ok=True)
        print(girlfav_dir)

        # 替换 shutil.copy() 为创建符号链接
        # 如果目标文件已存在，先删除
        if os.path.exists(favoriteimage):
            os.remove(favoriteimage)
        os.symlink(starpath, favoriteimage)  # 创建符号链接

        if os.path.exists(girlfavimage):
            os.remove(girlfavimage)
        os.symlink(starpath, girlfavimage)  # 创建符号链接


    return JSONResponse(content={"status": "success", "message": f"Image '{image}' liked status set to liked by {name}"})

@app.post("/set_preview")
async def set_preview(data: ImageData):
    image = data.image
    name = data.name
    girl = data.girl
    source = f'{path}/{image}'
    destination = f'{previewpath}/{name}.webp'
    girlsdestination = f'{girlspath}/{girl}.webp'
    print(image)
    print(name)
    print(source)
    print(destination)
    shutil.copyfile(source, destination)
    shutil.copyfile(source, girlsdestination)
    # os.copy(f'{path}/{image}', f'{previewpath}/{image}')
    return JSONResponse(content={"status": "success", "message": f"Image '{image}' set to preview by {name}", "url": f"{name}.webp"})


@app.post("/delete_image")
async def delete_image(data: ImageData):
    image = data.image
    name = data.name
    first, last = image.split('/')
    last = '.' + last
    print(first, last)
    finalimage = '/'.join([first, last])
    realimage = os.path.join(path, image)
    realfinalimage = os.path.join(path, finalimage)
    os.rename(realimage, realfinalimage)
    return JSONResponse(content={"status": "success", "message": f"Image '{image}' deleted by {name}"})

@app.post("/rate_albumn")
async def rate_albumn(request: Request, album_id: str = Form(...), rating: int = Form(...)):
    cursor = connection.cursor()

    # 使用参数化查询来防止 SQL 注入
    sql = "UPDATE girl SET score = ? WHERE address = ?"
    cursor.execute(sql, (rating, album_id))
    print(album_id, rating)
    # 提交事务
    connection.commit()

    # 关闭游标和连接
    cursor.close()


@app.get("/respider")
async def respider(request: Request, url: str):
    # 定义所有要执行的命令（除了 xiutaku）
    commands = [
        ["/usr/bin/python3", "/home/vajor/OneDrive/spider/save.py",  url],
    ]
    print("i will serespiderarch")
    for cmd in commands:
        print(" ".join(cmd))
    # 异步执行所有命令
    async def run_command(cmd):
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return {
            "command": " ".join(cmd),
            "returncode": process.returncode,
            "stdout": stdout.decode() if stdout else "",
            "stderr": stderr.decode() if stderr else ""
        }
    
    # 并行执行所有命令
    try:
        results = await asyncio.gather(*[run_command(cmd) for cmd in commands])
        
        # 格式化返回结果
        response = {
            "status": "success",
            "results": {}
        }
        
        for result in results:
            param = result["command"].split()[-1]  # 获取命令中的参数
            response["results"][param] = {
                "output": result["stdout"] if result["returncode"] == 0 else "",
                "error": result["stderr"] if result["returncode"] != 0 else "",
                "success": result["returncode"] == 0
            }
            
        return response
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/search/{girl}")
async def search(request: Request, girl: str):
    # 定义所有要执行的命令（除了 xiutaku）
    commands = [
        ["/usr/bin/python3", "/home/vajor/OneDrive/spider/girls.py", "4khd", girl],
        ["/usr/bin/python3", "/home/vajor/OneDrive/spider/girls.py", "cosplaytele", girl],
        ["/usr/bin/python3", "/home/vajor/OneDrive/spider/girls.py", "buondua", girl],
        ["/usr/bin/python3", "/home/vajor/OneDrive/spider/girls.py", "xiutaku", girl]
    ]
    print("i will search")
    for cmd in commands:
        print(" ".join(cmd))
    # 异步执行所有命令
    async def run_command(cmd):
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return {
            "command": " ".join(cmd),
            "returncode": process.returncode,
            "stdout": stdout.decode() if stdout else "",
            "stderr": stderr.decode() if stderr else ""
        }
    
    # 并行执行所有命令
    try:
        results = await asyncio.gather(*[run_command(cmd) for cmd in commands])
        
        # 格式化返回结果
        response = {
            "status": "success",
            "results": {}
        }
        
        for result in results:
            param = result["command"].split()[-1]  # 获取命令中的参数
            response["results"][param] = {
                "output": result["stdout"] if result["returncode"] == 0 else "",
                "error": result["stderr"] if result["returncode"] != 0 else "",
                "success": result["returncode"] == 0
            }
            
        return response
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/change_info")
async def change_info(
    address: str = Form(...),
    albumn_no: str = Form(...),
    girlname: str = Form(...),
    albumn: str = Form(...),
    albumn_name: str = Form(...)
):
    cursor = connection.cursor()
    # 使用参数化查询来防止 SQL 注入
    sql = """
    UPDATE girl
    SET albumn_no = ?, girlname = ?, albumn = ?, albumn_name = ?
    WHERE address = ?
    """
    cursor.execute(sql, (
        albumn_no,
        girlname,
        albumn,
        albumn_name,
        address
    ))
    # 提交事务
    connection.commit()
    cursor.close()
    return JSONResponse(content={"message": "更新成功"})

# 新增保存信息的路由
@app.post("/save_info")
async def save_info(
    title: str = Form(...),
    url: str = Form(...),
    public: str = Form(...),
    public_no: str = Form(...),
    public_name: str = Form(...),
    girlname: str = Form(...),
    keywords: str = Form(...),
    description: str = Form(...),
    website: str = Form(...)
):


    database_save(title, url, public, public_no, public_name, girlname, keywords, description, website)
    
    return JSONResponse(content={"message": "保存成功"})



if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="::", port=3334)
    uvicorn.run(
        "girls:app",  # 文件名:FastAPI实例名
        host="0.0.0.0",
        port=4444,
        reload=True  # 启用自动重载
    )


