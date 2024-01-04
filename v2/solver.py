import tls_client, json, requests
import time, random, base64
import numpy as np, os, httpx, re
from datetime import datetime
from colorama import Fore;
from hashlib import sha1; import enum
import io

database = {}; dup = [];
with open('scraped.csv', 'r+') as w:
    answers = w.read().splitlines()
    for i in answers:
        if i not in dup: 
            dup.append(i);
            try:
                database[i.split(':')[0].strip()] = i.split(':')[1].strip();
            except:
                pass
        else:
            pass
        

print(len(dup))

class Logger():
    def _log(text):
        time_now = datetime.now().strftime("%H:%M:%S")
        print(f'[{Fore.LIGHTBLACK_EX}{time_now}{Fore.RESET}] {text}')

hcaptchaApiVersion = requests.get('https://hcaptcha.com/1/api.js?render=explicit&onload=hcaptchaOnLoad', headers={
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
}).text.split('assetUrl:"https://newassets.hcaptcha.com/captcha/v1/')[1].split('/')[0]


class CaptchaType(enum.Enum):
    MULTIPLE_CHOICE = "image_label_multiple_choice"
    BINARY = "image_label_binary"
    TEXT = "text_free_entry"

class CaptchaTask:
        def __init__(self, hc, task):
            self.hcaptcha_instance = hc
            self.task_id = task["task_key"]
            if hc.get_type() == CaptchaType.TEXT:
                self.text = task["datapoint_text"]["nl"]
            else:
                self.uri = task["datapoint_uri"]

        def answer(self, answer):
            if isinstance(answer, bool):
                self.hcaptcha_instance.answers[self.task_id] = {
                    True: "true",
                    False: "false",
                }.get(answer)
            else:
                self.hcaptcha_instance.answers[self.task_id] = answer

        def get(self, as_bytesio: bool = False):
            if self.hcaptcha_instance.get_type() == CaptchaType.TEXT:
                return self.text
            else:
                r = requests.get(self.uri)
                return io.BytesIO(r.content) if as_bytesio else r.content



