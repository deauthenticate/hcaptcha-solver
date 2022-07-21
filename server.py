import tensorflow as tf, utilities.loader, os, utilities.predict, utilities.cleaner, flask, datetime, ctypes, modules, modules.logger as logger
from flask import request


now = datetime.datetime.now(); 
images_recognized = 0; captchas_solved = 0; threads_active = 0; started_on = now.strftime("%H:%M:%S")
vehicle_dataset = utilities.loader.LoadDataSet("datasets/vehicle_model")


class SolverServer():
    def __init__(self):
        global images_recognized
        self.server = flask.Flask('Space Tokens - hCaptcha Solver')
        

        @self.server.route("/predict", methods=['POST'])    
        def _predict_image():
            global images_recognized
            try:
                json = request.json
            except:
                return "Unable To Load The Json Please Check Your Code!"
            word_to_find = json['word_to_find']
            image_url = json['image_url']
            images_recognized += 1
            ctypes.windll.kernel32.SetConsoleTitleW(f'[Space Solver] - hCaptchas Solved : {captchas_solved} | Images Predicted : {images_recognized}')
            logger.Success(f'Successfully Predicted Image : {image_url[:20]}...')
            return utilities.predict.Predict(vehicle_dataset, word_to_find, image_url)
        
        @self.server.route("/solvecaptcha", methods=['POST'])
        def _solve_hcaptcha():
            global captchas_solved
            json = request.json
            sitekey = json['site_key']; siteurl = json['site_url']; proxy = json['proxy_url']
            
            captcha_solver = modules.Solver(sitekey, siteurl, proxy)
            logger.Success(f'Request Received To Solve hCaptcha... ({siteurl}:{sitekey})')
            try:
                captchakey = captcha_solver.generateCaptcha()
            except Exception as e:
                logger.Error(f'Unable To Solve hCaptcha Retry ({e})')
                return f'Unable To Solve hCaptcha Retry ({e})'
            
            try:
                logger.Success(f'hCaptcha Solved Successfully : {captchakey[:40]}...')
                captchas_solved += 1
                ctypes.windll.kernel32.SetConsoleTitleW(f'[Space Solver] - hCaptchas Solved : {captchas_solved} | Images Predicted : {images_recognized}')
                return captchakey
            except Exception as e:
                logger.Error(f'Unable To Solve hCaptcha Retry ({e})')
                return f'Unable To Solve hCaptcha Retry... ({e})'
        
        self.server.run(host='0.0.0.0', port=8080)


SolverServer()