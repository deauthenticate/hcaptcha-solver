import httpx, random, time
import certifi
import tls_client
class DolphinClient():
    def GetContext():
        ciphers_top = "ECDH+AESGCM:ECDH+CHACHA20:DH+AESGCM"
        ciphers_mid = 'DH+CHACHA20:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:RSA+AESGCM:RSA+AES:RSA+HIGH:!aNULL:!eNULL:!MD5:!3DES'
        cl = ciphers_mid.split(":")
        cl_len = len(cl)
        els = []
        
        for i in range(cl_len):
            idx = random.randint(0, cl_len-1)
            els.append(cl[idx])
            del cl[idx]
            cl_len-=1
        
        ciphers2 = ciphers_top+":".join(els)
        context = httpx.create_ssl_context()
        context.load_verify_locations(cafile=certifi.where())
        context.set_alpn_protocols(["h2"])
        context.minimum_version.MAXIMUM_SUPPORTED
        CIPHERS = ciphers2
        context.set_ciphers(CIPHERS)
        
        ciphers2
    
    def GetTransport():
        return httpx.HTTPTransport(retries=3)
    def __init__(self):
        self.auth_token = ''
        self.resolutions = ["1280x720","1280x800","1280x1024","1366x768","1440x900","1536x864","1600x900"]

        self.session = httpx.Client(transport=DolphinClient.GetTransport(), verify=DolphinClient.GetContext(), timeout=None)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.auth_token
        })
    
    def _start_browser(self, profile_id : str):
        response = self.session.get(f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1").json()
        print(response)
        return response["automation"]
    
    def _delete_browser(self, profile_id : str):
        self.session.delete(f'https://dolphin-anty-api.com/browser_profiles/{profile_id}?forceDelete=1')
    
    def _get_fingerprint(self):
        params = { 'platform': 'windows', 'browser_type': 'anty', 'browser_version': '112', 'type': 'fingerprint', 'screen': '1920x1080' }
        return self.session.get('https://dolphin-anty-api.com/fingerprints/fingerprint', params=params).json()
    
    def _create_browser_profile(self):
        browser_version = random.randint(100,120)
        payload = { "name": "Discord", "useragent[mode]": "manual", "mainWebsite": "google", "useragent[value]": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version}.0.0.0 Safari/537.36", "platform": "windows", "webrtc[mode]": "on", "canvas[mode]": "noise", "webgl[mode]": "noise", "locale[mode]": "auto", "cpu[mode]": "noise", "memory[mode]": "noise", "browserType": "anty", "webglInfo[mode]": "noise", "geolocation[mode]": "auto", "doNotTrack": 0 }

        response = self.session.post(f'https://dolphin-anty-api.com/browser_profiles', json=payload).json()
        return response['browserProfileId']
    
    def _update_browser(self, profile_id : str):
        browser_version = random.randint(100,120)
        fingerprint = self._get_fingerprint()

        payload = {
            'name': 'Discord',
            'tags': [],
            'browserType': 'anty',
            'mainWebsite': 'google',
            'useragent': {
                'mode': 'manual',
                'value': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version}.0.0.0 Safari/537.36',
            },
            'webrtc': {
                'mode': 'altered',
                'ipAddress': None,
            },
            'canvas': {
                'mode': 'noise',
            },
            'webgl': {
                'mode': 'noise',
            },
            'webglInfo': {
                'mode': 'manual',
                'vendor': fingerprint['webgl']['unmaskedVendor'],
                'renderer': fingerprint['webgl']['unmaskedRenderer'],
                'webgl2Maximum': fingerprint['webgl2Maximum'],
            },
            'clientRect': {
                'mode': 'noise',
            },
            'notes': {
                'content': None,
                'color': 'blue',
                'style': 'text',
                'icon': None,
            },
            'timezone': {
                'mode': 'auto',
                'value': None,
            },
            'locale': {
            'mode': 'auto',
            'value': None,
            },
            'proxy': None,#"http://thunderimwvzdrv36R-res-ANY:getohjahvalq83B@gw.thunderproxies.net:5959",
            'statusId': 0,
            'geolocation': {
                'mode': 'auto',
                'latitude': None,
                'longitude': None,
                'accuracy': None,
            },
            'cpu': {
                'mode': 'manual',
                'value': random.choice(["2","4","6","8","10","12","16"]),
            },
            'memory': {
                'mode': 'manual',
                'value': random.choice(["4", "8"]),
            },
            'screen': {
                'mode': 'real',
                'resolution': random.choice(self.resolutions),
            },
            'audio': {
                'mode': 'real',
            },
            'mediaDevices': {
                'mode': 'manual',
                'audioInputs': random.randint(1, 3),
                'videoInputs': random.randint(1, 3),
                'audioOutputs':     random.randint(1, 3)
            },
            'ports': {
                'mode': 'protect',
                'blacklist': '3389,5900,5800,7070,6568,5938',
            },
            'doNotTrack': True,
            'args': [],
            'platformVersion': '10.0.0',
            'uaFullVersion':  f'{browser_version}.0.5615.49',
            'login': '',
            'password': '',
            'appCodeName': 'Mozilla',
            'platformName': 'MacIntel',
            'connectionDownlink': 10,
            'connectionEffectiveType': '4g',
            'connectionRtt': 100,
            'connectionSaveData': 0,
            'cpuArchitecture': 'amd64',
            'osVersion': '10',
            'vendorSub': '',
            'productSub': '20030107',
            'vendor': 'Google Inc.',
            'product': 'Gecko',
        }

        self.session.patch(f'https://dolphin-anty-api.com/browser_profiles/{profile_id}', json=payload)

