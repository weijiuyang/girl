import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import *

# print('favorite')
favorite_list = []
for root, dirs, files in os.walk(favoritepath):
    for file in files:
        file_path = os.path.join(root, file)
        # print(file_path)
        # print(favoritepath)
        ori_path = file_path
        file_path = file_path.replace(favoritepath, '')
        file_path = file_path.strip(r'/')

        # print(file_path)
        favorite_list.append(file_path)
        if not os.path.exists(os.path.join(path, file_path)):
            print(os.path.join(path, file_path))
            print(ori_path)
            os.remove(ori_path)
            # exit()

    # return templates.TemplateResponse("favorite.html", {"request": request,  "images": favorite_list,})