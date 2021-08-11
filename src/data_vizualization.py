# multiple-use variables
ojv_column_name = 'count_jobid' # change this string so as to reflect the actual name of the column containing the OJV numbers in your file (recommended to start with 'count_')
language = 'German' # set 'German' for column names in German or 'English' for column names in English
years_list = [2014, 2015, 2016, 2017, 2018, 2019, 2020]
# region_codes = ['d'] # regions to be included in data processing
region_codes = ['d', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16'] # regions to be included in data processing
stat_types_list = ['wz', 'kldb']

#######################################################################

import pandas as pd
import numpy as np
import os

from data_vizualization_functions import select_1steller, select_2steller, select_3steller, add_proportions, add_totals, add_zufluss, add_abdeckung_ojv_nutzung, rename_columns


for stat_type in stat_types_list:
    for region in region_codes:
        for filename in os.listdir(f'../data/output/{stat_type}'):
            if filename == f"{stat_type}_{region}_all.xlsx":
                
                df_master = pd.read_excel(f"../data/output/{stat_type}/{stat_type}_{region}_all.xlsx")
                
                # create sub-dataframes for each steller
                df_1steller = select_1steller(df_master.copy())
                df_2steller = select_2steller(df_master.copy())
                df_3steller = select_3steller(df_master.copy())
                
                dfs_list = [df_1steller, df_2steller, df_3steller]
                
                for df in dfs_list:
                    
                    # add Zuflussverhältnis column
                    df = add_zufluss(df)
                    
                    # add OJV nutzung Abdeckung column
                    df = add_abdeckung_ojv_nutzung(df, ojv_column_name)
                    
                    # add proportions columns
                    df = add_proportions(df, years_list)
    
                    # add totals columns
                    df = add_totals(df, years_list)
                    
                # rename columns with cleaner and more explanatory names              
                df_1steller = rename_columns(df_1steller, language)
                df_2steller = rename_columns(df_2steller, language)
                df_3steller = rename_columns(df_3steller, language)
                
                # export
                df_1steller.to_excel(f"../data/vizualization/{stat_type}/{stat_type}_{region}_1steller.xlsx", index=False)
                print(f'Exported {stat_type}_{region}_1steller.xlsx')
                
                df_2steller.to_excel(f"../data/vizualization/{stat_type}/{stat_type}_{region}_2steller.xlsx", index=False)
                print(f'Exported {stat_type}_{region}_2steller.xlsx')

                df_3steller.to_excel(f"../data/vizualization/{stat_type}/{stat_type}_{region}_3steller.xlsx", index=False)
                print(f'Exported {stat_type}_{region}_3steller.xlsx')
