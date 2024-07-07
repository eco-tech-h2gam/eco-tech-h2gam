import sys
import platform
import os, shutil
import datetime as dt
from datetime import datetime
from datetime import date
import numpy as np
import pandas as pd
import xarray as xr
import regionmask
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
import seaborn as sns
import io
import imageio
from os import listdir
from os.path import isfile, join
from tqdm import tqdm  
import warnings
import boto3
warnings.filterwarnings("ignore")  
sys = platform.system()
work_dir = os.path.dirname(os.path.abspath(__file__))
today = date.today()  
print(today)
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
class compute_maps:
    def __init__(self):
        self.status = None
        self.data = None
        self.bucket_name = 'eco-tech-h2gam'
        self.bucket_name_prefix_forecast = 'cams/fr/forecast/'
        self.bucket_name_prefix_PM25 = 'PM25/'
        self.bucket_name_prefix_PM10 = 'PM10/'
        self.bucket_name_prefix_CO = 'CO/'
        self.bucket_name_prefix_NO2 = 'NO2/'
        self.bucket_name_prefix_SO2 = 'SO2/'
        self.bucket_name_prefix_O3 = 'O3/'

        self.object_key1 = 'pop.csv'  # Path to your CSV file in the S3 bucket
        self.object_key2 = 'Enriched_Covid_history_data.csv'  # Path to your CSV file in the S3 bucket
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

        if sys == "Windows":
            self.local_filename1 = work_dir + '\\pop.csv'  # Local file path to save the downloaded file
            self.local_filename2 = work_dir + '\\Enriched_Covid_history_data.csv'  # Local file path to save the downloaded file
            self.local_filename_init_PM25 = self.return_path_to_gif("PM25") + "\\PM25_concentration-2024-06-30.gif"
            self.local_filename_init_PM10 = self.return_path_to_gif("PM10") + "\\PM10_concentration-2024-06-30.gif"
            self.local_filename_init_CO = self.return_path_to_gif("CO") + "\\CO_concentration-2024-06-30.gif"
            self.local_filename_init_NO2 = self.return_path_to_gif("NO2") + "\\NO2_concentration-2024-06-30.gif"
            self.local_filename_init_SO2 = self.return_path_to_gif("SO2") + "\\SO2_concentration-2024-06-30.gif"
            self.local_filename_init_O3 = self.return_path_to_gif("O3") + "\\O3_concentration-2024-06-30.gif"
        else:
            self.local_filename1 = work_dir + '/pop.csv'  # Local file path to save the downloaded file
            self.local_filename2 = work_dir + '/Enriched_Covid_history_data.csv'  # Local file path to save the downloaded file
            self.local_filename_init_PM25 = self.return_path_to_gif("PM25") + "/PM25_concentration-2024-06-30.gif"
            self.local_filename_init_PM10 = self.return_path_to_gif("PM10") + "/PM10_concentration-2024-06-30.gif"
            self.local_filename_init_CO =self.return_path_to_gif("CO") + "/CO_concentration-2024-06-30.gif"
            self.local_filename_init_NO2 = self.return_path_to_gif("NO2") + "/NO2_concentration-2024-06-30.gif"
            self.local_filename_init_SO2 = self.return_path_to_gif("SO2") + "/SO2_concentration-2024-06-30.gif"
            self.local_filename_init_O3 = self.return_path_to_gif("O3") + "/O3_concentration-2024-06-30.gif"

    def list_all_files_in_aws_s3_bucket(self, bucket_prefix):
        file_list = []
        # Retrieve the list of files
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=bucket_prefix)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                file_list.append(obj['Key'])
        print(file_list)
        return file_list
    
    def delete_previous_file_from_aws_and_save_new_file_to_aws(self, bucket_prefix, object_key, outputfile):
        # Delete the previous file from the S3 bucket
        if self.object_key_init_forecast:
            key = bucket_prefix + object_key
            print("Debug",key)
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            print(f"Deleted {self.object_key_init_forecast} from S3 bucket.")

        # Upload the new file to the S3 bucket
        new_object_key = f"{bucket_prefix}{os.path.basename(outputfile)}"
        self.s3.upload_file(outputfile, self.bucket_name, new_object_key)
        print(f"Uploaded {outputfile} to S3 bucket as {new_object_key}.")

    def return_path_to_gif(self, pollutant):
        if sys == "Windows":
            mypath = work_dir + "\\forecast\\fr\\" + pollutant + "\\"
        else:
            mypath = work_dir + "/forecast/fr/" + pollutant +"/"
        return mypath
    
    def max_normalize(self, x):
        return (x - x.min()) / (x.max() - x.min())
    
    def findlatestdateofcamsdata(self, mypath):
            dates = []
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            for filename in onlyfiles:
                dates.append(pd.to_datetime(filename[14:24], dayfirst = False))
                print(dates)
            
            if dates != []:
                return (dates, max(dates))
            else:
                with open(self.work_dir + "/DownloadCAMSforecast.py", 'r') as file:
                    script_contents = file.read()
                exec(script_contents)
                self.findlatestdateofcamsdata(mypath)

    def download_pollutant_gif_init_from_s3(self, bucket_name, object_key, local_filename):
        # Create an S3 client
        s3 = boto3.client('s3')
        try:
            # Download the CSV file from S3
            s3.download_file(bucket_name, object_key, local_filename)
            print(f"Successfully downloaded {object_key} from {bucket_name} to {local_filename}")
        except Exception as e:
            print(f"Error downloading file: {e}")
    
    def download_forecast_init_from_s3(self, bucket_name, object_key, local_filename):
        # Create an S3 client
        s3 = boto3.client('s3')
        try:
            # Download the CSV file from S3
            s3.download_file(bucket_name, object_key, local_filename)
            print(f"Successfully downloaded {object_key} from {bucket_name} to {local_filename}")
        except Exception as e:
            print(f"Error downloading file: {e}")


    def download_csv_from_s3(self, bucket_name, object_key, local_filename):
        # Create an S3 client
        s3 = boto3.client('s3')

        try:
            # Download the CSV file from S3
            s3.download_file(bucket_name, object_key, local_filename)
            print(f"Successfully downloaded {object_key} from {bucket_name} to {local_filename}")
        except Exception as e:
            print(f"Error downloading file: {e}")

    def compute_maps(self):
        # Set up AWS credentials
        boto3.setup_default_session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

        # Download the CSV file from S3
        if not os.path.exists(self.local_filename1):
            self.download_csv_from_s3(self.bucket_name, self.object_key1, self.local_filename1)
        if not os.path.exists(self.local_filename2):
            self.download_csv_from_s3(self.bucket_name, self.object_key2, self.local_filename2)
        currentDate = pd.to_datetime(today, dayfirst = False)
        grayDark = '#e1e1e1'
        grayLight = '#404040'

        sns.set(
        context 	= 'paper',
        style 		= 'dark',
        palette 	= 'muted',
        color_codes = True,
            font_scale  = 2.0,
        font 		= 'sans-serif',
#         rc={
#             'axes.edgecolor'	: grayDark
#             ,'text.color' 		: grayDark
#             ,'axes.labelcolor' 	: grayDark
#             ,'xtick.color' 		: grayDark
#             ,'ytick.color' 		: grayDark
# #                ,'figure.facecolor' : grayDark
#  #               ,'axes.facecolor'   : grayDark
#  #               ,'savefig.facecolor': grayDark
#             }
        )

        print('Data pre-processing:', flush=True)

        countryEU = regionmask.defined_regions.natural_earth_v5_0_0
    
        times = ["0 days","1 days","2 days", "3 days",'4 days']
        counter = 0
        images1 = []
        images2 = []
        images3 = []
        images4 = []
        images5 = []
        images6 = []
        images7 = []

        risk1Maps = []
        risk2Maps = []
        risk3Maps = []
        risk4Maps = []
        risk5Maps = []
        risk6Maps = []
        newhospipredmaps = []
        

        # covidExtraToCom[['1MMaxpm25','1MMaxpm10','1MMaxo3','1MMaxno2','1MMaxco','pm107davg','pm257davg','o37davg','no27davg','co7davg','pm101Mavg',\
        #   'pm251Mavg','o31Mavg','no21Mavg','co1Mavg','population','hospi','CovidPosTest' ]] \
        #     = [dfpollution3[dfpollution3['numero'] == depNum].reindex(columns = ['1MMaxpm25','1MMaxpm10','1MMaxo3','1MMaxno2','1MMaxco','pm107davg','pm257davg','o37davg','no27davg','co7davg','pm101Mavg',\
        #   'pm251Mavg','o31Mavg','no21Mavg','co1Mavg','idx','hospi','CovidPosTest' ]).values.squeeze() for depNum in covidExtraToCom['dep']]
        if sys == "Windows":
            filePath = work_dir + "\\cams\\fr\\forecast\\"
        else:
            filePath = work_dir + '/cams/fr/forecast/'

        self.download_forecast_init_from_s3(self.bucket_name, self.bucket_name_prefix_forecast, filePath + self.object_key_init_forecast)
        for j in tqdm(times):
            print(j)
            # filename = "/home/ludo915/code/covsco/predictions/fr/" + currentDatestring + "_predictions_for_day_" + str(counter) +".csv"
            # newhospipredictionsdf = pd.read_csv(filename)
            # print(filename + " Read!")
 
            latestfiledatestring = self.findlatestdateofcamsdata(filePath)[1].strftime('%Y-%m-%d')
            currentDatestring = pd.to_datetime(latestfiledatestring, dayfirst = False).strftime('%Y-%m-%d')
            print("lastdate:", latestfiledatestring)
            fileName = "cams-forecast-"+latestfiledatestring +".nc"
            pollutants = xr.open_dataset(filePath + fileName).sel(time = j)

            pm25 = pollutants.pm2p5_conc
            o3 = pollutants.o3_conc
            no2 = pollutants.no2_conc
            co = pollutants.co_conc
            pm10 = pollutants.pm10_conc
            so2 = pollutants.so2_conc

            pm25 = pm25.drop('time').squeeze().drop('level').squeeze()
            o3 = o3.drop('time').squeeze().drop('level').squeeze()
            no2 = no2.drop('time').squeeze().drop('level').squeeze()
            co = co.drop('time').squeeze().drop('level').squeeze()
            pm10 = pm10.drop('time').squeeze().drop('level').squeeze()
            so2 = so2.drop('time').squeeze().drop('level').squeeze()

            pm25.coords['longitude'] = (pm25.coords['longitude'] + 180) % 360 - 180
            o3.coords['longitude'] = (o3.coords['longitude'] + 180) % 360 - 180
            no2.coords['longitude'] = (no2.coords['longitude'] + 180) % 360 - 180
            co.coords['longitude'] = (co.coords['longitude'] + 180) % 360 - 180
            pm10.coords['longitude'] = (pm10.coords['longitude'] + 180) % 360 - 180
            so2.coords['longitude'] = (so2.coords['longitude'] + 180) % 360 -180

            pm25 = pm25.sortby('longitude')
            pm25 = pm25.sel(longitude=slice(-10,10),latitude=slice(55,40))
            o3 = o3.sortby('longitude') 
            o3 = o3.sel(longitude=slice(-10,10),latitude=slice(55,40))
            no2 = no2.sortby('longitude')
            no2 = no2.sel(longitude=slice(-10,10),latitude=slice(55,40))
            co = co.sortby('longitude')
            co = co.sel(longitude=slice(-10,10),latitude=slice(55,40))
            pm10 = pm10.sortby('longitude')
            pm10 = pm10.sel(longitude=slice(-10,10),latitude=slice(55,40))
            so2 = so2.sortby('longitude')
            so2 = so2.sel(longitude=slice(-10,10),latitude=slice(55,40))
            print('OK')

            # =============================================================================
            # Interpolation
            # =============================================================================
            if sys == "Windows":
                pop = pd.read_csv(work_dir + "\\pop.csv", usecols=[0,1,2,3,4,5,6,42])
            else:
                pop = pd.read_csv(work_dir +"/pop.csv", usecols=[0,1,2,3,4,5,6,42])
        
            pop.columns = ['reg', 'dep', 'com', 'article', 'com_nom', 'lon', 'lat', 'total']
            lons, lats = pop.lon, pop.lat
            xrLons = xr.DataArray(lons, dims='com')
            xrLats = xr.DataArray(lats, dims='com')
            pm25Interpolated = pm25.interp(longitude=xrLons, latitude=xrLats)
            o3Interpolated = o3.interp(longitude=xrLons, latitude=xrLats)
            no2Interpolated = no2.interp(longitude=xrLons, latitude=xrLats)
            coInterpolated = co.interp(longitude=xrLons, latitude=xrLats)
            pm10Interpolated = pm10.interp(longitude=xrLons, latitude=xrLats)
            so2Interpolated = so2.interp(longitude=xrLons, latitude=xrLats)
            
            #endpart

            # =============================================================================
            # Risk Assessment
            # =============================================================================
            #part| #%%
            
            #for lead in progressbar(range(97), 'Compute risk: ', 60):
            print("Computing Atmospheric Pollutants maps ...")
            selected_columns = ["pm25","co","o3","no2","pm10","so2"]
            if sys == "Windows":
                dfpollution2 = pd.read_csv(work_dir + "/Enriched_Covid_history_data.csv", usecols=selected_columns)

            else:   
                dfpollution2 = pd.read_csv(work_dir + "/Enriched_Covid_history_data.csv", usecols=selected_columns)
           
            
            dfpollution2= dfpollution2.dropna()
            
            risk1 = pm25Interpolated
            risk2 = coInterpolated
            risk3 = o3Interpolated
            risk4 = no2Interpolated
            risk5 = pm10Interpolated
            risk6 = so2Interpolated
            
            risk1 = np.array(risk1)
            risk1 = np.vstack((lons,lats,risk1))
            risk1 = risk1.T
            risk1 = pd.DataFrame(risk1, columns = ['lon', 'lat', 'idx'])
            risk1max = dfpollution2['pm25'].max()

            risk2 = np.array(risk2)
            risk2 = np.vstack((lons,lats,risk2))
            risk2 = risk2.T
            risk2 = pd.DataFrame(risk2, columns = ['lon', 'lat', 'idx'])
            risk2max = dfpollution2['co'].max()
        

            risk3 = np.array(risk3)
            risk3 = np.vstack((lons,lats,risk3))
            risk3 = risk3.T
            risk3 = pd.DataFrame(risk3, columns = ['lon', 'lat', 'idx'])
            risk3max = dfpollution2['o3'].max()

            risk4 = np.array(risk4)
            risk4 = np.vstack((lons,lats,risk4))
            risk4 = risk4.T
            risk4 = pd.DataFrame(risk4, columns = ['lon', 'lat', 'idx'])
            risk4max = dfpollution2['no2'].max()

            risk5 = np.array(risk5)
            risk5 = np.vstack((lons,lats,risk5))
            risk5 = risk5.T
            risk5 = pd.DataFrame(risk5, columns = ['lon', 'lat', 'idx'])
            risk5max = dfpollution2['pm10'].max()

            risk6 = np.array(risk6)
            risk6 = np.vstack((lons,lats,risk6))
            risk6 = risk6.T
            risk6 = pd.DataFrame(risk6, columns = ['lon', 'lat', 'idx'])
            risk6max = dfpollution2['so2'].max()

            risk1Maps.append(risk1)
            risk2Maps.append(risk2)
            risk3Maps.append(risk3)
            risk4Maps.append(risk4)
            risk5Maps.append(risk5)
            risk6Maps.append(risk6)

            markersize = .1
            

            fig = plt.figure(figsize=(3,3))
            gs = fig.add_gridspec(1, 1)
            ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
          
            axes = [ax1]
            
            if not hasattr(ax1, 'background_patch'):
                for patch in ax1.patches:
                    patch.set_visible(False)
            else:
                ax1.background_patch.set_fill(False)
            for a in axes:
                a.add_geometries([regionmask.defined_regions.prudence["FR"].polygon,], ccrs.PlateCarree(),
                edgecolor=grayDark, lw=2, facecolor=grayDark, alpha=0, zorder=0)
                a.set_extent([-5,10,41,52])
                a.set_aspect('auto')
                if hasattr(a, 'outline_patch'):
                    a.outline_patch.set_linewidth(0.) 
                else:
                    text_x = 0.5  # X-coordinate in axes coordinates
                    text_y = 0.95  # Y-coordinate in axes coordinates
                    text = 'PM25-concentration:' + currentDatestring + " + " + j
                    a.text(text_x, text_y, text, transform=a.transAxes, color='red', fontsize=10, ha='center', va='center')
                pass
               

            cax = ax1.scatter(risk1Maps[counter].lon,risk1Maps[counter].lat,c=risk1Maps[counter].idx,
            cmap='RdYlGn_r', s=markersize*5, vmin=0, vmax=risk1max, zorder=4)
            cbar = fig.colorbar(cax, orientation='horizontal', pad=0, aspect=50,
            fraction=.01, extend='max', drawedges=False, ticks=[0, risk1max])
            cbar.ax.set_xticklabels(['low', 'high'])
            cbar.ax.xaxis.set_ticks_position('top')
            cbar.ax.xaxis.set_label_position('top')

            ax1.text(0,.0,'Data \nCAMS', transform=ax1.transAxes,fontdict={'size':12})

            currentDateWD = pd.to_datetime(latestfiledatestring).strftime('%a, %d - %m, %Y')
            ax1.set_title('PM25 concentrations: \n{:}\n'.format(currentDateWD + " + "+ str (counter) + " days"),
            loc='left', pad=-60)

            fig.subplots_adjust(bottom=.01, left=.01, right=.99, top=.99)
            #plt.show()
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=70)
            buffer.seek(0)
            images1.append(imageio.imread(buffer))
            buffer.close()
            plt.close()

            fig = plt.figure(figsize=(3,3))
            gs = fig.add_gridspec(1, 1)
            ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
            axes = [ax1]

            if not hasattr(ax1, 'background_patch'):
                for patch in ax1.patches:
                    patch.set_visible(False)
            else:
                ax1.background_patch.set_fill(False)

            for a in axes:
                a.add_geometries([regionmask.defined_regions.prudence["FR"].polygon,], ccrs.PlateCarree(),
                edgecolor=grayDark, lw=2, facecolor=grayDark, alpha=0, zorder=0)
                a.set_extent([-5,10,41,52])
                a.set_aspect('auto')
                if hasattr(a, 'outline_patch'):
                    a.outline_patch.set_linewidth(0.)
                else:
                    text_x = 0.5  # X-coordinate in axes coordinates
                    text_y = 0.95  # Y-coordinate in axes coordinates
                    text = 'CO-concentration:' + currentDatestring + " + " + j
                    a.text(text_x, text_y, text, transform=a.transAxes, color='red', fontsize=10, ha='center', va='center')
                pass

            cax = ax1.scatter(risk2Maps[counter].lon,risk2Maps[counter].lat,c=risk2Maps[counter].idx,
            cmap='RdYlGn_r', s=markersize*5, vmin=0, vmax=risk2max, zorder=4)
            cbar = fig.colorbar(cax, orientation='horizontal', pad=0, aspect=50,
            fraction=.01, extend='max', drawedges=False, ticks=[0, risk2max])
            cbar.ax.set_xticklabels(['low', 'high'])
            cbar.ax.xaxis.set_ticks_position('top')
            cbar.ax.xaxis.set_label_position('top')

            ax1.text(0,.0,'Data \nCAMS', transform=ax1.transAxes,fontdict={'size':12})
            ax1.set_title('CO concentrations: \n{:}\n'.format(currentDateWD + " + "+ str (counter) + " days"),
            loc='left', pad=-60)

            fig.subplots_adjust(bottom=.01, left=.01, right=.99, top=.99)
            #plt.show()
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=70)
            buffer.seek(0)
            images2.append(imageio.imread(buffer))
            buffer.close()
            plt.close()

            fig = plt.figure(figsize=(3,3))
            gs = fig.add_gridspec(1, 1)
            ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
            axes = [ax1]

            if not hasattr(ax1, 'background_patch'):
                for patch in ax1.patches:
                    patch.set_visible(False)
            else:
                ax1.background_patch.set_fill(False)

            for a in axes:
                a.add_geometries([regionmask.defined_regions.prudence["FR"].polygon,], ccrs.PlateCarree(),
                edgecolor=grayDark, lw=2, facecolor=grayDark, alpha=0, zorder=0)
                a.set_extent([-5,10,41,52])
                a.set_aspect('auto')
                if hasattr(a, 'outline_patch'):
                    a.outline_patch.set_linewidth(0.)
                else:
                    text_x = 0.5  # X-coordinate in axes coordinates
                    text_y = 0.95  # Y-coordinate in axes coordinates
                    text = 'O3-concentration:' + currentDatestring + " + " + j
                    a.text(text_x, text_y, text, transform=a.transAxes, color='red', fontsize=10, ha='center', va='center')
                pass

            cax = ax1.scatter(risk3Maps[counter].lon,risk3Maps[counter].lat,c=risk3Maps[counter].idx,
            cmap='RdYlGn_r', s=markersize*5, vmin=0, vmax=risk3max, zorder=4)
            cbar = fig.colorbar(cax, orientation='horizontal', pad=0, aspect=50,
            fraction=.01, extend='max', drawedges=False, ticks=[0, risk3max])
            cbar.ax.set_xticklabels(['low', 'high'])
            cbar.ax.xaxis.set_ticks_position('top')
            cbar.ax.xaxis.set_label_position('top')

            ax1.text(0,.0,'Data \nCAMS', transform=ax1.transAxes,fontdict={'size':12})
            ax1.set_title('O3 concentrations: \n{:}\n'.format(currentDateWD + " + "+ str (counter) + " days"),
            loc='left', pad=-60)

            fig.subplots_adjust(bottom=.01, left=.01, right=.99, top=.99)
            #plt.show()
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=70)
            buffer.seek(0)
            images3.append(imageio.imread(buffer))
            buffer.close()
            plt.close()

            fig = plt.figure(figsize=(3,3))
            gs = fig.add_gridspec(1, 1)
            ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
            axes = [ax1]

            if not hasattr(ax1, 'background_patch'):
                for patch in ax1.patches:
                    patch.set_visible(False)
            else:
                ax1.background_patch.set_fill(False)

            for a in axes:
                a.add_geometries([regionmask.defined_regions.prudence["FR"].polygon,], ccrs.PlateCarree(),
                edgecolor=grayDark, lw=2, facecolor=grayDark, alpha=0, zorder=0)
                a.set_extent([-5,10,41,52])
                a.set_aspect('auto')

                if hasattr(a, 'outline_patch'):
                    a.outline_patch.set_linewidth(0.)
                else:
                    text_x = 0.5  # X-coordinate in axes coordinates
                    text_y = 0.95  # Y-coordinate in axes coordinates
                    text = 'NO2-concentration:' + currentDatestring + " + " + j
                    a.text(text_x, text_y, text, transform=a.transAxes, color='red', fontsize=10, ha='center', va='center')
                pass

            cax = ax1.scatter(risk4Maps[counter].lon,risk4Maps[counter].lat,c=risk4Maps[counter].idx,
            cmap='RdYlGn_r', s=markersize*5, vmin=0, vmax=risk4max, zorder=4)
            cbar = fig.colorbar(cax, orientation='horizontal', pad=0, aspect=50,
            fraction=.01, extend='max', drawedges=False, ticks=[0, risk4max])
            cbar.ax.set_xticklabels(['low', 'high'])
            cbar.ax.xaxis.set_ticks_position('top')
            cbar.ax.xaxis.set_label_position('top')

            ax1.text(0,.0,'Data \nCAMS', transform=ax1.transAxes,fontdict={'size':12})

            currentDateWD = pd.to_datetime(latestfiledatestring, dayfirst = False).strftime('%a, %d %b %Y')
            ax1.set_title('NO2 concentrations: \n{:}\n'.format(currentDateWD + " + "+ str (counter) + " days"),
            loc='left', pad=-60)

            fig.subplots_adjust(bottom=.01, left=.01, right=.99, top=.99)
            #plt.show()
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=70)
            buffer.seek(0)
            images4.append(imageio.imread(buffer))
            buffer.close()
            plt.close()

            fig = plt.figure(figsize=(3,3))
            gs = fig.add_gridspec(1, 1)
            ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
            axes = [ax1]
            if not hasattr(ax1, 'background_patch'):
                for patch in ax1.patches:
                    patch.set_visible(False)
            else:
                ax1.background_patch.set_fill(False)

            for a in axes:
                a.add_geometries([regionmask.defined_regions.prudence["FR"].polygon,], ccrs.PlateCarree(),
                edgecolor=grayDark, lw=2, facecolor=grayDark, alpha=0, zorder=0)
                a.set_extent([-5,10,41,52])
                a.set_aspect('auto')
                if hasattr(a, 'outline_patch'):
                    a.outline_patch.set_linewidth(0.)
                else:
                    text_x = 0.5  # X-coordinate in axes coordinates
                    text_y = 0.95  # Y-coordinate in axes coordinates
                    text = 'PM10-concentration:' + currentDatestring + " + " + j
                    a.text(text_x, text_y, text, transform=a.transAxes, color='red', fontsize=10, ha='center', va='center')
                pass

            cax = ax1.scatter(risk5Maps[counter].lon,risk5Maps[counter].lat,c=risk5Maps[counter].idx,
            cmap='RdYlGn_r', s=markersize*5, vmin=0, vmax=risk5max, zorder=4)
            cbar = fig.colorbar(cax, orientation='horizontal', pad=0, aspect=50,
            fraction=.01, extend='max', drawedges=False, ticks=[0, risk5max])
            cbar.ax.set_xticklabels(['low', 'high'])
            cbar.ax.xaxis.set_ticks_position('top')
            cbar.ax.xaxis.set_label_position('top')

            ax1.text(0,.0,'Data \nCAMS', transform=ax1.transAxes,fontdict={'size':12})
            ax1.set_title('PM10 concentrations: \n{:}\n'.format(currentDateWD + " + "+ str (counter) + " days"),
            loc='left', pad=-60)

            fig.subplots_adjust(bottom=.01, left=.01, right=.99, top=.99)
            #plt.show()
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=70)
            buffer.seek(0)
            images5.append(imageio.imread(buffer))
            buffer.close()
            plt.close()

            fig = plt.figure(figsize=(3,3))
            gs = fig.add_gridspec(1, 1)
            ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
            axes = [ax1]
            if not hasattr(ax1, 'background_patch'):
                for patch in ax1.patches:
                    patch.set_visible(False)
            else:
                ax1.background_patch.set_fill(False)
            for a in axes:
                a.add_geometries([regionmask.defined_regions.prudence["FR"].polygon,], ccrs.PlateCarree(),
                edgecolor=grayDark, lw=2, facecolor=grayDark, alpha=0, zorder=0)
                a.set_extent([-5,10,41,52])
                a.set_aspect('auto')
                if hasattr(a, 'outline_patch'):
                    a.outline_patch.set_linewidth(0.)
                else:
                    text_x = 0.5  # X-coordinate in axes coordinates
                    text_y = 0.95  # Y-coordinate in axes coordinates
                    text = 'SO2-concentration:' + currentDatestring + " + " + j
                    a.text(text_x, text_y, text, transform=a.transAxes, color='red', fontsize=10, ha='center', va='center')
                pass

            cax = ax1.scatter(risk6Maps[counter].lon,risk6Maps[counter].lat,c=risk6Maps[counter].idx,
            cmap='RdYlGn_r', s=markersize*5, vmin=0, vmax=risk6max, zorder=4)
            cbar = fig.colorbar(cax, orientation='horizontal', pad=0, aspect=50,
            fraction=.01, extend='max', drawedges=False, ticks=[0, risk6max])
            cbar.ax.set_xticklabels(['low', 'high'])
            cbar.ax.xaxis.set_ticks_position('top')
            cbar.ax.xaxis.set_label_position('top')

            ax1.text(0,.0,'Data \nCAMS', transform=ax1.transAxes,fontdict={'size':12})
            ax1.set_title('SO2 concentrations: \n{:}\n'.format(currentDateWD + " + "+ str (counter) + " days"),
            loc='left', pad=-60)

            fig.subplots_adjust(bottom=.01, left=.01, right=.99, top=.99)
            #plt.show()
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=70)
            buffer.seek(0)
            images6.append(imageio.imread(buffer))
            buffer.close()
            plt.close()

            fig.subplots_adjust(bottom=.01, left=.01, right=.99, top=.99)
            #plt.show()
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=70)
            buffer.seek(0)
            images7.append(imageio.imread(buffer))
            buffer.close()
            plt.close()
            counter += 1

        print('Create gif ...', flush=True, end='')
        if sys == "Windows":
            gifPath = work_dir + "\\forecast\\fr\\"
        else:
            gifPath = work_dir + "/forecast/fr/"

        gifName = 'PM25_concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1 / duration
            imageio.mimsave(gifPath + "PM25\\" + gifName, images1, 'GIF', fps = fps , loop=0)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_PM25, self.object_key_init_PM25, gifPath + "PM25\\" + gifName)
        else:
            duration = 1 
            kargs = {'fps':1/duration, "loop":0 }
            imageio.mimwrite(gifPath + "PM25/" + gifName, images1, 'GIF', **kargs)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_PM25, self.object_key_init_PM25, gifPath + "PM25/" + gifName)
 
        print('Create gif ...', flush=True, end='')
        gifName = 'CO_concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1 / duration
            imageio.mimsave(gifPath + "CO\\" + gifName, images2, 'GIF', fps=fps, loop = 0)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_CO, self.object_key_init_CO, gifPath + "CO\\" + gifName)
        else:
            duration = 1 
            kargs = {'fps':1/duration, "loop":0 }
            imageio.mimwrite(gifPath + "CO/" + gifName, images2, 'GIF', **kargs)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_CO, self.object_key_init_CO, gifPath + "CO/" + gifName)
        print('Create gif ...', flush=True, end='')

        gifName = 'O3_concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1/ duration
            imageio.mimsave(gifPath + "O3\\" + gifName, images3, 'GIF', fps = fps, loop = 0)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_O3, self.object_key_init_O3, gifPath + "O3\\" + gifName)
        else:
            duration = 1 
            kargs = {'fps':1/duration, "loop":0 }
            imageio.mimwrite(gifPath + "O3/" + gifName, images3, 'GIF', **kargs)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_O3, self.object_key_init_O3, gifPath + "O3/" + gifName)

        print('Create gif ...', flush=True, end='')
        gifName = 'NO2_concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1/ duration
            imageio.mimsave(gifPath + "NO2\\" + gifName, images4, 'GIF', fps = fps, loop = 0)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_NO2, self.object_key_init_NO2, gifPath + "NO2\\" + gifName)

        else:
            duration = 1 
            kargs = {'fps':1/duration, "loop":0 }
            imageio.mimwrite(gifPath + "NO2/" + gifName, images4, 'GIF', **kargs)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_NO2, self.object_key_init_NO2, gifPath + "NO2/" + gifName)


        print('Create gif ...', flush=True, end='')
        gifName = 'PM10_concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1/ duration
            imageio.mimsave(gifPath + "PM10\\" + gifName, images5, 'GIF', fps=fps, loop = 0)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_PM10, self.object_key_init_PM10, gifPath + "PM10\\" + gifName)

        else:
            duration = 1 
            kargs = {'fps':1/duration, "loop":0 }
            imageio.mimwrite(gifPath + "PM10/" + gifName, images5, 'GIF', **kargs)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_PM10, self.object_key_init_PM10, gifPath + "PM10/" + gifName)

        
        print('Create gif ...', flush=True, end='')
        gifName = 'SO2_concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1/duration
            imageio.mimsave(gifPath + "SO2\\" + gifName, images6, 'GIF', fps=fps, loop = 0)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_SO2, self.object_key_init_SO2, gifPath + "SO2\\" + gifName)

        else:
            duration = 1 
            kargs = {'fps':1/duration, "loop":0 }
            imageio.mimwrite(gifPath + "SO2/" + gifName, images6, 'GIF', **kargs)
            self.delete_previous_file_from_aws_and_save_new_file_to_aws(self.bucket_name_prefix_SO2, self.object_key_init_SO2, gifPath + "SO2/" + gifName)


        print('OK')
        print('Finished.')

        return None
 
if __name__ == '__main__':
  Maps = compute_maps()
  Maps.compute_maps()
