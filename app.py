import streamlit as st
import base64
import os, glob, shutil
import platform
import pandas as pd
from datetime import datetime
from datetime import date
import yaml
import datetime
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
import datetime
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
import pytz
warnings.filterwarnings("ignore")  
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')

# Initialize a session using Amazon S3
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)
sys = platform.system()
work_dir = os.path.dirname(os.path.abspath(__file__))
today = date.today()  
print(today)

def chiffre_heure_actuelle_utc():
    time_format = "%H:%M"
    # Define the timezone for Paris
    paris_tz = pytz.timezone('Europe/Paris')
    # Get the current time in Paris (this is already a timezone-aware datetime object)
    paris_time = datetime.datetime.now(paris_tz)
    # Convert Paris time to UTC
    utc_time = paris_time.astimezone(pytz.utc)
    utc_hour = utc_time.hour
    return utc_hour

class app():

    def __init__(self, sys, work_dir):
        self.sys = sys
        self.work_dir = work_dir   
        self.bucket_name = 'eco-tech-h2gam'
        self.bucket_forecast_prefix = 'cams/fr/forecast/'
        self.bucket_PM25_prefix = 'PM25/'
        self.bucket_PM10_prefix = 'PM10/'
        self.bucket_CO_prefix = 'CO/'
        self.bucket_NO2_prefix = 'NO2/'
        self.bucket_SO2_prefix = 'SO2/'
        self.bucket_O3_prefix = 'O3/'
        self.s3 = boto3.client('s3')
        self.object_key_init_forecast = self.list_all_files_in_aws_s3_bucket(self.bucket_forecast_prefix)[1].split("/")[3]
        print(self.object_key_init_forecast)
        self.object_key_init_PM25 = self.list_all_files_in_aws_s3_bucket(self.bucket_PM25_prefix)[1].split("/")[1]
        self.object_key_init_PM10 = self.list_all_files_in_aws_s3_bucket(self.bucket_PM10_prefix)[1].split("/")[1]
        self.object_key_init_CO = self.list_all_files_in_aws_s3_bucket(self.bucket_CO_prefix)[1].split("/")[1]
        self.object_key_init_NO2 = self.list_all_files_in_aws_s3_bucket(self.bucket_NO2_prefix)[1].split("/")[1]
        print(self.object_key_init_NO2)
        self.object_key_init_SO2 = self.list_all_files_in_aws_s3_bucket(self.bucket_SO2_prefix)[1].split("/")[1]
        print(self.object_key_init_SO2)
        self.object_key_init_O3 = self.list_all_files_in_aws_s3_bucket(self.bucket_O3_prefix)[1].split("/")[1]
        print(self.object_key_init_O3)
        date_of_forecastfile = self.object_key_init_forecast.split(".")[0][-10:]
        print(date_of_forecastfile)
        date_of_forecastfile = pd.to_datetime(date_of_forecastfile, dayfirst= False)
        print(date_of_forecastfile)

    def download_pollutant_gif_init_from_s3(self, bucket_name, bucket_prefix, object_key, local_filename):
        # Create an S3 client
        s3 = boto3.client('s3')
        
        if not os.path.isfile(local_filename):
            full_object_key = bucket_prefix + object_key
            try:
                # Check if the object exists
                print(f"Checking existence of object: {full_object_key} in bucket: {bucket_name}")
                s3.head_object(Bucket=bucket_name, Key=full_object_key)
                
                # Download the file from S3
                print(f"Attempting to download {full_object_key} from bucket {bucket_name} to {local_filename}")
                s3.download_file(bucket_name, full_object_key, local_filename)
                print(f"Successfully downloaded {full_object_key} from {bucket_name} to {local_filename}")
            except s3.exceptions.NoSuchBucket:
                print(f"The bucket {bucket_name} does not exist.")
            except s3.exceptions.NoSuchKey:
                print(f"The object {full_object_key} does not exist in the bucket {bucket_name}.")
            except s3.exceptions.ClientError as e:
                if e.response['Error']['Code'] == '404':
                    print(f"Object {full_object_key} not found in bucket {bucket_name}.")
                else:
                    print(f"Client error: {e}")
            except Exception as e:
                print(f"Error downloading file: {e}")

    def list_all_files_in_aws_s3_bucket(self, bucket_prefix):
        file_list = []
        # Retrieve the list of files
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=bucket_prefix)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                file_list.append(obj['Key'])
        print(file_list)
        return file_list
    
    def get_latest_gif(self, folder_path):
        gifs = glob.glob(os.path.join(folder_path, '*.gif'))
        latest_gif = max(gifs, key=os.path.getctime)
        print(max(gifs, key=os.path.getctime))
        return latest_gif
    
    def return_path_to_gif(self, pollutant):
        if self.sys == "Windows":
            mypath = self.work_dir + "\\forecast\\fr\\" + pollutant + "\\"
        else:
            mypath = self.work_dir + "/forecast/fr/" + pollutant +"/"
        return mypath
       
    def display_gifs(self):

        os.chdir(self.return_path_to_gif("PM25"))
        
        #dateoffile1 = pd.to_datetime(self.get_latest_gif(self.return_path_to_gif("PM25")).split("_concentration-")[1].split(".")[0],dayfirst = False)
        #dateoffile2 = pd.to_datetime(self.get_latest_gif(self.return_path_to_gif("PM10")).split("_concentration-")[1].split(".")[0],dayfirst = False)
        #dateoffile3 = pd.to_datetime(self.get_latest_gif(self.return_path_to_gif("CO")).split("_concentration-")[1].split(".")[0],dayfirst = False)
        #dateoffile4 = pd.to_datetime(self.get_latest_gif(self.return_path_to_gif("NO2")).split("_concentration-")[1].split(".")[0],dayfirst = False)
        #dateoffile5 = pd.to_datetime(self.get_latest_gif(self.return_path_to_gif("SO2")).split("_concentration-")[1].split(".")[0],dayfirst = False)
        #dateoffile6 = pd.to_datetime(self.get_latest_gif(self.return_path_to_gif("O3")).split("_concentration-")[1].split(".")[0],dayfirst = False)
        print("Debug good 1", self.object_key_init_PM25.split(".")[0][-10:])
        print("Debug good 2",self.object_key_init_PM10.split(".")[0][-10:])
        dateoffile1 = pd.to_datetime(self.object_key_init_PM25.split(".")[0][-10:], dayfirst = False)
        dateoffile2 = pd.to_datetime(self.object_key_init_PM10.split(".")[0][-10:], dayfirst = False)
        dateoffile3 = pd.to_datetime(self.object_key_init_CO.split(".")[0][-10:], dayfirst = False)
        dateoffile4 = pd.to_datetime(self.object_key_init_NO2.split(".")[0][-10:], dayfirst = False)
        dateoffile5 = pd.to_datetime(self.object_key_init_SO2.split(".")[0][-10:], dayfirst = False)
        dateoffile6 = pd.to_datetime(self.object_key_init_O3.split(".")[0][-10:], dayfirst = False)
        
        
        print (chiffre_heure_actuelle_utc())
        if (((pd.Timestamp(datetime.date.today()) - dateoffile1 > pd.Timedelta("1 days")))|\
    (((pd.Timestamp(datetime.date.today()) - dateoffile2) > pd.Timedelta("1 days"))) |\
    (((pd.Timestamp(datetime.date.today()) - dateoffile3) > pd.Timedelta("1 days"))) |\
    (((pd.Timestamp(datetime.date.today()) - dateoffile4) > pd.Timedelta("1 days"))) |\
    (((pd.Timestamp(datetime.date.today()) - dateoffile5) > pd.Timedelta("1 days"))) |\
    (((pd.Timestamp(datetime.date.today()) - dateoffile6) > pd.Timedelta("1 days")))):
            print (chiffre_heure_actuelle_utc())
            if self.sys == "Windows":
                print("Executing Download script in a Windows environment...")
                with open(self.work_dir + "\\DownloadCAMSforecast.py", 'r') as file:
                    script_contents = file.read()
                exec(script_contents)
                print("Finished Download Script")
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

        else:
            self.download_pollutant_gif_init_from_s3(self.bucket_name,self.bucket_PM25_prefix, self.object_key_init_PM25, self.return_path_to_gif("PM25") + self.object_key_init_PM25)
            self.download_pollutant_gif_init_from_s3(self.bucket_name,self.bucket_PM10_prefix, self.object_key_init_PM10, self.return_path_to_gif("PM10") + self.object_key_init_PM10)
            self.download_pollutant_gif_init_from_s3(self.bucket_name,self.bucket_CO_prefix, self.object_key_init_CO, self.return_path_to_gif("CO") + self.object_key_init_CO)
            self.download_pollutant_gif_init_from_s3(self.bucket_name,self.bucket_SO2_prefix, self.object_key_init_SO2, self.return_path_to_gif("SO2") + self.object_key_init_SO2)
            self.download_pollutant_gif_init_from_s3(self.bucket_name,self.bucket_NO2_prefix, self.object_key_init_NO2, self.return_path_to_gif("NO2") + self.object_key_init_NO2)
            self.download_pollutant_gif_init_from_s3(self.bucket_name,self.bucket_O3_prefix, self.object_key_init_O3, self.return_path_to_gif("O3") + self.object_key_init_O3)

        file_1 = open(self.get_latest_gif(self.return_path_to_gif("PM25")), "rb")
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