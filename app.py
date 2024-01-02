import streamlit as st
import base64
import os, glob, shutil
import platform
import subprocess
import pandas as pd
import datetime as dt
from datetime import datetime
from datetime import date


class app():

    def __init__(self, sys, work_dir):
        self.sys = sys
        self.work_dir = work_dir   
        
    def display_gifs(self):
        if self.sys == "Windows":
            mypath = self.work_dir + "\\forecast\\fr\\"
        else:
            mypath = self.work_dir + "/forecast/fr/" 
        os.chdir(mypath)
        fileslist = []
        for file in glob.glob("*.gif"):
            print(file)
            fileslist.append(file)

        dateoffile = pd.to_datetime(fileslist[0].split("_concentration-")[1].split(".")[0],dayfirst = False)
        print(pd.Timestamp(date.today())  - dateoffile)
        if(pd.Timestamp(date.today())  - dateoffile > pd.Timedelta("1 Days")):
            print(pd.Timestamp(date.today())  - dateoffile)
            print("IN HERE")
            if self.sys == "Windows":
                subprocess.run("python " + self.work_dir + "\\DownloadCAMSforecast.py")
                subprocess.run("python " +  self.work_dir + "\\maps.py")
            else:
                subprocess.run(["python", self.work_dir + "/DownloadCAMSforecast.py"])
                subprocess.run(["python", self.work_dir + "/maps.py"])

        file_1 = open(mypath + fileslist[0], "rb")
        contents = file_1.read()
        data_url1 = base64.b64encode(contents).decode("utf-8")
        file_1.close()

        file_2 = open(mypath + fileslist[1], "rb")
        contents = file_2.read()
        data_url2 = base64.b64encode(contents).decode("utf-8")
        file_2.close()

        file_3 = open(mypath + fileslist[2], "rb")
        contents = file_3.read()
        data_url3 = base64.b64encode(contents).decode("utf-8")
        file_3.close()

        # HTML code to display gifs side by side
        html_code1 = f"""
            <div style="display: flex; justify-content: space-between;">
                <img src="data:image/gif;base64,{data_url1}" alt="GIF 1" style="width: 28%;" loop = True>
                <img src="data:image/gif;base64,{data_url2}" alt="GIF 2" style="width: 28%;" loop = True>
                <img src="data:image/gif;base64,{data_url3}" alt="GIF 3" style="width: 28%;" loop = True>
            </div>
        """

        file_4 = open(mypath + fileslist[3], "rb")
        contents = file_4.read()
        data_url4 = base64.b64encode(contents).decode("utf-8")
        file_4.close()

        file_5 = open(mypath + fileslist[4], "rb")
        contents = file_5.read()
        data_url5 = base64.b64encode(contents).decode("utf-8")
        file_5.close()

        file_6 = open(mypath + fileslist[5], "rb")
        contents = file_6.read()
        data_url6 = base64.b64encode(contents).decode("utf-8")
        file_6.close()

        # HTML code to display gifs side by side
        html_code2 = f"""
            <div style="display: flex; justify-content: space-between;">
                <img src="data:image/gif;base64,{data_url4}" alt="GIF 4" style="width: 28%;" loop = True>
                <img src="data:image/gif;base64,{data_url5}" alt="GIF 5" style="width: 28%;" loop>
                <img src="data:image/gif;base64,{data_url6}" alt="GIF 6" style="width: 28%;" loop>
            </div>
        """
        
        # Display the HTML code
        st.markdown(html_code1, unsafe_allow_html=True)
        st.markdown(html_code2, unsafe_allow_html=True)

if __name__ == '__main__':
    MyApp = app(platform.system(), os.path.dirname(os.path.abspath(__file__)) )
    MyApp.display_gifs()