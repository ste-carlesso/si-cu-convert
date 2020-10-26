"""Elaborazione N, non divisi, ma effettuata la media oraria
"""
from libreria import good_stations, label_dict, create_excel, bad_stations
import pandas as pd
import pytz, os, time
# import numpy as np
# from datetime import timedelta as tdelta


stations =  bad_stations # they have duplicate index
stations = ["pmn047"]

output_dir = "../" + str(round(time.time()))

os.mkdir(output_dir)
ita = pytz.timezone("Europe/Rome")
utc = pytz.timezone("UTC")
sol = pytz.timezone("Etc/GMT-1")


for station in stations:
    df0_list = []
    for input_dir in ["fomd1", "fomd2", "fomd3"]:
        path = "../input/{}/{}.csv".format(input_dir, station)
        df0 = pd.read_csv( filepath_or_buffer=path, sep=";", header=0, 
            usecols=["datetime", "temperature"], 
            # index_col="datetime", 
            # squeeze=True, 
            parse_dates=True, )
        df0_list.append(df0)

    station_label = label_dict[station]
    
    # unite the series into one
    df1 = pd.concat(df0_list, ignore_index=True)
    # create new columns  timezones
    df1["naive_dt"] = df1["datetime"].apply(pd.to_datetime)

    df1["italian_dt"] = df1["naive_dt"].dt.tz_localize(tz=ita, ambiguous="NaT", nonexistent="NaT")
    df1["solar_dt"] = df1["italian_dt"].dt.tz_convert(sol)
    # df2 = df1.dropna(axis=0, how="any")

    s1 = pd.Series(data=df1["temperature"], index=df1["solar_dt"])

    out_csv1= "{}/{}_suborari.csv".format(output_dir, station_label)
    s1.to_csv(path_or_buf=out_csv1, sep=";")

    # create hour data
    s2 = s1.resample(rule="1h", closed="right", label="right").mean()
        
    # write CSV
    out_csv2 = "{}/{}_orari.csv".format(output_dir, station_label)
    s2.to_csv(path_or_buf=out_csv2, sep=";")


"""     # convert from tz-aware to naive because Excel writer can't handle aware
    s3 = pd.Series(data=s2, index=s2.index.replace(tz=None))
    # change the name
    s3.name = station_label
    # write xlsx
    out_xlsx = "{}/{}_orari.xlsx".format(output_dir, station_label)
    s3.to_excel(excel_writer=out_xlsx, 
        sheet_name=station_label, 
        #float_format="%.1f",
        header=True, 
        index=True) """

 