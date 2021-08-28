import json, sys, os, csv, time, datetime
from selenium import webdriver 
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys 
from stdiomask import getpass
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from send_mail import send_mail

chrome_options = Options()

chrome_options.add_argument("--headless")
basedir = os.path.abspath(os.path.dirname(__file__))

options = webdriver.ChromeOptions() 
option = options.add_experimental_option("excludeSwitches", ["enable-logging"])
browser = webdriver.Chrome(options=option, executable_path='./chromedriver.exe')

class Bot:
    def __init__(self):
        self.init_bot()
        # Second Algorithm Global Objects
        self.loss_streak = 0
        self.loss_count = 0
        self.profit_count = 0
        self.win = False
        self.played = False
        self.time_in_hour = 60
        self.url_timeout = 60 * self.time_in_hour
        self.pause_after_loss = False
        self.pause_after_loss_number = 0
        
        self.index_of_game_selected = None
        
        self.profit_streak = True
        self.future_mail = time.time() 
        self.isPlayed = False
        # Exceptions
        self.ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        

        choice = self.ask_for_input('Welcome to VFL bot\n1. To start the bot \n2. For settings\n3. Exit\n', 3)
        
        if choice == 1:
            self.start_bot()
        elif choice == 2:
            self.settings()
        elif choice == 3:
            time.sleep(3)
            sys.exit(0)

    def load_data(self):
        # Load Bet Stake 
        self.bet_stake = ""
        with open('C:\ProgramData\SRB\config.json', 'r') as config:
            config = json.load(config)
            self.bet_stake = config['bet']
            
            self.username = config["username"]
            self.password = config["password"]
            self.profit_limit = int(config["profit_limit"])
            self.loss_limit = int(config["loss_limit"])
            self.martingale_perc = int(config["martingale_perc"])

            self.bet_pause_interval = int(config["bet_pause_interval"])
            self.mail_frequency = int(config["mail_frequency"])
            
            self.email_subject = config["email_subject"]
            self.email_body = config["email_body"]
            self.email = config["email"]

            self.martingale_limit_number = int(config["martingale_limit_number"])
            self.martingale_limit = config["martingale_limit"] 
            
            self.all_teams = config['team_to_bet']
            self.team_current_index = 0
            if self.all_teams:
                self.team_to_bet = self.all_teams[self.team_current_index]
            else:
                print("You don't have any teams to play, Go to setting, number to set teams")
                time.sleep(2)
                self.settings()

        # Load martingale
        self.stake_martingale = self.bet_stake

        # Print GAMEPLAY TYPE
        print("Over 1.5 play game")

    def checkpoint(self):
        with open('C:\ProgramData\SRB\config.json', 'r') as config:
            config = json.load(config)
        
        cur_time = time.time()
        is_url_active = config["checkpoint"]
        is_checkpoint_active = config["timeout"]

        if is_url_active and is_checkpoint_active and is_checkpoint_active > cur_time:
            is_url_active = config["checkpoint"]
            # config["checkpoint"] = ""
            # write_json = json.dumps(config)
            # with open('C:\ProgramData\SRB\config.json', 'w') as conf:
            #     conf.write(write_json)
            browser.get(is_url_active)

            playAreaFrame = WebDriverWait(browser, 50).until(EC.presence_of_element_located((By.ID,"playAreaFrame")))
            browser.switch_to.frame(playAreaFrame)
            return True       
        return False
        
    def login(self):
        url = "https://sports.bet9ja.com/mobile/login"
        browser.get(url)
        # # Select all the elements 
        username = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//input[@type='text']")))
        password = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//input[@type='password']")))
        button = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//button[@class='btn w-full mt15']")))
        
        # perform actions on them
        username.send_keys(self.username)
        password.send_keys(self.password)
        button.click()
        
        # browser.switch_to.
        # Go to URL
        virtual_url = "https://vsmobile.bet9ja.com/bet9ja-mobile/login/?game=league&mode=premier"
        browser.get(virtual_url)
        # lOGIN TO InTEGRate
        # vfl_login_button = browser.find_element_by_id("btn-login")
        playAreaFrame = WebDriverWait(browser, 50).until(EC.presence_of_element_located((By.ID,"playAreaFrame")))
        browser.switch_to.frame(playAreaFrame)
        
        self.button_clicker("btn-login")

        # Switch to playFrameArea again
        playAreaFrame = WebDriverWait(browser, 50).until(EC.presence_of_element_located((By.ID,"playAreaFrame")))
        browser.switch_to.frame(playAreaFrame)       
        
        
        with open('C:\ProgramData\SRB\config.json', 'r') as config:
            config = json.load(config)

        # sAVE THE CURRENT URL FOR CHECKPOINTS 
        url = browser.current_url
        config["checkpoint"] = url
        config["timeout"] = self.url_timeout + time.time()

        write_json = json.dumps(config)

        with open('C:\ProgramData\SRB\config.json', 'w') as conf:
            conf.write(write_json)


        # To get the actual text value
        # self.starting_acc_bal = 0#int(self.starting_acc_bal.text.split(" ")[1])
        # print(self.starting_acc_bal.text.split(" "), self.starting_acc_bal.text) 
        # Init current live time to 0
        self.inner_text_setter("time_current_event", "0")

        # Login
    def button_clicker(self, id):
        browser.execute_script("""
            let vfl_login = document.getElementById('%s')
            console.log(vfl_login)
            if(vfl_login){
                vfl_login.click()
            }
        """ %id)
    
    def inner_text_setter(self, id, text):
        browser.execute_script("""
            let element = document.getElementById('%s');
            if(element) element.innerText = %s
        """ %(id, text))
        
    def parseTime(self, time_list):
        # print("Time ", time_list)
        minutes = time_list[0] 
        seconds = time_list[1]
        minutes = int(minutes) * 60
        seconds = int(seconds)
        return minutes + seconds

    def analyse_result(self):
        try:
            if self.index_of_game_selected != None:
                self.result_score_total = 0
                not_started_or_not_finish = True
                while not_started_or_not_finish:
                    vfl_live_timer = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//span[@id='time_current_event']")))
                    
                    if vfl_live_timer.text:
                        vfl_live_timer = int(vfl_live_timer.text)
                        team_a_score = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, f"//span[@id='goal_team_A_{self.index_of_game_selected}']")))
                        team_b_score =  WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, f"//span[@id='goal_team_B_{self.index_of_game_selected}']")))
                        if team_a_score and team_b_score:
                            team_a_score = int(team_a_score.text)
                            team_b_score = int(team_b_score.text)
                            if vfl_live_timer > 85: 
                                # Print Scores at end
                                print(f"Score at {vfl_live_timer} secs")
                                print(team_a_score, team_b_score)
                            
                                self.result_score_total = team_a_score + team_b_score
                                
                                not_started_or_not_finish = False
                                
                                if self.result_score_total < 2:
                                    print(f"Game LOST!!!, The total score is {self.result_score_total}")
                                    if not self.pause_after_loss:
                                        self.loss_count += 1
                                        self.loss_streak += 1
                                        print(f"STATS\nProfit count ---> {self.profit_count}\nLoss count ---> {self.loss_count}\nLoss Streak ---> {self.loss_streak} \n \n \n")
                                        # Multiply stake by martingale percentage
                                        self.stake_martingale = int(self.stake_martingale) * self.martingale_perc
                                        # send_mail(recipient=self.email, subject=self.email_subject, message=self.email_body)

                                    # Game paused logic
                                    self.pause_after_loss_number = self.bet_pause_interval
                                    if self.pause_after_loss_number:
                                        self.pause_after_loss = True
                                    else:
                                        self.switch_bot_team()
                                        
                                else:
                                    # Reset the stake
                                    if not self.pause_after_loss:
                                        self.stake_martingale = self.bet_stake
                                        self.profit_count += 1
                                        self.loss_streak = 0
                                        
                                        print(f"You won!!!, The total score is {self.result_score_total}")
                                        # send_mail(recipient=self.email, subject=self.email_subject, message=self.email_body)
                                        print(f"STATS\nProfit count ---> {self.profit_count}\nLoss count ---> {self.loss_count}\nLoss Streak ---> {self.loss_streak} \n \n \n")

                                    if self.pause_after_loss_number > 0: 
                                        self.pause_after_loss_number -= 1
                                        if self.pause_after_loss_number == 0:
                                            self.pause_after_loss = False

                                            # Switch team after consecutive losses has be observed
                                            self.switch_bot_team()
                                            print("The bot will resume game play now after the losses")
                                    else:
                                        self.pause_after_loss = False
                            
                                self.isPlayed = False

                        # print("Waiting for Game to start!")
                        time.sleep(3)
        except Exception as exc:
            # print(str(exc))
            time.sleep(3)
            self.analyse_result()

    def switch_bot_team(self):
        # Switch team after consecutive losses has be observed
        if self.team_current_index >= (len(self.all_teams) - 1):
            self.team_current_index = 0
            self.team_to_bet = self.all_teams[self.team_current_index]
            print(f"BOT has switch team to {self.team_to_bet}")
        else:
            self.team_current_index += 1
            self.team_to_bet = self.all_teams[self.team_current_index]
            print(f"BOT has switch team to {self.team_to_bet}")
            
    def get_current_bal(self):
        current_cash = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//div[@id='credit-countdown']")))
        if current_cash.text:  
            cash_string = current_cash.text.split(" ")[1]                  
            if "," in cash_string:
                cash_string = cash_string.replace(",", "")
                
            current_cash = int(cash_string)
            # print("Acc bal: ", current_cash)
            return current_cash

    def check_limits(self):
        try:
            current_cash = self.get_current_bal()
            # print("Check_limit", current_cash)   
            if current_cash != None:
                # new_cash = browser.find_element_by_xpath("//div[@class='rs-menu__balance-value']")
                # new_acc_bal = int(float(new_cash.find_element_by_tag_name('span').text))
                if self.martingale_limit == "1" and self.loss_streak >= self.martingale_limit_number:
                    send_mail(recipient=self.email, subject=self.email_subject, message=self.email_body)
                    print("Unfortunately, the game has to stop cos it has reached the martingale limit")
                    browser.quit()
                    # Set a large time for the time out
                    time.sleep(1200)
                    sys.exit(0)


                if  current_cash:
                    if current_cash >= self.loss_limit:
                        loss = self.starting_acc_bal - current_cash 
                        print(f"Sorry... You have reached your loss limit, you lost N{loss}, try again soon, you have better strategy do contact me via whatsapp +2348142700835")
                        send_mail(recipient=self.email, subject=self.email_subject, message=self.email_body)
                        browser.quit()
                        # Set a large time for the time out self.
                        time.sleep(1200)
                        sys.exit(0)

                    elif current_cash >= self.profit_limit:
                        profit = current_cash - self.starting_acc_bal
                        send_mail(recipient=self.email, subject=self.email_subject, message=self.email_body)
                        print(f"congratulation!!! You have reached your profit limit, you won N{profit} play more soon!")
                        browser.quit()
                        # Set a large time for the time out
                        time.sleep(1200)
                        sys.exit(0)
            else:
                time.sleep(3)
                self.check_limits()

        except Exception as exc:
            print(str(exc))

        # if self. current_cash

    def get_team_index(self):
            if not self.isPlayed:
                vfl_timer = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//div[@id='bets-time-betContdown']")))
                ov_one_button = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Over/Under 1.5")))
                ov_one_button.click()
                
                get_games = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_all_elements_located((By.XPATH,"//div[@id='tab_id_Over_Under_1_5']/ul/li/div/fieldset/table/tbody/tr/td/div[2]")))

                self.index_of_game_selected = None
                for index, game in enumerate(get_games):
                    if self.team_to_bet in game.text:
                        self.index_of_game_selected = index
        
    def play_game(self):
        try:
            if not self.isPlayed:
                vfl_timer = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//div[@id='bets-time-betContdown']")))
                
                
                # default random number to show when the vfl timer is not visible
                current_time = 12        
                if len(vfl_timer.text.split(":")):

                    # print(vfl_timer.text, self.parseTime(vfl_timer.text.split(":")))
                    current_time = self.parseTime(vfl_timer.text.split(":"))
            

                # play game only when the time is greater than 10sec
                if current_time > 10:
                    ov_one_button = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"Over/Under 1.5")))
                    ov_one_button.click()
                    
                    get_games = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_all_elements_located((By.XPATH,"//div[@id='tab_id_Over_Under_1_5']/ul/li/div/fieldset/table/tbody/tr/td/div[2]")))

                    self.index_of_game_selected = None
                    for index, game in enumerate(get_games):
                        if self.team_to_bet in game.text:
                            self.button_clicker(f"Over_Under_1_5_{index}_over")
                            self.index_of_game_selected = index
                    

                    
                    # current_cash = self.get_current_bal()

                    # if current_cash < int(self.stake_martingale):
                    #     print("Not enough credit")

                    #     acc_bal = self.get_current_bal()
                        
                    #     message = f"""
                    #     INSUFFICIENT BALANCE!!!

                    #     {self.email_body}
                    #     Account Statement
                    #     ==========================================\n
                    #     Starting Account =  {self.starting_acc_bal}\n
                    #     Current Account Balance = {acc_bal}\n
                    #     ==========================================\n
                    #     change in Cash  = {self.starting_acc_bal - acc_bal}\n
                    #     """

                    #     send_mail(recipient=self.email, subject=self.email_subject, message=message)
                    #     ok_button = WebDriverWait(game, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//button[text()='OK']")))
                    #     if ok_button:
                    #         ok_button.click()
                        
                    # else:
                    #     stake_input = WebDriverWait(game, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//input[@id='inputAmount']")))
                    #     stake_input.send_keys(str(self.stake_martingale))
                        
                    #     # Bet button
                    #     bet_button = WebDriverWait(game, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//button[@id='button_bet']")))
                    #     bet_button.click()

                    #     time.sleep(3)
                    #     self.button_clicker(f"button_bet_ticket")
                    #     time.sleep(2)
                    #     self.button_clicker(f"button_sent-ticket-close")

                    #     # Shift this 
                    self.isPlayed = True
                    
                    print(f"{self.team_to_bet} Over 1,5 played!")
        
        except Exception as exc:
            # print("Next Game is Loading or ran into some sort of error...", str(exc))
            time.sleep(2)
            self.play_game()


    def interval_mail(self):
        current_time = time.time()
        if current_time > self.future_mail:
            acc_bal = self.get_current_bal()
            if acc_bal:
                message = f"""
                {self.email_body}\n
                Account Statement
                ==========================================\n
                Starting Account =  {self.starting_acc_bal}\n
                Current Account Balance = {acc_bal}\n
                ==========================================\n
                change in Cash  = {self.starting_acc_bal - acc_bal}\n


                Game Stats\n
                ==========================================\n
                amount of Game won = {self.profit_count}\n
                amount of Game Loss = {self.loss_count}\n
                """

                send_mail(recipient=self.email, subject=self.email_subject, message=message)
                self.future_mail = current_time + (60 * 60 * self.mail_frequency)
                print(f"The next mail is scheduled till the next {self.mail_frequency} hours")


    def handle_error_buttons(self):
        try:
            error_btn = WebDriverWait(browser, 3 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//button[text()='OK']")))
            error_btn.click()
        except Exception as exc:
            print("Error OK Button was not present") 

    def start_bot(self):
        
        self.load_data()
        
        self.checkpointTrue = self.checkpoint()
        # maximize page
        browser.maximize_window()
        
        if not self.checkpointTrue:
            self.login()

        
        # self.starting_acc_bal = WebDriverWait(browser, 50 ,ignored_exceptions=self.ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//div[@id='credit-countdown']")))
        # Get Starting balance
        self.starting_acc_bal = self.get_current_bal()
        print(f"The bot is opening account with N{self.starting_acc_bal}")

        self.bot_loop()


    def bot_loop(self):
        while True:
            # Check limits loss and profit
            self.check_limits()

            # Sleep for a while
            time.sleep(2)
            
            if self.pause_after_loss:
                self.get_team_index()
                print(f"Game Paused for previous, it remains {self.pause_after_loss_number} consecutive wins before continuing")
            else:
                self.play_game()
                self.interval_mail()

            # This will block the thread until the game result is finalized 
            self.analyse_result()
    
            # Init current live time to 0
            self.inner_text_setter("time_current_event", "0")
    
        # except Exception as exc:
        #     print("some bad happened restarting bot to continue playing", str(exc))
        #     time.sleep(5)
        #     self.bot_loop()
    
    def init_bot(self):
        try:
            with open('C:\ProgramData\SRB\config.json', 'r') as config:
                config = json.load(config)    
            if not config["username"]:
                unconfirmed_username = True
                username = ""
                while unconfirmed_username:
                    print('hi, congratulation for acquiring bet9ja VFL bots\n')
                    username_value = input('set your bet9ja username, make sure it is correct because you are allowed to set it once in the bot\n')
                    username_value_comfirmed = input('confirm your username, make sure it is correct because you are allowed to set it once once in the bot\n')
                    if username_value == username_value_comfirmed:
                        unconfirmed_username = False
                        username = username_value
                        print(f'++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your bet9ja username to {username} \n++++++++++++++++++++')
                    else:
                        print('++++++++++++++++++++\nyour username and confirm username must match\n++++++++++++++++++++')
                        time.sleep(2)

                config['username'] = username
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)


            # for your bet 9ja password

            if not config["password"]:
                unconfirmed_password = True
                password = ""
                while unconfirmed_password:
                    password_value = getpass(prompt='set your bet9ja password \n')
                    password_value_comfirmed = getpass(prompt='confirm your password\n')
                    if password_value == password_value_comfirmed:
                        unconfirmed_password = False
                        password = password_value
                        print(f'++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your bet9ja password to {password} \n++++++++++++++++++++')
                    else:
                        print('++++++++++++++++++++\nyour password and confirm password must match\n++++++++++++++++++++')
                        time.sleep(2)

                config['password'] = password
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)


            if not config["bet"]:
                not_enough_bet = True
                # making sure the bet is more than 
                while not_enough_bet:
                    bet_value = input('set the amount you want the bot to bet in naira e.g 100, you can always change this in the settings \n')
                    if bet_value.isdecimal():
                        if int(bet_value) >= 50:
                            config['bet'] = bet_value
                            print(f"++++++++++++++++++++\nthe bet price has been successfully set {bet_value}\n++++++++++++++++++++")
                            not_enough_bet = False
                        else:
                            print("++++++++++++++++++++\nthe least amount a bot can bet is 50\n++++++++++++++++++++")
                            time.sleep(2)
                    else:
                        print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                        time.sleep(2)

                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)

            if not config["martingale"]:
                algo_value = self.ask_for_input('Do you want the bot to have martingale system, i.e the ability to triple stake upon lose\n1. Yes \n2. No\n', 2)
                config['martingale'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)

            if not config["martingale_perc"]:
                algo_value = float(input("Set you martingale multiples in decimals or integers e.g 1.5 or 2\n"))
                config['martingale_perc'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)
            
            if not config["martingale_limit"]:
                algo_value = self.ask_for_input('Do you want to activate martingale limit\n1. Yes \n2. No\n', 2)
                config['martingale_limit'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)

            if not config["martingale_limit_number"]:
                algo_value = float(input("Set you martingale limit number e.g 3, 4 or any reasonable number\n"))
                config['martingale_limit_number'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)
            

            if not config["loss_limit"]:
                no_loss_limit = True
                # making sure the bet is more than 
                while no_loss_limit:
                    loss_limit_value = input('set your loss limit in naira e.g. 1000, if you don"t set your loss limit, if you are unfortunate, the bot might run until you have lost all your funds, you can always change this in the settings \n')
                    if loss_limit_value.isdecimal():
                        if int(loss_limit_value) >= 500:
                            config['loss_limit'] = loss_limit_value
                            print(f"++++++++++++++++++++\nthe loss limit has been successfully set {loss_limit_value}\n++++++++++++++++++++")
                            no_loss_limit = False
                        else:
                            print('++++++++++++++++++++\nloss limit too small the least should be 500\n++++++++++++++++++++')
                            time.sleep(2)
                    else:
                        print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                        time.sleep(2)

            
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)

                time.sleep(2)

            if not config["profit_limit"]:
                no_profit_limit = True
                # making sure the bet is more than 
                while no_profit_limit:
                    profit_limit_value = input('set your profit limit in naira e.g. 1000, if you don"t set your profit limit, you might never make any profit till the bot reach loss limit and if you did not set your loss limit as well you might lose all you funds \n')
                    if profit_limit_value.isdecimal():
                        if int(profit_limit_value) >= 500:
                            config['profit_limit'] = profit_limit_value
                            print(f"++++++++++++++++++++\nthe profit limit has been successfully set {profit_limit_value}\n++++++++++++++++++++")
                            no_profit_limit = False
                        else:
                            print('++++++++++++++++++++\nprofit limit too small the least should be 500\n++++++++++++++++++++')
                            time.sleep(2)
                    else:
                        print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                        time.sleep(2)

            
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)

                time.sleep(2)
            
            if not config["team_to_bet"]:
                teams = []
                loop = True
                while loop:
                    algo_value = input("Enter the teams you want to play ov1,5 for in this format -> MNC, SOU e.t.c\n")
                    teams.append(algo_value)
                    config['team_to_bet'] = teams
                    write_json = json.dumps(config)

                    with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                        conf.write(write_json)
                    
                    print(f"Team {algo_value} saved successfully!!!")
                    
                    choice = self.ask_for_input("Do you want to add more \n1. Yes \n2.No\n", 2)
                    if choice == 2:
                        loop = False
                        time.sleep(2)

            if not config["email"]:
                algo_value = input("Enter the email address you want to send notifications to e.g. dataslid@gmail.com\n")
                config['email'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)

            if not config["email_subject"]:
                algo_value = input("Set mail subject for notifications to e.g. Profit alert\n")
                config['email_subject'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)

            
            if not config["email_body"]:
                algo_value = input("Set mail body for notifications to e.g. Profit alert\n")
                config['email_body'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)

            if not config["bet_pause_interval"]:
                algo_value = input("Enter how many constant you want the bot to watch before continuing playing game after each loss e.g 1 or 2\n")
                config['bet_pause_interval'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)

            
            if not config["mail_frequency"]:
                algo_value = input("Enter in hours how often you want to receive emails e.g if every 12 hours enter just --> 12\n")
                config['mail_frequency'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)

        except Exception as exc:
            print(exc)
            demo_start_date = time.time()
            config = {"username": "", "password": "", "bet": "", "loss_limit": "", "profit_limit": "", "acc_bal": "", "checkpoint": "", "checkpoint_type": "", "timeout": "", "team_to_bet": "", "alert_music": "", "demo_start_date": f"{demo_start_date}", "bot_type": "paid", "remote_url": "", "is_active": "", "user_id": "", "martingale": "", "martingale_perc": "", "color_failure": "", "martingale_limit": "", "martingale_limit_number": "", "email": "", "email_subject": "", "email_body": "", "team_to_bet": [], "mail_frequency": "", "bet_pause_interval": ""}
            write_json = json.dumps(config) 
            os.chdir('C:\ProgramData')
            if 'SRB' in os.listdir():
                with open('./SRB/config.json', 'w') as config:
                    config.write(write_json)
            else:
                os.system("mkdir SRB")
                with open('./SRB/config.json', 'w') as config:
                    config.write(write_json)
                    
            self.init_bot()
 
    def settings(self):
        choice = self.ask_for_input('what do you want to change?\n1. bet price\n2. bet9ja password\n3. settings for email address for mail notification \n4. settings for the email subject notification \n5. settings for the email body \n6. loss limit\n7. profit limit\n8. Set teams to play e.g MNC, CHE e.t.c\n9. reset whether your want martingale percent in numbers or decimals\n10. reset whether your want martingale system or not\n11. reset whether your want to activate the martingale limit or not\n12. Reset you martingale limit number e.g 3, 4 or any reasonable number\n13. Enter how many games you want the bot to watch before continuing playing game after each loss e.g 1 or 2\n14. Enter in hours how often you want to receive emails e.g if every 12 hours enter just --> 12\n', 14) 

        if choice == 1:
            self.bot_settings("bet")

        elif choice == 2:
            self.bot_settings("password")

        elif choice == 3:
            self.bot_settings("email")

        elif choice == 4:
            self.bot_settings("email_subject")

        elif choice == 5:
            self.bot_settings("email_body")

        elif choice == 6:
            self.bot_settings("loss_limit")
        
        elif choice == 7:
            self.bot_settings("profit_limit")
        
        elif choice == 8:
            self.bot_settings("team_to_bet")

        elif choice == 9:
            self.bot_settings("martingale_perc")
        
        elif choice == 10:
            self.bot_settings("martingale")

        elif choice == 11:
            self.bot_settings("martingale_limit")
        
        elif choice == 12:
            self.bot_settings("martingale_limit_number")
        
        
        elif choice == 13:
            self.bot_settings("bet_pause_interval")
        
        elif choice == 14:
            self.bot_settings("mail_frequency")




    def bot_settings(self, arg):
        with open('C:\ProgramData\SRB\config.json', 'r') as config:
            config = json.load(config)

        if arg == "bet":
            print(f"\nThe current bet price is set to {config['bet']}\n")
            not_enough_bet = True
            # making sure the bet is more than 
            while not_enough_bet:
                bet_value = input('reset the amount you want the bot to bet in naira e.g 100\n')
                if bet_value.isdecimal():
                    if int(bet_value) >= 50:
                        config['bet'] = bet_value
                        print(f"++++++++++++++++++++\nthe bet price has been successfully set {bet_value}\n++++++++++++++++++++")
                        not_enough_bet = False
                    else:
                        print("++++++++++++++++++++\nthe least amount a bot can bet is 50\n++++++++++++++++++++")
                        time.sleep(2)
                else:
                    print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                    time.sleep(2)

            write_json = json.dumps(config)
            with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                conf.write(write_json)

            time.sleep(2)
            self.__init__()

        elif arg == "loss_limit":
            print(f"\nThe current loss limit is set to {config['loss_limit']}\n")
            no_loss_limit = True
            # making sure the bet is more than 
            while no_loss_limit:
                loss_limit_value = input('reset your loss limit in naira e.g. 1000, if you don"t set your loss limit, if you are unfortunate, the bot might run until you have lost all your funds \n')
                if loss_limit_value.isdecimal():
                    if int(loss_limit_value) >= 500:
                        config['loss_limit'] = loss_limit_value
                        print(f"++++++++++++++++++++\nthe loss limit has been successfully set {loss_limit_value}\n++++++++++++++++++++")
                        no_loss_limit = False
                    else:
                        print('++++++++++++++++++++\nloss limit too small the least should be 500\n++++++++++++++++++++')
                        time.sleep(2)
                else:
                    print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                    time.sleep(2)

          
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                conf.write(write_json)

            time.sleep(2)
            self.__init__()

        elif arg == "profit_limit":
            print(f"\nThe current profit limit is set to {config['profit_limit']}\n")
            no_profit_limit = True
            # making sure the bet is more than 
            while no_profit_limit:
                profit_limit_value = input('reset your profit limit in naira e.g. 1000, if you don"t set your profit limit, you might never make any profit till the bot reach loss limit and if you did not set your loss limit as well you might lose all you funds \n')
                if profit_limit_value.isdecimal():
                    if int(profit_limit_value) >= 500:
                        config['profit_limit'] = profit_limit_value
                        print(f"++++++++++++++++++++\nthe profit limit has been successfully set {profit_limit_value}\n++++++++++++++++++++")
                        no_profit_limit = False
                    else:
                        print('++++++++++++++++++++\nprofit limit too small the least should be 500\n++++++++++++++++++++')
                        time.sleep(2)
                else:
                    print("++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++")
                    time.sleep(2)

          
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                conf.write(write_json)

            time.sleep(2)
            self.__init__()

        elif arg == "password":
            print(f"\nyour current password is set to {config['password']}\n")
            unconfirmed_password = True
            password = ""
            while unconfirmed_password:
                password_value = getpass(prompt='reset your bet9ja password \n')
                password_value_comfirmed = getpass(prompt='confirm your password\n')
                if password_value == password_value_comfirmed:
                    unconfirmed_password = False
                    password = password_value
                    print(f'++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your bet9ja password to {password} \n++++++++++++++++++++')
                else:
                    print('++++++++++++++++++++\nyour password and confirm password must match\n++++++++++++++++++++')
                    time.sleep(2)

            config['password'] = password
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                conf.write(write_json)
            
            time.sleep(2)
            self.__init__()

        elif arg == 'team_to_bet':
            teams = []
            loop = True
            while loop:
                algo_value = input("Enter the teams you want to play ov1,5 for in this format -> MNC, SOU e.t.c\n")
                teams.append(algo_value)
                config['team_to_bet'] = teams
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                print(f"Team {algo_value} saved successfully!!!")
                choice = self.ask_for_input("Do you want to add more \n1. Yes \n2.No\n", 2)
                
                if choice == 2:
                    loop = False
                    time.sleep(2)
                    self.__init__()

        elif arg == 'email':
            algo_value = input("Enter the email address you want to send notifications to e.g. dataslid@gmail.com")
            config['email'] = algo_value
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as config:
                config.write(write_json)

            time.sleep(2)
            self.__init__()


        elif arg =="email_subject":
            algo_value = input("Set mail subject for notifications to e.g. Profit alert")
            config['email'] = algo_value
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as config:
                config.write(write_json)
            
            time.sleep(2)
            self.__init__()
        
        elif arg == "email_body":
            algo_value = input("Set mail body for notifications to e.g. Profit alert")
            config['email'] = algo_value
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as config:
                config.write(write_json)
            
            time.sleep(2)

            self.__init__()


        elif arg == "martingale":
            algo_value = self.ask_for_input('Do you want the bot to have martingale system, i.e the ability to triple stake upon lose\n1. Yes \n2. No\n', 2)
            config['martingale'] = algo_value
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                conf.write(write_json)
            
            time.sleep(2)
            self.__init__()

        elif arg == "martingale_perc":
            algo_value = float(input("Set you martingale multiples in decimals or integers e.g 1.5 or 2\n"))
            config['martingale_perc'] = algo_value
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                conf.write(write_json)
            
            time.sleep(2)
            self.__init__()

        elif arg == "martingale_limit":
                algo_value = self.ask_for_input('Do you want to activate martingale limit\n1. Yes \n2. No\n', 2)
                config['martingale_limit'] = algo_value
                write_json = json.dumps(config)

                with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                    conf.write(write_json)
                
                time.sleep(2)
                self.__init__()

        elif arg == "martingale_limit_number":
            algo_value = float(input("Set you martingale limit number e.g 3, 4 or any reasonable number\n"))
            config['martingale_limit_number'] = algo_value
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                conf.write(write_json)
            
            time.sleep(2)
            self.__init__()

        
        elif arg == "bet_pause_interval":
            algo_value = input("Enter how many constant you want the bot to watch before continuing playing game after each loss e.g 1 or 2\n")
            config['bet_pause_interval'] = algo_value
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                conf.write(write_json)
            
            time.sleep(2)
            self.__init__()

        
        elif arg == "mail_frequency":
            algo_value = input("Enter in hours how often you want to receive emails e.g if every 12 hours enter just --> 12\n")
            config['mail_frequency'] = algo_value
            write_json = json.dumps(config)

            with open('C:\ProgramData\SRB\config.json', 'w') as conf:
                conf.write(write_json)
            
            time.sleep(2)
            self.__init__()

        
    def ask_for_input(self, question, max_choice):
        choice = ""
        while choice == "":
            num_input = input(question)
            if num_input.isdecimal():
                choice = int(num_input)
                if choice <= max_choice:
                    return choice
                
                print('++++++++++++++++++++\nyour choice is out of bound\n++++++++++++++++++++')
                choice = ""
            print('++++++++++++++++++++\ninvalid choice\n++++++++++++++++++++')
 
Bot()