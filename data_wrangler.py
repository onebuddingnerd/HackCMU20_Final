import os
import pandas as pd #for data frame
import numpy as np
import pickle


class Data():
    def __init__(self):
        self.USER_DATA = dict()
        
        # no user data backup yet
        if not os.path.isfile("alldata.pickle"):
            f = open("alldata.pickle", "w+") # backup file creation
            f.close()

        else: # restore
            self.reload()

        self.NUTRITION_DATA = pd.read_csv('./cmu_nutrition.csv')

    def debug_print(self):
        print('cmu_nutrition')
        #print(self.NUTRITION_DATA['Cal'])

        for k in self.USER_DATA.keys():
            print(k)
            print(self.USER_DATA[k])

    def add_usr(self, name, pwd):
        new_usr_dict = dict()
        new_usr_dict['pwd'] = pwd
        self.USER_DATA[name] = new_usr_dict
        self.save()

    def save(self):
        pickle_out = open("alldata.pickle","wb")
        pickle.dump(self.USER_DATA, pickle_out)
        pickle_out.close()

    def reload(self):
        if os.path.getsize("alldata.pickle") > 0:
            pickle_in = open("alldata.pickle","rb")
            self.USER_DATA = pickle.load(pickle_in)

        else:
            print('***\nERROR: 0sized USER_DATA!\n***')





