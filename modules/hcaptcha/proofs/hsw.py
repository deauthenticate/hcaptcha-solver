
from datetime import datetime
from os.path import dirname
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import atexit
import math
import hashlib
import subprocess
import time
import random
import threading
wd_opt = Options()
wd_opt.add_argument("start-maximized")
wd_opt.add_argument("--headless")
wd_opt.add_experimental_option("excludeSwitches", ["enable-automation"])
wd_opt.add_experimental_option('useAutomationExtension', False)
wd = webdriver.Chrome(chrome_options=wd_opt)
wd2 = webdriver.Chrome(chrome_options=wd_opt)
wd3 = webdriver.Chrome(chrome_options=wd_opt)
wd4 = webdriver.Chrome(chrome_options=wd_opt)
#atexit.register(lambda *_: wd.quit())

hsw_time = 0
hsw_last = None
hsw_lock = threading.Lock()
def get_proof(req):
    
    with open(dirname(__file__) + "\\hcaptcha-js\\hsw.js") as fp:
        driver = random.choice([wd, wd2, wd3, wd4])
        driver.execute_script(fp.read() + "; window.hsw = hsw")
    
    proof = driver.execute_async_script("window.hsw(arguments[0]).then(arguments[1])", req)
    return proof