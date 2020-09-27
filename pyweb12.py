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
    
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        
        global ALL_DATA

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

        elif ("setupprofile" in self.requestline):
            self.setup_file = open("./setupPage.html")
            self.setup_file_lines = self.setup_file.readlines()
            for line in self.setup_file_lines:
                self.wfile.write(bytes(line, "utf-8"))
            firstEqual = self.requestline.index("=")
            andSign = self.requestline.index("&", firstEqual)
            secondEqual = self.requestline.index("=", firstEqual+1)
            httpIndex = self.requestline.index("HTTP", secondEqual)
            username = self.requestline[firstEqual+1: andSign]
            pwd = self.requestline[secondEqual+1: httpIndex-1]
            
##          (input, username, pwd) = self.rfile.read(content_length).decode('utf-8').split('=')
##          username = urllib.parse.unquote_plus(username)[:-6]
##          pwd = urllib.parse.unquote_plus(pwd)
            
            print("username: ", username)
            print("pwd: ", pwd)
            
            ALL_DATA.add_usr(username, pwd)
            ALL_DATA.save()

            ALL_DATA.debug_print()

        else: #main webpage
            if (ALL_DATA == None):
                ALL_DATA = Data()

            #if not os.path.isfile("dict.pickle"):
                #f = open("dict.pickle", "w+")
                #f.close()
        
            #if os.path.getsize("dict.pickle") > 0:
                #pickle_in = open("dict.pickle","rb")
                #userInfo = pickle.load(pickle_in)
                
            html_file = open("./mydesign1.html")
            html_file_lines = html_file.readlines()
            for line in html_file_lines:
                self.wfile.write(bytes(line, "utf-8"))

    def do_POST(self):
        #self._set_headers()
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        print(post_body)
        

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")