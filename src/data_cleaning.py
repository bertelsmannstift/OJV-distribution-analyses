import pandas as pd
import os

# multiple-use variables
wz_taxonomy = pd.read_excel('../data/taxonomy/wz2008_taxonomy.xlsx', converters={'wz2008_code':str}) # file with codes and labels to serve as basis
kldb_taxonomy = pd.read_excel('../data/taxonomy/kldb2010_taxonomy.xlsx', converters={'kldb2010_code':str, 'kldb2010_bereich_code':str}) # file with codes and labels to serve as basis
region_codes = ['d', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16'] # regions to be included in data processing
directories_list = ['../data/raw/wz', '../data/raw/kldb']

#%%

'''
Beschäftigte (SVB and GB)

WHAT THIS PROCESS DOES:
Reads the files downloaded from the website of the Bundesagentur für Arbeit,
returns a new, cleaned file for every file read.

REQUIREMENTS to run without errors or changes: 
    1. the original file naming system from the BA must be retained (e.g. wz-heft-d-0-202003-xlsx.xlsx)
    2. the files must be located under /data/raw/wz or /data/raw/kldb
'''

from data_cleaning_functions import clean_besch_data_tabelleII

variables_list = ['SVB', 'GB'] # employment types to be included in the process (case sensitive)

for directory in directories_list:
    for filename in os.listdir(directory): # iterates through filenames in each directory
        if (filename.startswith('wz-heft-') or filename.startswith('bo-heft-')): # avoid reading irrelevant files
            for variable in variables_list:
                
                # read and clean file
                df = pd.read_excel(f'{directory}/{filename}', sheet_name=f'{variable} - Tabelle II')               
                
                # define new filename length according to region
                if '-d-' in filename or '-w-' in filename or '-o-' in filename:
                    name_length = 18
                else:
                    name_length = 19
                
                # clean and export files
                if 'wz' in filename:
                    df_cleaned = clean_besch_data_tabelleII(df, variable, 'wz')
                    new_filename = f'{filename[:name_length]}_{str.lower(variable)}_tabelle2.csv'
                    df_cleaned.to_csv(f'../data/processing/wz/{new_filename}', index=False)        
                    print(f'Exported: {new_filename} to data/processing/wz')
                    
                elif 'bo' in filename:
                    df_cleaned = clean_besch_data_tabelleII(df, variable, 'kldb')
                    new_filename = f'kldb-{filename[3:name_length]}_{str.lower(variable)}_tabelle2.csv'
                    df_cleaned.to_csv(f'../data/processing/kldb/{new_filename}', index=False)        
                    print(f'Exported: {new_filename} to data/processing/kldb')

                else:
                    print('File not cleaned or exported')
                    

#%%

'''
Begonnene sozialversicherungspflichtige Beschäftigungsverhältnisse

WHAT THIS PROCESS DOES:
Reads the files acquired from the Bundesagentur für Arbeit,
returns a new, cleaned file for every file read.

REQUIREMENTS to run without errors or changes: 
    1. the original 'standard' table formatting of the BA must be retained (i.e. contents of the excel file acquired from the BA must not be altered)
    2. the file name must be: {stat_type}_{region}_begBesch (e.g. wz_d_begBesch.xlsx)
    3. the sheet name containing the data in the files must be: Beg.BV_Svpfl_WZ2008 (for WZ) or Beg.BV_Svpfl_KldB2010 (for KldB)
    4. the files must be located under /data/raw/wz or /data/raw/kldb
    
    Alternatively, an already cleaned version of the file can be placed in data/processing with the following requirements:
        Name of the file: {stat_type}_{region}_begBesch.csv (e.g. kldb_08_begBesch.csv or wz_d_begBesch.csv)
        Name of the column containing the WZ or KldB codes: wz2008_code or kldb2010_code
'''

from data_cleaning_functions import clean_begBesch_data


for directory in directories_list:
    for filename in os.listdir(directory): # iterates through filenames in each directory
        for region in region_codes:
            if f'{region}_begBesch' in filename: # avoid reading irrelevant files
                
                if 'wz' in filename:
                    df_master = pd.read_excel(f'{directory}/{filename}', sheet_name='Beg.BV_Svpfl_WZ2008')
                    
                    # clean the dataframe
                    df = clean_begBesch_data(df_master.copy(), 'wz')
                    
                    # add taxonomy information and merge
                    df_base = wz_taxonomy.copy()
                    df_base = df_base['wz2008_code']
                    df = df.merge(df_base, on='wz2008_code', how='left')
                    
                    # export new file
                    new_filename = f'wz_{region}_begBesch.csv'
                    df.to_csv(f'../data/processing/wz/{new_filename}', index=False)
                    print(f'Exported: {new_filename} to data/processing/wz')
                    
                if 'kldb' in filename:
                    df_master = pd.read_excel(f'{directory}/{filename}', sheet_name='Beg.BV_Svpfl_KldB2010')
                    
                    # clean the dataframe
                    df = clean_begBesch_data(df_master.copy(), 'kldb')
                    
                    # add taxonomy information and merge
                    df_base = kldb_taxonomy.copy()
                    df_base = df_base['kldb2010_code']
                    df = df.merge(df_base, on='kldb2010_code', how='left')
                    
                    # export new file
                    new_filename = f'kldb_{region}_begBesch.csv'
                    df.to_csv(f'../data/processing/kldb/{new_filename}', index=False)
                    print(f'Exported: {new_filename} to data/processing/kldb')


#%%

'''
Online Job Vacancies

WHAT THIS PROCESS DOES:
Reads and cleans a single file containing the data,
returns unified file with ojv count by all WZ levels.

REQUIREMENTS to run without errors or changes:
    1. the file name must be: {stat_type}_{region}_ojv (e.g. wz_d_ojv.csv)
    2. the column name must be either: wz2008_code or kldb2010_code
    3. the files must be located under /data/raw/wz or /data/raw/kldb
'''

from data_cleaning_functions import clean_codes

for directory in directories_list:
    for filename in os.listdir(directory): # iterates through filenames in each directory
        for region in region_codes:
            if f'{region}_ojv' in filename: # avoid reading irrelevant files
                
                if 'wz' in filename:
                    df_base = wz_taxonomy.copy() # import taxonomy file
                    stat_type = 'wz'
                    code = 'wz2008_code'
                    
                if 'kldb' in filename:
                    df_base = kldb_taxonomy.copy() # import taxonomy file
                    stat_type = 'kldb'
                    code_column = 'kldb2010_code'
            
                # read file with ojv data
                if (filename.endswith('xlsx')) | (filename.endswith('xls')):
                    df_ojv = pd.read_excel(f'../data/raw/{stat_type}/{filename}')
                elif filename.endswith('csv'):
                    df_ojv = pd.read_csv(f'../data/raw/{stat_type}/{filename}')
        
                
                # create dataframe for for each steller 
                df2 = clean_codes(df_ojv.copy(), '2steller', stat_type)
                df3 = clean_codes(df_ojv.copy(), '3steller', stat_type)
                df4 = clean_codes(df_ojv.copy(), '4steller', stat_type)
                df5 = clean_codes(df_ojv.copy(), '5steller', stat_type)
                
                # append them to get single dataframe
                df_all = df2.append(df3)
                df_all = df_all.append(df4)
                df_all = df_all.append(df5)
                
                # merge to base dataframe
                df = df_base.merge(df_all, on=code, how='left')
                df = df.groupby([code, 'year'], as_index=False).sum()
                
                # export to file
                new_filename = f'{stat_type}_{region}_ojv.csv'
                df.to_csv(f'../data/processing/{stat_type}/{new_filename}', index=False)
                print(f'Exported: {new_filename} to data/processing')