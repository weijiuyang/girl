
from oneapi import *
from config import *
import datetime

def ai_key(title):
    public_no = None

    for one in remove_list :
        title = title.replace(one, '')
    # while True:
    prompt = """
            根据用户传入的信息提取出来下面摄影作品的出品方,作品编号,作品名字,人物名字。给出json字符串,键为public, number, bookname,  personname,
            举例子:Coser@橙子喵酱: 穹妹旗袍 (23 photos) 结果是 {"public":"Coser","public_number":,"personname":"橙子喵酱","bookname":"穹妹旗袍"},
            Umeko J cosplay Ahri – League of Legends “109 photos,10 gifs and 9 videos” 结果是 {"public":"cosplay","public_number":0,"personname":"Umeko J","bookname":"Ahri – League of Legends"},
            Lingyu69  浴室情挑[810MB-119photos] 结果是 {"public":"", "public_number" :0, "personname":"Lingyu69", "bookname":"浴室情挑"},
            Mona (모나): Special Nude Art No.01 (74 photos) 结果是 {"public":"", "public_number" :1, "personname":"Mona", "bookname":"Special Nude Art"},
            鱼子酱Fish – Kyoto Creed “145 photos” 结果是 {"public":"", "public_number" :0, "personname":"鱼子酱", "bookname":"Kyoto Creed"},
            OrangePic Vol.4 – Web Pictorial[435MB-62photos] 结果是{"public":"OrangePic", "public_number" :4, "personname":"", "bookname":"Web Pictorial"},
            [XiuRen秀人网]第9032期拍黄瓜写真 结果是 {"public":"XiuRen秀人网", "public_number" :9032, "personname":"拍黄瓜", "bookname":""},
            Coser@爆机少女喵小吉 (Nekokoyoshi): 密室监禁 (41 photos),结果是 {"public":"Coser", "public_number" :0, "personname":"爆机少女喵小吉", "bookname":"密室监禁"},
            """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": title}
    ]
    # content = get_completion(messages)
    content = get_album_info(messages)


    # public, public_no, public_name, girlname, keywords
    if not content.public:
        content.public = content.personname
    print(content)
    
    return content.public, content.public_number, content.personname, content.bookname, ''




def database_save(title, link, public, public_no, public_name, girlname, keywords, description, website):
    dirs = os.path.join(path, title)
    os.makedirs(dirs, exist_ok = True)
    nowdate = datetime.datetime.now().date().strftime("%Y%m%d")
    if not girlname:
        girlname = 'unknown'

    print(f'title: {title}')
    print(f'link: {link}')
    print(f'public: {public}')
    print(f'public_no: {public_no}')
    print(f'public_name: {public_name}')
    print(f'girlname: {girlname}')
    print(f'girlname type: {type(girlname)}')

    if isinstance(girlname, list):  # 使用 isinstance 代替 type 比较
        girlname = ','.join(girlname)
    print(f'girlname: {girlname}')
    
    print(f'keywords: {keywords}')
    print(f'description: {description}')
    print(f'website: {website}')
    if isinstance(keywords, (list, tuple)):
        keywords_str = ','.join(keywords)
    else:
        keywords_str = str(keywords) 
        keywords_str = ''
    sql = """
        INSERT OR REPLACE INTO girl (address, link, girlname, keywords, albumn, albumn_no,albumn_name,  description, date, website, score, is_exist)
        VALUES (?, ?, ?, ?, ?, ?, ?,?, ?, ?, 50, 1)
    """
    cursor = connection.cursor()
    cursor.execute(sql, (
        title, 
        link, 
        girlname, 
        keywords_str, 
        public, 
        public_no, 
        public_name,
        description, 
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
        website
    ))
    connection.commit()