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
warnings.filterwarnings("ignore")  
sys = platform.system()
work_dir = os.path.dirname(os.path.abspath(__file__))
today = date.today()  
print(today)
class compute_maps:
    def __init__(self):
        self.status = None
        self.data = None
    
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
                return (dates, dt.date.today() - pd.Timedelta("3 Y"))

    def compute_maps(self):
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

        for j in tqdm(times):
            print(j)
            # filename = "/home/ludo915/code/covsco/predictions/fr/" + currentDatestring + "_predictions_for_day_" + str(counter) +".csv"
            # newhospipredictionsdf = pd.read_csv(filename)
            # print(filename + " Read!")
            if sys == "Windows":
                filePath = work_dir + "\\cams\\fr\\forecast\\"
            else:
                filePath = work_dir + '/cams/fr/forecast/'

            latestfiledatestring = self.findlatestdateofcamsdata(filePath)[1].strftime('%Y-%m-%d')
            currentDatestring = pd.to_datetime(latestfiledatestring, dayfirst = False).strftime('%Y-%m-%d')
            print("latdate:", latestfiledatestring)
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
            
            if sys == "Windows":
                dfpollution2 = pd.read_csv(work_dir + "/Enriched_Covid_history_data.csv")

            else:   
                dfpollution2 = pd.read_csv(work_dir + "/Enriched_Covid_history_data.csv")
           
            
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
            
            if sys == "Windows":
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
                    text = 'PM2.5-concentration:' + currentDatestring + " + " + j
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
            ax1.set_title('PM2.5 concentrations: \n{:}\n'.format(currentDateWD + " + "+ str (counter) + " days"),
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

            if sys == "Windows":
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

            if sys == "Windows":
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

            if sys == "Windows":
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
            if sys == "Windows":
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
            if sys == "Windows":
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

        folder = gifPath
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        
        gifName = 'PM2.5-concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1 / duration
            imageio.mimsave(gifPath + gifName, images1, 'GIF', fps = fps , loop=0)
        else:
            kargs = { 'duration': 1, "loop":0 }
            imageio.mimwrite(gifPath + gifName, images1, 'GIF', **kargs)

        print('Create gif ...', flush=True, end='')
        gifName = 'CO-concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1 / duration
            imageio.mimsave(gifPath + gifName, images2, 'GIF', fps=fps, loop = 0)
        else:
            kargs = { 'duration': 1 , "loop" : 0 }
            imageio.mimwrite(gifPath + gifName, images2, 'GIF', **kargs)

        print('Create gif ...', flush=True, end='')
        gifName = 'O3-concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1/ duration
            imageio.mimsave(gifPath + gifName, images3, 'GIF', fps = fps, loop = 0)
        else:
            kargs = { 'duration': 1, "loop" : 0 }
            imageio.mimwrite(gifPath + gifName, images3, 'GIF', **kargs)

        print('Create gif ...', flush=True, end='')
        gifName = 'NO2-concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1/ duration
            imageio.mimsave(gifPath + gifName, images4, 'GIF', fps = fps, loop = 0)
        else:
            kargs = { 'duration': 1, "loop" : 0 }
            imageio.mimwrite(gifPath + gifName, images4, 'GIF', **kargs)

        print('Create gif ...', flush=True, end='')
        gifName = 'PM10-concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1/ duration
            imageio.mimsave(gifPath + gifName, images5, 'GIF', fps=fps, loop = 0)
        else:
            kargs = { 'duration': 1, "loop": 0 }
            imageio.mimwrite(gifPath + gifName, images5, 'GIF', **kargs)
        
        print('Create gif ...', flush=True, end='')
        gifName = 'SO2-concentration-{:}.gif'.format(currentDatestring)
        if sys == "Windows":
            duration = 1  # Adjust the duration value as needed
            fps = 1/duration
            imageio.mimsave(gifPath + gifName, images6, 'GIF', fps=fps, loop = 0)
        else:
            kargs = { 'duration': 1 , "loop": 0}
            imageio.mimwrite(gifPath + gifName, images6, 'GIF', **kargs)

        print('OK')
        print('Finished.')

        return None
 
if __name__ == '__main__':
  Maps = compute_maps()
  Maps.compute_maps()
