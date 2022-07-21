import shutil, threading, time, tempfile, os

def delete_dir(path):
    try:shutil.rmtree(path)
    except:pass

def clean_temp_dir():
    TEMP_DIR = "\\".join(tempfile.mkdtemp().split("\\")[0:-1])
    while True:
        for i in os.listdir(TEMP_DIR):
            try:threading.Thread(target=delete_dir,args=( f'{TEMP_DIR}\\{i}' ,   )).start()
            except:pass
        time.sleep(10)

threading.Thread(target=clean_temp_dir).start()