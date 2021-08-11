import os
import pandas as pd

# multiple-use variables
wz_taxonomy = pd.read_excel('../data/taxonomy/wz2008_taxonomy.xlsx', converters={'wz2008_code':str}) # file with codes and labels to serve as basis
kldb_taxonomy = pd.read_excel('../data/taxonomy/kldb2010_taxonomy.xlsx', converters={'kldb2010_code':str, 'kldb2010_bereich_code':str}) # file with codes and labels to serve as basis
region_codes = ['d', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16'] # regions to be included in data processing
stat_types_list = ['wz', 'kldb']

#%%

'''
Beschäftigte (SVB and GB)

This process reads in the files in data/processing/wz and /kldb,
merges all quarters into a single file,
melts the dataframe to a flat format,
sums count_svb and count_gb to a new column,
calculates rounded yearly averages (out of the quarters),
and saves to a new file in data/processing/wz and /kldb,
(thus producing one file containing the columns count_besch_svb, count_besch_gb and count_besch_svb+gb)
'''

print('PROCESS: Beschäftigte (SVB and GB)') # for easier identification

from data_integration_functions import rename_columns

variables_list = ['svb', 'gb'] # employment types to be included in data processing
column = 'insgesamt' # which column containing employment numbers to be included in data processing
tabelle = 'tabelle2' # table in original files from which the data was extracted
not_exported = [] # leave empty, used to print message at the end of code

for stat_type in stat_types_list:
    
    # define some variables based on stat_type
    if stat_type == 'wz':
        code = 'wz2008_code' 
        df_base_master = wz_taxonomy.copy()
        label_columns = ['wz2008_abschnitt_buchstabe', 'wz2008_abschnitt_label', 'wz2008_level', 'wz2008_label', 'wz2008_code_and_label']
    elif stat_type == 'kldb':
        code = 'kldb2010_code'
        df_base_master = kldb_taxonomy.copy()
        label_columns = ['kldb2010_bereich_code', 'kldb2010_bereich_label', 'kldb2010_level', 'kldb2010_label', 'kldb2010_code_and_label']
    
    for region in region_codes:
        for variable in variables_list:
            
            # get dataframe with taxonomy codes
            df_base = df_base_master[[code]]
            df_merged = df_base.copy()
            
            for filename in os.listdir(f'../data/processing/{stat_type}'):
                if filename.startswith(f"{stat_type}-heft-{region}") & filename.endswith(f"{variable}_{tabelle}.csv"):
                 
                    # rename and merge columns into single dataframe
                    df_current = rename_columns(f'../data/processing/{stat_type}', filename, column, stat_type)
                    df_merged = df_merged.merge(df_current, on=code, how='left')
                
                else: pass
            
            # melt and export files only if some change occured
            if df_base.equals(df_merged):
                not_exported.append(f'{stat_type}_{region}_besch_{variable}_quarterly.csv')
                
            else:
                # melt files 
                df_melted = pd.melt(df_merged, 
                                    id_vars=[code],
                                    var_name='year',
                                    value_name=f'count_besch_{variable}')
                
                # create new column with quarter value
                df_melted['quarter'] = df_melted.year.str[-3:]
                df_melted['quarter'].replace({'mar': 1, 'jun': 2, 'sep': 3, 'dec': 4}, inplace=True)
                
                # replace values in year column to actual year as integer
                df_melted['year'] = df_melted['year'].str[:4].astype('int64')
                
                # export files
                new_filename = f"{stat_type}_{region}_besch_{variable}_quarterly.csv"
                df_melted.to_csv(f"../data/processing/{stat_type}/{new_filename}", index=False)
                print(f"Exported {new_filename} to data/processing/{stat_type}")
    
    
        # MERGE count_besch_svb AND count_besch_gb INTO SINGLE FILE
        
        # reset df_base value
        df_base = df_base_master.copy() # file with codes and labels to serve as basis
        df_base = df_base[[code]]
        
        svb_filename = f'{stat_type}_{region}_besch_svb_quarterly.csv'
        gb_filename = f'{stat_type}_{region}_besch_gb_quarterly.csv'
    
        # only run process if both svb and gb files exist (to avoid mistakes)
        if (os.path.isfile(f'../data/processing/{stat_type}/{svb_filename}') and os.path.isfile(f'../data/processing/{stat_type}/{gb_filename}')):
            
            # get dataframe for svb and drop unwanted columns
            df_svb = pd.read_csv(f'../data/processing/{stat_type}/{svb_filename}', dtype={code:str})
            df_svb = df_svb.drop(columns=label_columns, errors='ignore')
            
            #get dataframe for gb and drop unwanted columns
            df_gb = pd.read_csv(f'../data/processing/{stat_type}/{gb_filename}', dtype={code:str})
            df_gb = df_gb.drop(columns=label_columns, errors='ignore')
            
            # merge dataframes
            df = df_base.merge(df_svb, on=code, how='left')
            df = df.merge(df_gb, on=[code, 'year', 'quarter'], how='left')
            
            # create new column with sum of svb + gb
            df['count_besch_svb+gb'] = df['count_besch_svb'] + df['count_besch_gb']
            
            # calculate yearly averages and drop 'quarter' column
            df = df.groupby([code, 'year'], as_index=False).mean().round()
            df = df.drop(columns={'quarter'})
            
            # export files
            new_filename = f"{stat_type}_{region}_besch.csv"
            df.to_csv(f"../data/processing/{stat_type}/{new_filename}", index=False)
            print(f"Exported {new_filename} to data/processing/{stat_type}")
        
        else:
            not_exported.append(f"{stat_type}_{region}_besch.csv")
print('')         
print(f'Due to missing input files, the following output files were not created: {not_exported}')
print('')   
#%%

'''
Unify all different statistics

This process reads in the files containing info on Beschäftigte, begonnene Beschäftigungsverhältnisse and OJV,
merges them and returns a unified file.
'''

print('INITIATING PROCESS: Unify all different statistics') # for easier identification

data_types_list = ['besch', 'begBesch', 'ojv'] # data files to be included in process
not_exported = [] # leave empty, used to print message at the end of code

for stat_type in stat_types_list:
    for region in region_codes:
        
        # set base file
        if stat_type == 'wz':
            code = 'wz2008_code' 
            df_base_master = wz_taxonomy.copy()
        elif stat_type == 'kldb':
            code = 'kldb2010_code'
            df_base_master = kldb_taxonomy.copy()
                
        df = df_base_master.copy()
        
        # read the different files (containing data on besch, begBesch and ojv) and merge them
        for data_type in data_types_list:
            
            file = f'../data/processing/{stat_type}/{stat_type}_{region}_{data_type}.csv'
            
            if os.path.isfile(file): # check if file exists to avoid error
                df_data_type = pd.read_csv(file, dtype={code:str})
                
                if 'year' in df.columns:
                    df = df.merge(df_data_type, on=[code, 'year'], how='left')
                else:
                    df = df.merge(df_data_type, on=[code], how='left')
        
        # export files only if some change occured
        if df_base_master.equals(df):
            not_exported.append(f'{stat_type}_{region}')
            
        else:
            new_filename = f'{stat_type}_{region}_all.xlsx'
            df.to_excel(f'../data/output/{stat_type}/{new_filename}', index=False)
            print(f"Exported {new_filename} to data/output/{stat_type}")
        
print(f'No {data_types_list} files found for {not_exported}')