import requests

def send_url_to_browser_service(url: str):
    endpoint = "http://localhost:5555/open"
    data = {"url": url}
    try:
        response = requests.post(endpoint, json=data)
        print("响应:", response.status_code, response.json())
    except Exception as e:
        print("请求失败:", str(e))

if __name__ == "__main__":
    # 在这里修改你要跳转的网址

    URL= "https://www.v2ph.com/album/ae4849mz.html?page=4&hl=zh-Hans"
    send_url_to_browser_service(URL)