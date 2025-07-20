import sqlite3
import os
connection = sqlite3.connect('/home/vajor/OneDrive/sqlite/vajor.db')

path = r"/home/vajor/OneDrive/images/albumn"
favoritepath = r"/home/vajor/OneDrive/images/favorite"
girlfavpath = r"/home/vajor/OneDrive/images/girlfav"
girlspath = r"/home/vajor/OneDrive/images/girls"
previewpath = r"/home/vajor/OneDrive/images/preview"




institutions = {'尤果网':'尤果网','ugirls':'尤果网','果团网':'果团网','girlt':'果团网','喵糖映画':'喵糖映画',\
                'bololi':'波萝社','波萝社':'波萝社','xiuren':'秀人网','秀人网':'秀人网','mygril':'美媛馆','美媛馆':'美媛馆',\
                'youwu':'尤物馆','尤物馆':'尤物馆','imiss':'爱蜜社',"爱蜜社":'爱蜜社','蜜桃':'miitao蜜桃社','蜜桃社':'蜜桃社',\
                'uxing':'优星馆',"优星馆":"优星馆",'tukmo':'兔几盟','兔几盟':'兔几盟','feilin':'嗲囡囡','嗲囡囡':'嗲囡囡',\
                'mistar':'魅妍社','魅妍社':'魅妍社','wings':'影私荟','影私荟':'影私荟','leyuan':'星乐园','星乐园':'星乐园',\
                'mfstar':'模范学院','模范学院':'模范学院','huayan':'花の颜','花の颜':'花の颜','dkgirl':'御女郎',\
                '御女郎':'御女郎','candy':'网红馆','网红馆':'网红馆','partycat':'轰趴猫','轰趴猫':'轰趴猫','cosplay':'Cosplay',\
                'xgyw':'散图','micat':'猫萌榜','猫萌榜':'猫萌榜' ,'xingyan':'星颜社', '星颜社': '星颜社',\
                'xiaoyu':'画语界', '画语界':'画语界', 'youmi':'优蜜荟', '优蜜荟':'优蜜荟',\
                'Pure Media' : 'Pure Media'}
in_list=['黄色','白丝','户外','黑色','白色','粉色','吊带','浴室','蕾丝','翘臀','清纯','粉红','兔女郎','居家','红色','情趣','真空','女仆','情人节','护士',\
    '古装','沙滩','热裤', '海边','露背毛衣','丁字裤','奶油','短裙','旗袍','缕空','黑丝','霸气','美少女','比基尼','大海','灰色','连身裙',"半脱","蓝色",\
    '胶布',"美腿","薄纱","端午","民国","全裸",'日系','婚纱','连衣裙','胶带']
replace_list={'全脱':"全裸","乳":"美胸","胸":"美胸","和服":"和服","遮点":"遮点","胴体":"全裸","无内":"全裸","捆绑":"捆绑","警":"女警","JK":"JK","OL":"OL","短牛仔裤":"热裤",
        "三点式":"比基尼","学生装":"JK","合集":"合集","萝莉":"萝莉","剑道":"剑道","甜美":"甜美","运动":"运动","职场":"OL","秘书":"OL",
        "Cos":"cos","COS":"cos","cos":"cos",'屁沟':"裸臀","裸下半身":"裸臀","职业装":"OL","连体":"死库水",'黄':'黄色'}


girlname_dict = {'Yeha':'Yeha','yeha':'Yeha','ye ha':'Yeha', 'ye ha':'Yeha', '幼幼':'幼幼','Chunmomo':'蠢沫沫','蠢沫沫':'蠢沫沫',\
        '桜井宁宁':'桜井宁宁','Sakurai Ningning':'桜井宁宁','Chengzimiaoj':'橙子喵酱','媃柔':'媃柔','发条少女':'迷之呆梨',\
        'Rinaijiao':'日奈娇','晕崽':'晕崽', '鱼子酱Fish':'鱼子酱', '鱼子酱':'鱼子酱','迷之呆梨':'迷之呆梨',"谭小灵":"谭小灵","谭小灵(Tanxiaoling)":"谭小灵",\
        '白莉爱吃巧克力':'白莉爱吃巧克力','白莉':'白莉爱吃巧克力','小薯条':'小薯条','Blacqkl':'白莉爱吃巧克力', '袁圆':'袁圆','晚苏':'晚苏','晚苏susu':'晚苏',\
        '懒懒睡不醒':'懒懒睡不醒', '莱可Raika':'莱可Raika', '桃妖天':'桃妖夭', '蛋蛋宝':'蛋蛋宝','拍黄瓜':'拍黄瓜','麻布学妹':'麻布学妹'
        }


remove_list = ['Cosplaytele', 'cosplaytele', '4khd', '4KHD']
keywords_list = ['内购']



abandon_list = ['[JVID]','Dorasnow','[AI Generated]','Unknown Cosplayer cosplay','小海臀','[JP]','Aqua' \
                'Tokar 浵卡','Potato Godzilla', 'Natsuko夏夏子', 'Byoru', 'Atsuki', '唐兴'\
                '星澜是澜澜叫澜妹呀', '木之本果', 'Arty亚缇', '水淼aqua', '铃木美咲' ,'九言'\
                '璟乐','林星阑','诗诗kiki','妲己_Toxic', '陆萱萱', '梦心玥','[Shooting Star’s (Saku)]'\
                '王雨纯','Umeko J','胡桃猫','sarina kurokawa', 'Iori Sagara', 'Pyoncos', 'Ria Kurumi', 'Nina Rei']






keygirl_list = set(girlname_dict.values()) 
newgirls = os.listdir(girlspath)
newgirls = [os.path.splitext(filename)[0] for filename in newgirls]
keygirl_list = keygirl_list.union(newgirls)
keygirl_list = list(keygirl_list)
