import os, shutil
from datetime import date
import datetime as dt
import cdsapi
import yaml
import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm
from os import listdir
from os.path import isfile, join
import urllib3
urllib3.disable_warnings()
import platform
import boto3
import os
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

# Use the session to create a resource

class download_cams_forecast:
    
    def __init__(self):
        self.work_dir = None
        self.save_to = None
        self.bucket_name = 'eco-tech-h2gam'
        self.bucket_prefix = 'cams/fr/forecast/'
        self.s3 = boto3.client('s3')
        self.object_key_init_forecast = self.list_all_files_in_aws_s3_bucket()[1].split("/")[3]
        print(self.object_key_init_forecast)
    
    def list_all_files_in_aws_s3_bucket(self):
        file_list = []
        # Retrieve the list of files
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=self.bucket_prefix)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                file_list.append(obj['Key'])
        print(file_list)
        return file_list

    
    def delete_previous_file_from_aws_and_save_new_file_to_aws(self, object_key, outputfile):
        # Delete the previous file from the S3 bucket
        if self.object_key_init_forecast:
            key = self.bucket_prefix + object_key
            print("Debug",key)
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            print(f"Deleted {self.object_key_init_forecast} from S3 bucket.")

        # Upload the new file to the S3 bucket
        new_object_key = f"{self.bucket_prefix}{os.path.basename(outputfile)}"
        self.s3.upload_file(outputfile, self.bucket_name, new_object_key)
        print(f"Uploaded {outputfile} to S3 bucket as {new_object_key}.")

    
    def download(self):
        print("Downloading CAMS data...")
        sys = platform.system()
        self.work_dir = os.path.dirname(os.path.abspath(__file__))
        
        print("sys:", sys)
        if sys == "Windows":
            self.save_to = os.path.join(self.work_dir, "cams", "fr", "forecast")
        else:
            self.save_to = os.path.join(self.work_dir, "cams", "fr", "forecast")

        folder = self.save_to
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        
        print("System:", sys) 

        if not os.path.exists(self.save_to):
            os.makedirs(self.save_to)

        # get personal directory of cdsapi
        try:
            if sys == "Windows":
                with open(os.path.join(self.work_dir, ".cdsapirc_cams_windows"), 'r') as file:
                    cams_api = os.path.join(self.work_dir, ".cdsapirc")
            else:
                with open(os.path.join(self.work_dir, ".cdsapirc_cams"), "r") as file:
                    cams_api = os.path.join(self.work_dir, ".cdsapirc")
        except FileNotFoundError:
            raise FileNotFoundError("""cdsapirc file cannot be found. Write the
                directory of your personal .cdsapirc file in a local file called
                `.cdsapirc_cams` and place it in the directory where this script lies.""")

        # Download CAMS
        # -----------------------------------------------------------------------------
        print('Download data from CAMS ...', flush=True)

        with open(cams_api, 'r') as f:
            credentials = yaml.safe_load(f)

        mypath = os.path.join(self.work_dir, "cams")

        def findlatestdateofcamsdata(mypath):
            dates = []
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            for filename in onlyfiles:
                dates.append(pd.to_datetime(filename[14:24]))
            
            if dates:
                return (dates, max(dates))
            else:
                return (dates, dt.date.today() - pd.Timedelta(1, unit="days"))

        prevday = dt.date.today() - pd.Timedelta("1 days")
        startdate = findlatestdateofcamsdata(mypath)[1]
        datesnotclean = pd.date_range(start=startdate, end=prevday).strftime("%Y-%m-%d").tolist()
        
        dates = []

        for date in datesnotclean:
            if date not in pd.to_datetime(findlatestdateofcamsdata(mypath)[0]):
                dates.append(date)

        print(dates)

        area = [51.75, -5.83, 41.67, 11.03]

        for date in tqdm(dates):
            print(date)
            file_name = f'cams-forecast-{date}.nc'
            output_file = os.path.join(self.save_to, file_name)
            if not os.path.exists(output_file):
                c = cdsapi.Client(url=credentials['url'], key=credentials['key'])
                c.retrieve(
                    'cams-europe-air-quality-forecasts',
                    {
                        'variable': [
                            'carbon_monoxide', 'nitrogen_dioxide', 'ozone',
                            'particulate_matter_10um', 'particulate_matter_2.5um', 'sulphur_dioxide',
                        ],
                        'model': 'ensemble',
                        'level': '0',
                        'date': date,
                        'type': 'forecast',
                        'time': '00:00',
                        'leadtime_hour': [
                            '0', '24', '48',
                            '72', '96'
                        ],
                        'area': area,
                        'format': 'netcdf',
                    },
                    output_file)
        self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.object_key_init_forecast, output_file)
        print('Download finished.', flush=True)

if __name__ == '__main__':
    CamsHistForecasts = download_cams_forecast()
    CamsHistForecasts.download()
