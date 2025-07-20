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


response = session.get(url, proxies=proxies, headers=headers, verify=False, timeout=10)