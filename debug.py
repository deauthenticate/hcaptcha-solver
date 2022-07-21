import httpx, threading


def GetCaptcha():
    captchakey = httpx.post("http://185.61.137.160:8080/solvecaptcha", json={
    "site_key": "4c672d35-0701-42b2-88c3-78380b0db560",
    "site_url": "https://discord.com/",
    "proxy_url": ''
    }, timeout=None)
    print(captchakey.text)




for i in range(1):
    resp = threading.Thread(target=GetCaptcha).start()