class Solver():
    def __init__(self, session:tls_client.Session, siteKey:str, siteUrl:str, rqData : str = None) -> None:
        self.debug = False;
        self.answers = {}

        #Requests
        self.session = session
        self.oldHeaders = self.session.headers
        self.session.headers = {
            'authority': 'hcaptcha.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'text/plain',
            'origin': 'https://newassets.hcaptcha.com',
            'referer': 'https://newassets.hcaptcha.com/',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        }

        self.siteKey = siteKey
        self.siteUrl = siteUrl

        self.log(f'Solving Captcha, SiteKey: {self.siteKey} | SiteUrl: {self.siteUrl}')
        self.log(f'Hcaptcha Api Version: {hcaptchaApiVersion}')     

        self.hsw:str = None
        self.captchaKey:str = None
        self.question:str = None

        self.proofData:dict = None
        self.tasklist:dict = None
        self.solution:dict = None
        self.rqData:str = rqData
        self.sed = False
    

    def log(self, txt:str) -> None:
        if self.debug: print(txt)


    def getHsw(self) -> str:

        # return requests.post(
        #     f"http://45.133.74.49:{random.choice(['8484','9898','9999','9888'])}/hsw",
        #     json={
        #         "req": self.proofData['req']
        #     }
        # ).text
        port = random.choice(['1337', '9534'])
        return requests.post(f"http://83.143.112.33:{port}/hsw", json={"req": self.proofData['req']}).text



    def mouse_movement(self,size:int=50):
        x_movements = np.random.randint(15, 450, size=size)
        y_movements = np.random.randint(15, 450, size=size)
        times = np.round(time.time(), decimals=0)
        times_list = [times] * len(x_movements)
        movement = np.column_stack((x_movements, y_movements, times_list))
        return movement.tolist()

    def checkSiteConfig(self) -> dict:
        return self.session.post(
            'https://hcaptcha.com/checksiteconfig',
            params={
                'v': hcaptchaApiVersion,
                'host': self.siteUrl,
                'sitekey': self.siteKey,
                'sc': '1',
                'swa': '1',
            }
        ).json()
    
    def getCaptcha(self) -> dict:
        self.session.headers['content-type'] = "application/x-www-form-urlencoded"
        payload = {
                'v': hcaptchaApiVersion,
                'sitekey': self.siteKey,
                'host': self.siteUrl,
                'hl': 'nl',
                'motionData': '{"st":1701275206255,"mm":[[52,36,1701275206706]],"mm-mp":0,"md":[[52,36,1701275206706]],"md-mp":0,"mu":[[52,36,1701275206743]],"mu-mp":0,"v":1,"topLevel":{"st":1701275204896,"sc":{"availWidth":1366,"availHeight":728,"width":1366,"height":768,"colorDepth":24,"pixelDepth":24,"availLeft":0,"availTop":0,"onchange":null,"isExtended":false},"nv":{"vendorSub":"","productSub":"20030107","vendor":"Google Inc.","maxTouchPoints":0,"scheduling":{},"userActivation":{},"doNotTrack":null,"geolocation":{},"connection":{},"pdfViewerEnabled":true,"webkitTemporaryStorage":{},"hardwareConcurrency":4,"cookieEnabled":true,"appCodeName":"Mozilla","appName":"Netscape","appVersion":"5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36","platform":"Win32","product":"Gecko","userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36","language":"en-US","languages":["en-US"],"onLine":true,"webdriver":false,"deprecatedRunAdAuctionEnforcesKAnonymity":false,"bluetooth":{},"clipboard":{},"credentials":{},"keyboard":{},"managed":{},"mediaDevices":{},"storage":{},"serviceWorker":{},"virtualKeyboard":{},"wakeLock":{},"deviceMemory":8,"ink":{},"hid":{},"locks":{},"gpu":{},"mediaCapabilities":{},"mediaSession":{},"permissions":{},"presentation":{},"usb":{},"xr":{},"serial":{},"windowControlsOverlay":{},"userAgentData":{"brands":[{"brand":"Google Chrome","version":"119"},{"brand":"Chromium","version":"119"},{"brand":"Not?A_Brand","version":"24"}],"mobile":false,"platform":"Windows"},"plugins":["internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer"]},"dr":"https://www.google.com/","inv":false,"exec":false,"wn":[[624,825,0.75,1701275204897]],"wn-mp":0,"xy":[[0,0,1,1701275204897]],"xy-mp":0,"mm":[[617,285,1701275205631],[594,290,1701275205647],[558,297,1701275205670],[538,302,1701275205686],[524,306,1701275205702],[510,310,1701275205718],[496,313,1701275205734],[478,317,1701275205750],[461,321,1701275205766],[325,381,1701275206247],[364,382,1701275206270],[390,384,1701275206286],[413,384,1701275206302],[430,384,1701275206318],[436,384,1701275206374],[436,382,1701275206398],[426,377,1701275206414]],"mm-mp":24.46875},"session":[],"widgetList":["0pnjp6w7k2ej"],"widgetId":"0pnjp6w7k2ej","href":"https://discord.com/","prev":{"escaped":false,"passed":false,"expiredChallenge":false,"expiredResponse":false}}'.replace("16956548", str(round(datetime.now().timestamp()))[:8]).replace('mmdata', str(self.mouse_movement())),
                'n': self.hsw,
                'c': json.dumps(self.proofData),
                
        }
        payload["a11y_tfe"] = "true"

        if self.rqData != None:
            payload['rqdata'] = self.rqData
        response = self.session.post(
            f'https://hcaptcha.com/getcaptcha/{self.siteKey}',
            data=payload
        ).json()

        
        return response
    
    
    def postCaptcha(self) -> dict:
        self.session.headers.update({
            'accept': '*/*',
            'content-type': 'application/json;charset=UTF-8'
        })

        return self.session.post(
            f'https://hcaptcha.com/checkcaptcha/{self.siteKey}/{self.captchaKey}',
            json={
                'v': hcaptchaApiVersion,
                'job_mode': self.captcha['request_type'],
                'answers': self.answers,
                'serverdomain': self.siteUrl,
                'sitekey': self.siteKey,
                'motionData': '{"st":1700933492828,"dct":1700933492828,"mm":[[14,296,1700933493543],[81,281,1700933493566],[129,272,1700933493582],[211,256,1700933493606],[305,238,1700933493629],[367,216,1700933493646],[377,5,1700933494798],[338,54,1700933494814],[305,102,1700933494830],[275,141,1700933494846],[253,169,1700933494862],[235,188,1700933494878],[225,202,1700933494894],[217,212,1700933494910],[213,217,1700933494926],[211,221,1700933494942],[207,225,1700933494965],[207,228,1700933495254],[207,232,1700933495270],[207,236,1700933495286],[207,240,1700933495302],[207,248,1700933495318],[205,253,1700933495334],[203,257,1700933495350],[201,258,1700933495366],[199,260,1700933495446],[195,260,1700933495462],[190,256,1700933495478],[187,249,1700933495494],[183,241,1700933495510],[183,229,1700933495534],[183,221,1700933495550],[183,209,1700933495574],[183,202,1700933495590],[183,194,1700933495606],[183,188,1700933495622],[185,185,1700933495638],[186,186,1700933495822],[189,201,1700933495838],[193,228,1700933495854],[198,258,1700933495870],[207,313,1700933495894],[217,344,1700933495910],[223,368,1700933495926],[233,388,1700933495942],[237,405,1700933495958],[246,422,1700933495974],[253,437,1700933495990],[261,450,1700933496006],[269,460,1700933496022],[274,466,1700933496038],[278,472,1700933496062],[281,473,1700933496110],[281,476,1700933496374],[285,481,1700933496390],[285,492,1700933496414],[285,504,1700933496438],[285,514,1700933496454],[289,526,1700933496470],[293,536,1700933496486],[297,548,1700933496511],[302,557,1700933496534],[305,561,1700933496550],[306,565,1700933496566],[309,569,1700933496582],[310,573,1700933496598],[313,580,1700933496622],[317,584,1700933496638],[317,585,1700933496654],[319,586,1700933496670],[323,588,1700933496710],[327,588,1700933496750],[329,588,1700933496782],[331,588,1700933496950],[333,584,1700933496976],[335,578,1700933497005],[337,578,1700933497038],[339,576,1700933497086],[341,576,1700933497118],[343,574,1700933497150],[345,572,1700933497518],[346,566,1700933497541],[346,558,1700933497557],[349,544,1700933497574],[349,502,1700933497598],[366,420,1700933497630],[395,329,1700933497654]],"mm-mp":24.32544378698226,"md":[[185,185,1700933495703],[281,473,1700933496207],[343,574,1700933497255]],"md-mp":776,"mu":[[185,185,1700933495774],[281,473,1700933496285],[343,574,1700933497333]],"mu-mp":779.5,"topLevel":{"st":1700933474365,"sc":{"availWidth":1366,"availHeight":728,"width":1366,"height":768,"colorDepth":24,"pixelDepth":24,"availLeft":0,"availTop":0,"onchange":null,"isExtended":false},"nv":{"vendorSub":"","productSub":"20030107","vendor":"Google Inc.","maxTouchPoints":0,"scheduling":{},"userActivation":{},"doNotTrack":null,"geolocation":{},"connection":{},"pdfViewerEnabled":true,"webkitTemporaryStorage":{},"hardwareConcurrency":4,"cookieEnabled":true,"appCodeName":"Mozilla","appName":"Netscape","appVersion":"5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36","platform":"Win32","product":"Gecko","userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36","language":"en-US","languages":["en-US"],"onLine":true,"webdriver":false,"deprecatedRunAdAuctionEnforcesKAnonymity":false,"bluetooth":{},"clipboard":{},"credentials":{},"keyboard":{},"managed":{},"mediaDevices":{},"storage":{},"serviceWorker":{},"virtualKeyboard":{},"wakeLock":{},"deviceMemory":8,"ink":{},"hid":{},"locks":{},"gpu":{},"mediaCapabilities":{},"mediaSession":{},"permissions":{},"presentation":{},"usb":{},"xr":{},"serial":{},"windowControlsOverlay":{},"userAgentData":{"brands":[{"brand":"Google Chrome","version":"119"},{"brand":"Chromium","version":"119"},{"brand":"Not?A_Brand","version":"24"}],"mobile":false,"platform":"Windows"},"plugins":["internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer"]},"dr":"","inv":false,"exec":false,"wn":[],"wn-mp":0,"xy":[],"xy-mp":0,"mm":[[152,514,1700933482406],[149,514,1700933483526],[145,514,1700933483566],[144,514,1700933483646],[141,514,1700933483774],[140,514,1700933483846],[137,514,1700933483862],[136,513,1700933483886],[132,512,1700933483902],[128,512,1700933483918],[124,512,1700933483934],[118,512,1700933483950],[110,512,1700933483966],[104,512,1700933483982],[97,512,1700933484006],[100,512,1700933484126],[116,513,1700933484142],[148,517,1700933484158],[189,518,1700933484174],[233,518,1700933484190],[252,518,1700933484566],[218,521,1700933484582],[184,522,1700933484598],[150,522,1700933484614],[125,522,1700933484630],[108,522,1700933484646],[96,522,1700933484662],[84,525,1700933484678],[77,529,1700933484694],[69,533,1700933484710],[61,536,1700933484726],[54,538,1700933484742],[49,538,1700933484758],[44,538,1700933484774],[40,538,1700933484790],[33,538,1700933484862],[32,538,1700933484886],[28,538,1700933484902],[25,538,1700933484935],[24,538,1700933484974],[21,538,1700933484998],[20,538,1700933485134],[17,538,1700933485166],[16,538,1700933485190],[13,538,1700933485214],[12,538,1700933485326],[9,537,1700933485342],[8,537,1700933485358],[5,536,1700933485374],[4,536,1700933485470],[1,536,1700933485542],[0,533,1700933485566],[0,532,1700933485758],[0,529,1700933485950],[0,528,1700933486142],[1,525,1700933486550],[10,525,1700933486574],[24,525,1700933486590],[50,525,1700933486613],[74,525,1700933486629],[102,526,1700933486646],[150,524,1700933486670],[208,516,1700933486694],[249,506,1700933486710],[296,498,1700933486726],[118,473,1700933488022],[86,454,1700933488038],[60,441,1700933488054],[44,432,1700933488070],[37,428,1700933488086],[38,428,1700933488198],[57,429,1700933488215],[106,442,1700933488238],[150,449,1700933488254],[193,460,1700933488271],[258,480,1700933488294],[438,461,1700933488678],[486,428,1700933488694],[541,389,1700933488710],[597,346,1700933488726],[653,298,1700933488742],[710,252,1700933488758],[774,205,1700933488774],[804,96,1700933489611],[746,157,1700933489630],[694,198,1700933489646],[641,237,1700933489662],[586,269,1700933489679],[514,309,1700933489702],[477,333,1700933489718],[445,354,1700933489734],[420,373,1700933489750],[397,393,1700933489766],[373,409,1700933489782],[350,426,1700933489798],[329,445,1700933489814],[305,465,1700933489830],[250,506,1700933489886],[244,509,1700933489910],[242,512,1700933489926],[240,513,1700933489942],[238,516,1700933489958],[234,520,1700933489974],[230,525,1700933489990],[230,530,1700933490006],[229,533,1700933490774],[226,533,1700933490791],[225,534,1700933490814],[222,534,1700933490838],[218,533,1700933490854],[217,532,1700933490870],[214,529,1700933491006],[213,528,1700933491158],[210,528,1700933491206],[140,494,1700933491638],[118,486,1700933491654],[96,478,1700933491670],[77,473,1700933491686],[62,472,1700933491702],[53,472,1700933491718],[58,472,1700933491830],[82,473,1700933491846],[121,481,1700933491862],[168,489,1700933491878],[222,500,1700933491894],[281,510,1700933491911],[250,517,1700933492310],[228,517,1700933492326],[209,517,1700933492342],[192,512,1700933492358],[181,508,1700933492374],[173,504,1700933492390],[168,501,1700933492406],[166,501,1700933492438],[164,501,1700933492454],[160,501,1700933492478],[158,501,1700933492494],[156,501,1700933492534],[154,501,1700933492550],[152,500,1700933492574],[150,500,1700933492678],[152,501,1700933493414],[158,508,1700933493430],[169,513,1700933493446],[182,521,1700933493462],[202,524,1700933493478],[225,525,1700933493494],[254,521,1700933493510],[288,513,1700933493526],[328,505,1700933493542],[738,397,1700933493662],[794,360,1700933493678],[802,88,1700933494755],[750,142,1700933494774],[710,189,1700933494790]],"mm-mp":53.14173228346457,"md":[[97,512,1700933484014],[0,528,1700933486198],[37,428,1700933488110],[50,472,1700933491742]],"md-mp":2692,"mu":[[97,512,1700933484086],[46,428,1700933488206],[50,472,1700933491805]],"mu-mp":3578.3333333333335},"v":1}'.replace("1683111", str(round(datetime.now().timestamp()))[:7]).replace('mmdata', str(self.mouse_movement())).replace("md_data__",str(self.mouse_movement(size=5))),
                'n': self.hsw,
                'c': json.dumps(self.proofData)
            },
        ).json()
    
    def get_task_list(self):
        return [CaptchaTask(self, x) for x in self.captcha["tasklist"]]
    
    def answer2(self):
        tasks = self.get_task_list()
        #print(tasks)
        answers = []
        for x in tasks:
            answer = random.choice(["ja", "nee"])
            if found := database.get(sha1(x.text.encode()).hexdigest()):
                answer = found
            
            x.answer({"text": answer})
            answers.append([x.text, answer])
        
        self.textanswers = answers
        #print(self.answers)
        
    def get_type(self, e=True):
        try:
            return (
                CaptchaType(self.captcha["request_type"])
                if e
                else self.captcha["request_type"]
            )
        except Exception:
            return self.captcha["request_type"]



    def solveCaptcha(self) -> str:
        self.proofData = self.checkSiteConfig()
        if self.proofData['pass'] != True:
            self.log('Failed Check Site Config')
            return None
        self.proofData = self.proofData['c']
        self.log('Passed Check Site Config')

        started = time.time()

        self.hsw = self.getHsw()
        self.captcha = self.getCaptcha()
        
        if "generated_pass_UUID" in self.captcha:
            self.session.headers = self.oldHeaders
            self.log(f'Solved Captcha: {self.captcha["generated_pass_UUID"][:20]}')
            return self.captcha['generated_pass_UUID']
        
        if "key" not in self.captcha:
            self.log(f'Failed Captcha: {self.captcha}')
            self.session.headers = self.oldHeaders
            return None

        self.captchaKey = self.captcha['key']
        self.tasklist = self.captcha['tasklist']
        
        self.proofData = self.captcha['c']

        #self.log(f'Solving: {self.question}')
        self.solution = self.answer2()
        #self.log(f'Solved: {self.prediction}')

        self.hsw = self.getHsw()

        elapsed_time = time.time() - started
        self.log(f'Got Solution In {elapsed_time}s')
        if elapsed_time < 3:
            timeToSleep = 3 - elapsed_time + random.uniform(0,0.5)
            #print(f'Waiting {round(timeToSleep,2)}s to not be under 5s')
            time.sleep(timeToSleep)

        self.captchaKey = self.postCaptcha()
        if 'generated_pass_UUID' in self.captchaKey:
            self.session.headers = self.oldHeaders
            self.log(f'Solved Captcha: {self.captchaKey["generated_pass_UUID"][:20]}')
            for x in self.textanswers:
                database[sha1(x[0].encode()).hexdigest()] =  x[1];
                with open('scraped.csv', 'a+') as txt:
                    txt.write(f'{sha1(x[0].encode()).hexdigest()}:{x[1]}\n')
            return self.captchaKey['generated_pass_UUID']
        self.session.headers = self.oldHeaders
        
        self.log(f'Failed Captcha: {self.captchaKey}')
        return None

if __name__ == "__main__":
    while True:
        started = time.time()
        solver = Solver(
            session=tls_client.Session(client_identifier="chrome114", random_tls_extension_order=True),
            siteKey="4c672d35-0701-42b2-88c3-78380b0db560",
                siteUrl="discord.com"
            #rqData='WgnlEveaU9kkuU0x19+477W3LBtdTuCPbCIQJhLBsqIQau+OmosgiTptVUsBB8UQe4zRHh2URrC9hANabDPRhI+bq3dPAgHFK9nnnZr5me/+xaDTGBVsYLQfksP8yxbrVidt3/+nrfneW1QgGyZrNTkUvbw/HfCC8o9vd7ev'
        )
        response = solver.solveCaptcha()
        # print(response)
        print(f"Solved In {round(time.time()-started,3)}s")