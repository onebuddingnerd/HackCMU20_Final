# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib
import pickle
from os import path
import os

# import all user data class
from data_wrangler import Data

hostName = "localhost"
serverPort = 8080

ALL_DATA = None

def parse_assist(s):
    s = s.replace('+',' ')
    s = s.replace('%2F','/')
    s = s.replace('%3F','?')
    return s
    
def init_profiler(usr):
    global ALL_DATA
    usr_info = ALL_DATA.USER_DATA[usr]

    usr_gender = usr_info['Gender']
    usr_height = float(int(usr_info['height'])) * 2.54 #cm
    usr_weight = float(int(usr_info['weight'])) / 2.2 #kg
    usr_age = float(int(usr_info['age']))

    usr_bmr = None
    if usr_gender == 'male':
        usr_bmr = 66.47 + (13.75 * usr_weight) + (5.003 * usr_height) - (6.755 * usr_age)
    else:
        usr_bmr = 655.1 +(9.563 * usr_weight) + (1.85 * usr_height) - (4.676 * usr_age)

    usr_info['bmr'] = usr_bmr

def get_demo_meals():
    meal1 = {"Name":"Veggie Wrap", "Restaurant":"Zebra Lounge","Cal":300}
    meal2 = {"Name":"Italian Sub", "Restaurant":"Zebra Lounge","Cal":550}
    meal3 = {"Name":"Ham Sandwich", "Restaurant":"Ginger's Express","Cal":400}
    meal4 = {"Name":"Fruit and Nut Salad", "Restaurant":"Ginger's Express","Cal":300}
    meal5 = {"Name":"Chicken Ceasar Wrap", "Restaurant":"Au Bon Pain","Cal":480}
    return [meal1,meal2,meal3,meal4,meal5]


