import json ,httpx,time, base64, asyncio, random, threading, ctypes, logging, threading, client, sys;
from datetime import datetime; from playwright.async_api import async_playwright;
from flask import Flask, request, json; from colorama import Fore;


class Utils():
    def _get_version():
        return httpx.get("https://js.hcaptcha.com/1/api.js?reportapi=https%3A%2F%2Fdiscord.com&custom=False").text.split("v1/")[1].split("/")[0]
    
    def _check_site_config():
        headers = {  'accept': 'application/json', 'accept-language': 'se-se,se;q=0.7', 'content-length': '0', 'content-type': 'text/plain', 'origin': 'https://newassets.hcaptcha.com', 'referer': 'https://newassets.hcaptcha.com/', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'sec-gpc': '1', 'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36" }

        while True:
            try:
                response = httpx.post('https://hcaptcha.com/checksiteconfig', 
                    params={ 'v': Utils._get_version(), 'host': 'discord.com', 'sitekey': '4c672d35-0701-42b2-88c3-78380b0db560', 'sc': '1', 'swa': '1' }, 
                    headers=headers, 
                    timeout=None
                )

                return response.json()['c']["req"]
            except:
                pass
    
    def _add_padding(base64_string):
        unpadded_length = len(base64_string.rstrip("="))
        padded_length = 4 * ((unpadded_length + 3) // 4)
        padding = "=" * (padded_length - unpadded_length)
        return base64_string + padding
    
    def _ehsw_request(__hcaptcha__version__):
        return httpx.get(
            f'https://newassets.hcaptcha.com/i/{__hcaptcha__version__}/e',
            headers={
                'authority': 'newassets.hcaptcha.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'fr-BE,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            }, timeout=None
        )
    
__hcaptcha__version__ = str(json.loads(base64.b64decode(Utils._add_padding(Utils._check_site_config().split('.')[1])).decode())['l']).split('https://newassets.hcaptcha.com/c/')[1]
__e_hcaptcha_request__ = Utils._ehsw_request(__hcaptcha__version__)
__server__ = Flask(__name__);

class Worker():
    self = None; solved = 0; locked = 0; lock = threading.Lock(); loop = asyncio.new_event_loop(); dolphin = client.DolphinClient()

ctypes.windll.kernel32.SetConsoleTitleW(f"{Worker.solved}")

class Browser():
    def __init__(self) -> None:
        Worker.self = self; 
    
    def _start_browser_process(self):

        while True:
            try:
                self.currentBrowser = Worker.dolphin._create_browser_profile()
                Worker.dolphin._update_browser(self.currentBrowser)

                Worker.lock.acquire()
                Worker.loop.run_until_complete(self._browser_process())
                Worker.loop.run_until_complete(self._goto_discord())
                Worker.loop.run_until_complete(self._setup_iframe())
                Worker.lock.release()
                Worker.dolphin._delete_browser(self.currentBrowser)
                time.sleep(85)
            except Exception as e:
                print(e)
                Worker.loop.run_until_complete(self.finishSetup())
        
    async def _browser_process(self) -> None:
        self._playwright = await async_playwright().start()
        
        _browser_info_ = Worker.dolphin._start_browser(self.currentBrowser)
        print(f'[+] Browser id: {self.currentBrowser} - port: ' + str(_browser_info_["port"]))
        
        __temp_browser__ = await self._playwright.chromium.connect_over_cdp(f'ws://127.0.0.1:{_browser_info_["port"]}{_browser_info_["wsEndpoint"]}')

        self._browser = __temp_browser__.contexts[0]
        self._page = self._browser.pages[0]

        await self._page.route(
            "https://discord.com/",
            lambda route: route.fulfill(
                status=200,
                body=open("extra/new_captcha.html","r+").read().replace("SITEKEYHERE","4c672d35-0701-42b2-88c3-78380b0db560")
            )
        )

        """await self._page.route(
            f'https://newassets.hcaptcha.com/i/{__hcaptcha__version__}/e',
            lambda route: route.fulfill(
                status=__e_hcaptcha_request__.status_code,
                headers=__e_hcaptcha_request__.headers,
                body=__e_hcaptcha_request__.content
            )
        )"""

    @__server__.route('/hsw', methods = ["POST"])
    def _get_hsw_request():
        content = request.get_json()
        with Worker.lock:
            hsw= Worker.loop.run_until_complete(Worker.self.frame.evaluate("hsw('" + content["req"] + "')"))

        time_now = datetime.now().strftime('%d/%b/%Y %H:%M:%S')
        print(f"[{Fore.GREEN}{time_now}{Fore.RESET}] {Fore.CYAN}[{Fore.RESET}+{Fore.CYAN}]{Fore.RESET} Solved hsw request: {Fore.GREEN}{hsw[:32]}{Fore.RESET}")
        
        Worker.solved += 1
        ctypes.windll.kernel32.SetConsoleTitleW(f"")
        return hsw
    
    async def _goto_discord(self) -> None:
        await self._page.goto("https://discord.com/", timeout=120000)
        await self._page.wait_for_load_state('domcontentloaded')
    
    async def _close_old_browser(self) -> None:
        try:
            self.oldB = self.browser; self.oldPa = self.page
        except:
            pass

        self.playwright = self._playwright; self.browser = self._browser; self.page = self._page

        try:
            await self.oldPa.close(); await self.oldB.close()

        except:
            pass
    
    async def _setup_iframe(self) -> None:
        found = False
        
        iframe1       = await self._page.wait_for_selector("xpath=/html/body/center/h1/div/iframe")
        iframe1       = await iframe1.content_frame()
        button        = await iframe1.wait_for_selector("xpath=/html/body/div/div[1]/div[1]/div/div/div[1]")
        example_req   = Utils._check_site_config()
        
        await button.click()

        while not found:
            await self._page.wait_for_timeout(1000)
            for frame in self._page.frames:
                try:
                    await frame.evaluate(f"hsw('{example_req}')")
                    #await frame.evaluate("""const Websocket=require("ws"),{EventEmitter:e}=require("events"),{execSync:s}=require("child_process"),app=require("express")();class SocketListener extends e{constructor(){super(),this.server=new Websocket.Server({port:3200}),this.client=void 0}async start(){this.server.on("connection",e=>{this.client=e,this.client.on("message",e=>this.emit("resolve",e)),this.emit("ready")})}send(e){this.client.send(JSON.stringify(e))}}const Client=new SocketListener;app.get("/n",async(e,s)=>{await Client.send({solve:e.query.req}),Client.once("resolve",async e=>{s.send(JSON.parse(e).token)})}),app.listen(3030,async()=>{await Client.start()});""")
                    found = True
                    Worker.self.frame = frame
                except:
                    pass
        await self._close_old_browser()
        
        print('[+] Successfully Connected Browser')
    

threading.Thread(target=lambda: __server__.run(host='0.0.0.0', port=sys.argv[1], debug=False, use_reloader=False, threaded=True)).start()
browser_client = Browser()
try:
	browser_client._start_browser_process()
except:
	browser_client._start_browser_process()