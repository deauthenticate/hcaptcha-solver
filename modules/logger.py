import os, threading
from colorama import init, Fore
from datetime import datetime


def CenterText(var:str, space:int=None): # From Pycenter
    if not space:
        space = (os.get_terminal_size().columns - len(var.splitlines()[int(len(var.splitlines())/2)])) / 2
    return "\n".join((' ' * int(space)) + var for var in var.splitlines())
    
def Success(text):
    lock = threading.Lock()
    lock.acquire()
    print(f'[{Fore.GREEN}${Fore.WHITE}] {text}')
    lock.release()
    
def Error(text):
    lock = threading.Lock()
    lock.acquire()
    print(f'[{Fore.RED}-{Fore.WHITE}] {text}')
    lock.release()
    
def Question(text):
    lock = threading.Lock()
    lock.acquire()
    print(f'[{Fore.BLUE}?{Fore.WHITE}] {text}')
    lock.release()