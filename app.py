import streamlit as st
import base64
import os, glob
import platform
import subprocess

# Run the other script






class app:

    def __init__(self):
        self.sys = platform.system()
        self.work_dir = os.path.dirname(os.path.abspath(__file__))   
        if self.sys == "Windows":
            self.mypath = self.work_dir + "\\forecast\\fr\\"
        else:
            self.mypath = self.work_dir + "/forecast/fr/" 

        

    def display_gifs(self):
        os.chdir(self.mypath)
        fileslist = []
        for file in glob.glob("*.gif"):
            print(file)
            fileslist.append(file)

        for i in range(0,len(fileslist)):
            file_ = open(self.mypath + fileslist[i], "rb")
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
    MyApp = app()
    MyApp.display_gifs()