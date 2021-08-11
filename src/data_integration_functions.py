import pandas as pd
import datetime 
import re 

'''
rename_columns

This function reads in files,
extracts the year and month from the filename (e.g. transforms 202006 to 2020-jun),
renames the column with this date,
and returns a new dataframe.
'''

def rename_columns(dir_input, # directory where files are located
                   filename, # name of file to process
                   column, # desired column to rename eg. 'insgesamt'
                   stat_type # 'wz' or 'kldb'
                   ):

    if stat_type == 'wz':
        code = 'wz2008_code' # column name containing WZ codes
    elif stat_type == 'kldb':
        code = 'kldb2010_code'

    # import file
    df = pd.read_csv(f'{dir_input}/{filename}')
    
    # get year and month in filename
    yyyymm = re.search(r'[0-9]{6}', filename).group(0) 
    yyyymm = str(yyyymm[:4] + '-' + yyyymm[4:])
    date = datetime.datetime.strptime(yyyymm, '%Y-%m').date() 
    
    # rename column
    column_label = f"{date.year}_{date.strftime('%b').lower()}"
    df = df.rename(columns={column: column_label})
    df = df[[code, column_label]]
    
    return(df)