def init_recommender(usr):
    global ALL_DATA
    NDAT = ALL_DATA.NUTRITION_DATA

    usr_info = ALL_DATA.USER_DATA[usr]
    bmr = usr_info['bmr']
    caloric_matches = NDAT.loc[(NDAT['Cal'] >= bmr/7) & (NDAT['Cal'] <= bmr/4)]

    caloric_matches_random = caloric_matches.sample(4)
    usr_info['random meals'] = caloric_matches_random.T.to_dict().values()


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        
        global ALL_DATA
        global STATE

        print("REQUEST LINE: ",self.requestline)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        if ("login" in self.requestline):
            self.login_file = open("./loginPage.html")
            self.login_file_lines = self.login_file.readlines()
            for line in self.login_file_lines:
                self.wfile.write(bytes(line, "utf-8"))

        elif ("signup" in self.requestline):
            self.signup_file = open("./signupPage.html")
            self.signup_file_lines = self.signup_file.readlines()
            for line in self.signup_file_lines:
                self.wfile.write(bytes(line, "utf-8"))
            
        elif ("dashboard" in self.requestline):
            self.dasbrd_file = open("./usr_dashboard.html")
            self.dasbrd_file_lines = self.dasbrd_file.readlines()
            for line in self.dasbrd_file_lines:
                self.wfile.write(bytes(line, "utf-8"))

        else: #main webpage
            if (ALL_DATA == None):
                ALL_DATA = Data()
            html_file = open("./mydesign1.html")
            html_file_lines = html_file.readlines()
            for line in html_file_lines:
                self.wfile.write(bytes(line, "utf-8"))

    def do_POST(self):
        global ALL_DATA
        global STATE

        content_length = int(self.headers['Content-Length'])
        
        #body = self.rfile.read(content_length)
        #print(body)
        print("POST:", self.requestline)
        if ("setupPage" in self.requestline): #sign up preceded this
            (input,username,pwd) = self.rfile.read(content_length).decode('utf-8').split('=')
            username = urllib.parse.unquote_plus(username)[:-6]
            pwd = urllib.parse.unquote_plus(pwd)
            print("username: ", username)
            print("pwd: ", pwd)
            ALL_DATA.add_usr(username, pwd)
            ALL_DATA.save()
            ALL_DATA.debug_print()
            STATE.curr_user = username
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            self.setup_file = open("./setupPage.html")
            self.setup_file_lines = self.setup_file.readlines()
            for line in self.setup_file_lines:
                self.wfile.write(bytes(line, "utf-8"))

        # elif ("dashboardReturn" in self.requestline)   #IF HAVE TIME
                
        elif("dashboard" in self.requestline): # setup preceded this
            print("goes into setupPage")
            (v0,v1,v2,v3,v4,v5,v6,v7,v8) = self.rfile.read(content_length).decode('utf-8').split('=')
            replies = [v0,v1,v2,v3,v4,v5,v6,v7,v8]

            curr_reply, curr_prompt,next_prompt = None, None, None
            for i in range(len(replies)):
                v = replies[i]
                if i == 0:
                    curr_prompt = replies[0]
                elif i < len(replies) - 1:
                    curr_reply, next_prompt = v.split("&")
                    curr_prompt = parse_assist(curr_prompt)
                    curr_reply = parse_assist(curr_reply)
                    (ALL_DATA.USER_DATA[STATE.curr_user])[curr_prompt] = curr_reply
                    curr_prompt = next_prompt
                else:
                    curr_reply = parse_assist(replies[i])
                    curr_prompt = parse_assist(curr_prompt)
                    (ALL_DATA.USER_DATA[STATE.curr_user])[curr_prompt] = curr_reply

            #print(ALL_DATA.USER_DATA[STATE.curr_user])
            init_profiler(STATE.curr_user)
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            html_file = open("./usr_dashboard.html")
            html_file_lines = html_file.readlines()
            for line in html_file_lines:
                self.wfile.write(bytes(line, "utf-8")) #would need to change

        elif ("feedback" in self.requestline): #dashboard preceded this
            (v0,v1,v2,v3,v4,v5) = self.rfile.read(content_length).decode('utf-8').split('=')
            replies = [v0,v1,v2,v3,v4,v5]

            curr_reply, curr_prompt,next_prompt = None, None, None
            for i in range(len(replies)):
                v = replies[i]
                if i == 0:
                    curr_prompt = replies[0]
                elif i < len(replies) - 1:
                    curr_reply, next_prompt = v.split("&")
                    curr_prompt = parse_assist(curr_prompt)
                    curr_reply = parse_assist(curr_reply)
                    (ALL_DATA.USER_DATA[STATE.curr_user])[curr_prompt] = curr_reply
                    curr_prompt = next_prompt
                else:
                    curr_reply = parse_assist(replies[i])
                    curr_prompt = parse_assist(curr_prompt)
                    (ALL_DATA.USER_DATA[STATE.curr_user])[curr_prompt] = curr_reply

            #init_rec_demo()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_file  = open("./feedback1.html")
            html_file_lines = html_file.readlines()
            for line in html_file_lines:
                self.wfile.write(bytes(line, "utf-8"))
                
            #write variable part
            self.summarize_and_write(STATE.curr_user)

            html_file  = open("./feedback2.html")
            html_file_lines = html_file.readlines()
            for line in html_file_lines:
                self.wfile.write(bytes(line, "utf-8"))
            
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_file = open("./mydesign1.html")
            html_file_lines = html_file.readlines()
            for line in html_file_lines:
                self.wfile.write(bytes(line, "utf-8"))

    def summarize_and_write(self, usr):
        usr_info = ALL_DATA.USER_DATA[usr]
        #print(usr_info)
        usr_info['demo meals'] = get_demo_meals()
        
        # link interested responses to meals
        i = 1
        for meal_dict in usr_info['demo meals']:

            meal_dict['Interested ' + str(i)] = usr_info['Interested ' + str(i)]
            i += 1

        for k in usr_info.keys():
            if (not (k == 'demo meals')) and (not "Interest" in k) and (not (k == 'pwd')): 
                strk = k
                if k == "weightplan": strk = "Weight Plan"
                elif k == 'weight': strk = "Weight"
                elif k == 'height': strk = "Height" 
                elif k == "What is your favorite genre of food?": strk = "Favorite Genre Of Food"
                elif k == "genre": strk = "Genre (other)"
                elif k == "genre": strk = "Genre (other)"
                elif k == "on/off campus?": strk = "On/Off Campus"
                elif k == "activity": strk = "Activity"
                elif k == 'age': strk = 'Age'
                elif k == 'bmr': strk = 'BMR'
                info_line = '<tr> <td> <b>' + strk + '</b> </td> ' + ' <td> ' + str(usr_info[k]) + '</td> </tr>'
                self.wfile.write(bytes(info_line, 'utf-8'))
                    

class State:
    def __init__(self):
        self.curr_user = "" #overwrite

STATE = State()

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
    print("Server stopped.")
