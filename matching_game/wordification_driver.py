
"""
     Handles logins and pilots student
     Teach once - or as many times as you want?
     When you're ready click start

     add scrolling to feedback
"""

from matching_words import *
from collections import defaultdict
from tkinter import *
from tkinter import font
from random import random as RNG
from student import Student
import datetime
import sorting, matching

import threading, queue

import requests, sys, os

colors = {
    'dark_blue' : "#294777",
    'light_blue': "#55a0d6",
    'orange' : "#ed9f47",
    'dark_orange' : "#f48042",
    'red' : "#ef5656",
    'green' : "#38ea85",
    'lime_green': "#caf441",
    'teal': "#41f4ac",
    'cyan' : "#41d0f4",
    'indigio' : "#4170f4",
    'violet' : "#7f41f4",
    'hot_pink' : "#f44182",
    'dark_red' : "#a81900"
}
"""
head_font = font.Font(family = "Consolas",size=20, weight='bold')
med_font = font.Font(family = "Consolas",size=14, weight='bold')
sm_font = font.Font(family = "Consolas",size=12, weight='')
"""
def get_csrftoken(client):

    if 'csrftoken' in client.cookies:
        # Django 1.6 and up
        csrftoken = client.cookies['csrftoken']
        print("Acquired Token")
    else:
        # older versions
        csrftoken = client.cookies['csrf']
     #print(client.cookies.keys())
    return csrftoken


def submit_results(client, _game_dat, _DEBUG):
    URL = "http://scholastechnology.com/post_data/"
    
    DEBUG = _DEBUG
    if DEBUG or _game_dat == {}:       
        URL = "http://127.0.0.1:8000/post_data/"
        _game_dat["time"] = 600      
        _game_dat["complete"] = 11
        _game_dat["correct"] = 0
        _game_dat["total_categories"] = "aI,iCe,I"
        _game_dat["total_words"] = 24
        _game_dat["correct_categories"] = 0
        _game_dat["verbose_logs"] = "logs/test.txt"
        #_game_dat["verbose_logs_file"] = open("logs/test.txt", 'rb')
        _game_dat["passed"] = "NA"
        _game_dat["category"] = "Teach"
        _game_dat["exercise_type"] = "Matching"
        _game_dat["exercise_level"] = 1
        _game_dat["score"] = 100.0

    if len(_game_dat) <= 0: return False
    client.get(URL)  # sets cookie
    csrftoken = get_csrftoken(client)
    print("Got csrftoken")
    payload = _game_dat
    if os.path.isfile(_game_dat["verbose_logs"]):
        _files = {"verbose_logs_file": open(_game_dat["verbose_logs"], 'rb')}
        payload["csrfmiddlewaretoken"] = csrftoken
        r = client.post(URL, files = _files, data=payload)
        return bool(r.text)

"""
Sends username and password to the login url
Returns a float value between 1 and 5 if login was successfull
Returns -1 or bad html if unsuccessful
returns -2 if the server could not be reached
"""

def try_login(client, u_name, p_word, _DEBUG):
    URL = "http://scholastechnology.com/login/"
    DEBUG = _DEBUG
    if DEBUG:
        URL = "http://127.0.0.1:8000/login/"
    # client = requests.session()

    # Retrieve the CSRF token first
    try:
        client.get(URL)  # sets cookie
        csrftoken = get_csrftoken(client)
        print("Got token")
        payload = dict(username = u_name, password =  p_word, csrfmiddlewaretoken=csrftoken)
        r = client.post(URL, data=payload)
        retval = r.text
    except:
        print("site not running")
        retval = -2
    return retval

def test_responses(payload, _DEBUG):
    client = requests.session()
    username = "test_acc"
    password = "adm1nrul3z"
    if _DEBUG:
        payload = {}
    print("Attempting login")
    client_response = try_login(client, username, password, _DEBUG)
    print("Login successful")
   
    print("Attempting upload")
    client_response = submit_results(client, payload, _DEBUG)
    print("Upload successful")
    print(client_response)

