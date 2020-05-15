# -*- coding: utf-8 -*-
"""
@author: Stefano Carlesso
<s.carlesso#fondazioneomd.it>
"""
from glob import glob
import csv
from datetime import datetime
from datetime import timedelta
import pytz
import xlsxwriter
import os
#import shutils

## settings
debug = False
metadata_file = "./stazioni_good.csv"
utc = pytz.timezone("UTC")
filename_list = glob("fomd3/[a-z][a-z][a-z][0-9][0-9][0-9].csv")
metadata_dict = dict()

with open(metadata_file) as a_file:
    """ csv header is 
    code;latitudine;longitudine;altitudineslm;strumentazione;regione;comune;
    area;provincia;label_tmp;label_good"""
    metadata_reader = csv.DictReader(a_file, delimiter=";", )
    for metadata_row in metadata_reader:
        metadata_dict[ metadata_row["code"] ] =  metadata_row["label_good"]

# def preproc():
#     """Unite files with the same name in different directories"""
#     list2 = glob("fomd2/*")
#     #os.mkdir("fomd3")
#     shutils.copy("fomd1", "fomd3")
#     for fname in list2:
#         with open(fname) as fobj:
#             reader = csv.DictReader(file, delimiter=";", )
#             for row_counter, row in enumerate(reader):
#                 # "2013-06-20 00:30:00"
#                 # italy_datetime is naive

def elaborate(my_input):
    """ elaborate my_input, that is a single csv file corresponding to a 
    single station."""
    # get station_id from filename
    station_id = my_input[6:12]
    # convert it to a pretty label
    station_label = metadata_dict[station_id]
    print(station_id, station_label)
    # output to ever new dir
    creation_timestamp = int(datetime.timestamp(datetime.now()))
    # TODO create folder if not exists
    dest_dir_name = "suborari_{}".format(creation_timestamp)
    if not os.path.exists(dest_dir_name):
        os.mkdir(dest_dir_name)
    output_file = "{}/Temp_suborari_{}.xlsx".format(dest_dir_name, station_label)    
    
    # create an Excel Workbook for any station
    wb = xlsxwriter.Workbook(output_file)
    
    ws0 = wb.add_worksheet("metadata")
    metadata_text = ["Questo file Excel riporta le temperature di alcune stazioni MeteoNetwork.",
        "italy_datetime è la marca temporale presente nei dati forniti da MeteoNetwork, che interpretiamo come riferita all'ora Italiana;",
        "solar_dt è invece riferita a UTC+1 (CET), quindi indipendente dai periodi in cui vige l'ora legale.",
        "L'orario in vigore in Italia si discosta di 0 o 1 ore dall'ora in UTC, a seconda della stagione.",]
    for index, value in enumerate(metadata_text):
        # row, col, data
        ws0.write(index,0, value)
        
    # create a sheet for the station
    ws = wb.add_worksheet(station_label)
    # write the column header to sheet
    header = ["italy_datetime", "utc_datetime", "solar_datetime", station_label]
    for n,h in enumerate(header):
        ws.write(0, n, h)
        
    with open(filename) as file:
        # csv header is 
        # code;datetime;temperature
        reader = csv.DictReader(file, delimiter=";", )
        for row_counter, row in enumerate(reader):
            # "2013-06-20 00:30:00"
            # italy_datetime is naive
            naive_italy_datetime = datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S")
            

            
            aware_utc_datetime = naive_italy_datetime.astimezone(utc)
            # solar_datetime is timezone-aware
            aware_utc_datetime = naive_italy_datetime.astimezone(utc)
            # trasform aware to naive for the benefit of ppor xlsxwriter
            naive_utc_datetime = aware_utc_datetime.replace(tzinfo=None)
            
            naive_solar_datetime = naive_utc_datetime + timedelta(hours=1)
            
            if debug:
                print("datetime from csv:", row["datetime"])
                print("naive italy datetime", naive_italy_datetime)
                print("aware utc datetime", aware_utc_datetime)
                print("naive utc datetime", naive_utc_datetime)
                print("naive solar datetime", naive_solar_datetime)
                        
            try:
                temperature = round(float(row["temperature"]), ndigits=1)
            except: 
                temperature = -999.9

            
            excel_date_format = wb.add_format({"num_format": "yyyy-mm-dd hh:mm"})
            #excel_float_format = wb.add_format({"num_format": "0,0"})
            # append single cells
            ws.write_datetime(row_counter + 1, 0, naive_italy_datetime, excel_date_format)
            ws.write_datetime(row_counter + 1, 1, naive_utc_datetime, excel_date_format)
            ws.write_datetime(row_counter + 1, 2, naive_solar_datetime, excel_date_format)
            ws.write(row_counter + 1, 3, temperature)
            
        wb.close()

def elaborate_all(my_list):
    """Elaborate all files in my_list"""
    for filename in my_list:
        # put here the function to elaborate one station
        elaborate(my_input = filename)
        pass

#elaborate("input/)