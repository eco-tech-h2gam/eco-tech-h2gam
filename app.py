import streamlit as st
import base64
import os, glob, shutil
import platform
import pandas as pd
from datetime import datetime
from datetime import date
import yaml
import datetime as dt
import cdsapi
import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm
from os import listdir
from os.path import isfile, join
import urllib3
urllib3.disable_warnings()
import sys
import platform
import os, shutil
import datetime as dt
from datetime import datetime
from datetime import date
import regionmask
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
import seaborn as sns
import io
import imageio
from tqdm import tqdm  
import boto3
import warnings
warnings.filterwarnings("ignore")  

sys = platform.system()
work_dir = os.path.dirname(os.path.abspath(__file__))
today = date.today()  
print(today)

class app():

    def __init__(self, sys, work_dir):
        self.sys = sys
        self.work_dir = work_dir   

    def get_latest_gif(self, folder_path):
        gifs = glob.glob(os.path.join(folder_path, '*.gif'))
        latest_gif = max(gifs, key=os.path.getctime)
        return latest_gif
    
    def return_path_to_gif(self, pollutant):
        if self.sys == "Windows":
            mypath = self.work_dir + "\\forecast\\fr\\" + pollutant + "\\"
        else:
            mypath = self.work_dir + "/forecast/fr/" + pollutant +"/"
        return mypath
       
    def display_gifs(self):

        os.chdir(self.return_path_to_gif("PM2.5"))


        dateoffile = pd.to_datetime(self.get_latest_gif(self.return_path_to_gif("PM2.5")).split("_concentration-")[1].split(".")[0],dayfirst = False)
        print(pd.Timestamp(date.today())  - dateoffile)
        if(pd.Timestamp(date.today())  - dateoffile > pd.Timedelta("1 Days")):
            print(pd.Timestamp(date.today())  - dateoffile)
            print("IN HERE")
            if self.sys == "Windows":
                with open(self.work_dir + "\\DownloadCAMSforecast.py", 'r') as file:
                    script_contents = file.read()
                exec(script_contents)
                with open(self.work_dir + "\\maps.py", 'r') as file:
                    script_contents = file.read()
                exec(script_contents)
            else:
                with open(self.work_dir + "/DownloadCAMSforecast.py", 'r') as file:
                    script_contents = file.read()
                exec(script_contents)
                with open(self.work_dir + "/maps.py", 'r') as file:
                    script_contents = file.read()
                exec(script_contents)

        file_1 = open(self.get_latest_gif(self.return_path_to_gif("PM2.5")), "rb")
        contents = file_1.read()
        data_url1 = base64.b64encode(contents).decode("utf-8")
        file_1.close()

        file_2 = open(self.get_latest_gif(self.return_path_to_gif("PM10")), "rb")
        contents = file_2.read()
        data_url2 = base64.b64encode(contents).decode("utf-8")
        file_2.close()

        file_3 = open(self.get_latest_gif(self.return_path_to_gif("CO")), "rb")
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

        file_4 = open(self.get_latest_gif(self.return_path_to_gif("NO2")), "rb")
        contents = file_4.read()
        data_url4 = base64.b64encode(contents).decode("utf-8")
        file_4.close()

        file_5 = open(self.get_latest_gif(self.return_path_to_gif("SO2")), "rb")
        contents = file_5.read()
        data_url5 = base64.b64encode(contents).decode("utf-8")
        file_5.close()

        file_6 = open(self.get_latest_gif(self.return_path_to_gif("O3")), "rb")
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