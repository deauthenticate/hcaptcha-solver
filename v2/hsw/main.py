import threading, os;

def start(port):
   os.system(f'py server-reload.py {port}');

for i in ['8484','9898','9999','9888']:
   threading.Thread(target=start, args=[i]).start()