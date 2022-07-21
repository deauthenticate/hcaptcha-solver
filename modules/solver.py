import httpx, threading, requests
from timeit import default_timer as timer
import modules.logger as logger
from colorama import Fore, Style, init
import modules.hcaptcha as hcaptcha, time
init()

class Solver:
    def __init__(self, site_key, url, proxy = None):
        self.site_key = site_key
        self.url = url
        self.captcha = hcaptcha
        self.proxy = proxy
        self.console = Console()

    def get_topic(self, ch):
        topic = ch.question["en"]
        
        if "river" in topic:
            return topic.split(" ")[-2]
        elif "left" in topic:
            return "left"
        else:
            return topic.split(" ")[-1]

    def answer_question(self, ch ,topic, tile, url):
        req = httpx.post('http://localhost:8080/predict', json={ 
            'word_to_find': topic,
            'image_url': url
        }, timeout=None)#requests.post("http://185.61.137.160:26000/predict", headers = {"Content-Type":"text/plain; charset=UTF-8"}, data = data)
        correct = req.text == "True"

        if correct:
            ch.answer(tile)
            return tile.index + 1
            
    def generateCaptcha(self):
        
        ch = self.captcha.Challenge(
            site_key=self.site_key,
            site_url=self.url,
            proxy=self.proxy,
        )
        start = time.time()

        topic = self.get_topic(ch)
        answers = []    
        tiles = []

        for tile in ch:
            tiles.append(tile)

        logger.Success(f'Obtained {len(tiles)} Tiles ({topic}...)')

        for i in range(len(tiles)):
            answer = self.answer_question(ch, topic, tiles[i], str(tiles[i].image_url))
            if answer:
                answers.append(answer)

        try:
            token = ch.submit()
            end = timer()
            logger.Success(f'Successfully Solved hCaptcha Getting hCaptcha Token... ({round(time.time() - start)}) ')
            

        except self.captcha.ChallengeError as err:
            self.console.pprint(err)
            ch.close()
            return False
        finally:
            if ch: ch.close()

        if token:
            return token

class Console:
    def __init__(self):
        self.lock = threading.Lock()
        
    def pprint(self, text):
        self.lock.acquire()
        print(text)
        self.lock.release()