class WordificationDriver():

    def __init__(self):
        self.build_root()
        self.root.mainloop()

    def build_root(self):
        self.DEBUG = False
        self.root = Tk()
        self.client = requests.session()
        self.menu_items = defaultdict()
        self.head_font = font.Font(family = "Consolas",size=20, weight='bold')
        self.med_font = font.Font(family = "Consolas",size=14, weight='bold')
        self.sm_font = font.Font(family = "Consolas",size=12)
        self.root.title('Wordification® - Main Menu')

        license_text = "Wordification®/SpellingBits®"
        Label(self.root, text=license_text, font = self.sm_font).pack(fill=Y, side=BOTTOM, expand=FALSE)

        self.error_message = StringVar()

        self.student = Student("Test", 1.0)
        print("login successfull and student created")

        self.render_home()

    def call_login(self):
        client_response = try_login(self.client, self.username.get(), self.password.get(), self._DEBUG)
        print("Client responded with %s" %client_response)
        student_level = 0
        try:
            student_level = int(float(client_response))
        except:
            self.handle_error(self.login_box, "Incorrect username or password", 5, 0)
            return

        if student_level == -1:
            self.handle_error(self.login_box, "User not authenticated", 5, 0)
            return
        elif student_level == -2:
            self.handle_error(self.login_box, "Site could not be reached", 5, 0)
            #WARNING INFINITE RECURSION A POSSIBILITY
            self.call_login()
            return

        self.student = Student(self.username.get(), student_level)
        print("login successfull and student created")
        self.reset_board(self.login_box)
        self.render_home()
        """
        Takes to home screen - see progress, scores, ranking?
        Welcome back X, you're currently at level 3
        Log out button, reset client, reset passwords, etc.
        Render main exercise - test
        Following a test event - allow teaching at current level
        """

    def handle_error(self, frame, _error_message, _row, _column):
        if not self.error_message.get() == "":
            print("reset error msg - %s" %_error_message)
            self.menu_items["error"].grid_forget()
            del self.menu_items["error"]

        self.error_message.set(_error_message)
        self.menu_items["error"] = Label(frame, textvariable = self.error_message, font = self.med_font)
        self.menu_items["error"].grid(row = _row, column = _column, columnspan = 3)


    def reset_board(self, target_board):
        target_board.destroy()
        self.menu_items = defaultdict()
        print("Reset successfull")
        self.root.title('Wordification® - Home')

    """
    table for last login
    """

    def render_home(self):
        self.home_box = Canvas(self.root)
        welcome_msg = "Welcome back %s!\nWe have some new exercises for you!" %self.student.username
        self.menu_items["student"] = Label(self.home_box, text = self.student, font = self.med_font)
        self.menu_items["student"].grid(row = 0, column = 0, columnspan = 2)
        self.menu_items["welcome"] = Label(self.home_box, text = welcome_msg, font = self.head_font)
        self.menu_items["welcome"].grid(row = 1, column = 0, columnspan = 3)
        sorting_test = "Sorting Game - Test - Level "
        sorting_teach = "Sorting Game - Teach - Level "
        matching_test = "Matching Game - Test - Level "
        matching_teach = "Matching Game - Teach - Level "
        l = [0,2,4,6]

        for i in range(1,4):
            self.menu_items["sorting_test"] = Button(self.home_box, text = "%s %s" %(sorting_test, i), font = self.med_font, command=lambda data = ["Sorting","Test", i]: self.call_game_method(data))
            self.menu_items["sorting_teach"] = Button(self.home_box, text = "%s %s" %(sorting_teach, i), font = self.med_font, command=lambda data = ["Sorting","Teach", i]: self.call_game_method(data))
            self.menu_items["matching_test"] = Button(self.home_box, text = "%s %s" %(matching_test, i), font = self.med_font, command=lambda data = ["Matching","Test", i]: self.call_game_method(data))
            self.menu_items["matching_teach"] = Button(self.home_box, text = "%s %s" %(matching_teach, i), font = self.med_font, command=lambda data = ["Matching","Teach", i]: self.call_game_method(data))
            self.menu_items["sorting_test"].grid(row =l[i], column = 0)
            self.menu_items["sorting_teach"].grid(row = l[i], column = 1)
            self.menu_items["matching_test"].grid(row = l[i]+1, column =0)
            self.menu_items["matching_teach"].grid(row = l[i]+1, column =1)

        self.home_box.pack()

    def call_game_method(self, data):
        exercise = data[0]
        _type = data[1]
        _level = data[2]
        self.root.destroy()
        game = None
        if exercise == "Sorting":
            self.student.level = _level
            game = sorting.SortingGame(_type, self.student.level)
              
        elif exercise == "Matching":
            self.student.level = _level
            game = matching.MatchingGame(_type, self.student.level)
        if game != None:
            payload = game.get_gamedat()
            log_filename = "logs/%s-%s-%s-%s-%s.txt" %(self.student.username, payload["category"], \
                                                payload["exercise_type"], payload["exercise_level"],\
                                                str(datetime.datetime.now()).replace(" ", "-").replace(":", "."))
            if "verbose_logs" in payload.keys():
                with open(log_filename, 'w') as outfile:
                    for line in payload["verbose_logs"]:
                        outfile.write(line)
                payload["verbose_logs"] = log_filename
            else:
                payload["verbose_logs"] = "logs/test.txt"
            #client_response = submit_results(self.client, payload)
            test_responses(payload, self.DEBUG)
        self.build_root()

if __name__=='__main__':
    WordificationDriver()
    #test_responses({}, True)
