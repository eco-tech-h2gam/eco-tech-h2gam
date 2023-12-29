import streamlit as st
import base64
import os, glob
import platform
import subprocess

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

        for i in range(0,len(fileslist)):
            file_ = open(mypath + fileslist[i], "rb")
            contents = file_.read()
            data_url = base64.b64encode(contents).decode("utf-8")
            file_.close()

            st.markdown(
                f'<img src="data:image/gif;base64,{data_url}" alt="Pollutant GIF">',
                unsafe_allow_html=True,
            )
        
if __name__ == '__main__':
    subprocess.run(["python", "DownloadCAMSforecast.py"])
    subprocess.run(["python", "maps.py"])
    MyApp = app(platform.system(), os.path.dirname(os.path.abspath(__file__)) )
    MyApp.display_gifs()