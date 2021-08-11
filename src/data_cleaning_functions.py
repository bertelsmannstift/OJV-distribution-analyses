import pandas as pd
import numpy as np

'''
clean_besch_data_tabelleII

This function reads the downloaded file from the Bundesagentur für Arbeit (BA) containing number of employees (Beschäftigte)
and returns a cleaned version of it
    
Known error: Script returns error "BadZipFile: File is not a zip file"
    Description: some excel files (apparently only for the year 2020) downloaded from the BA website come with a problem and pd.read_excel returns this error while reading the file
    Solution: open the problematic .xlsx file -> Excel will ask to fix the file -> accept save the file -> run the function again.
'''

def clean_besch_data_tabelleII(df, # raw dataframe from to clean
                              variable, # desired variable to extract, being either SVB, GB, aGB or iNGB (case sensitive)
                              stat_type # statistics type: 'wz' or 'kldb'
                              ):
    
    # define column name according to stat type
    if stat_type == 'wz':
        code = 'wz2008_code'
    elif stat_type =='kldb':
        code = 'kldb2010_code'
        
    # extract WZ code from cell values
    df[code] = df['Unnamed: 0'].str.extract('(^[0-9]{2,4})')
    
    # create especial handling for unbekannt
    df.loc[df['Unnamed: 0'].str.contains('XX', na=False), code] = 'unbekannt'
    df.loc[df['Unnamed: 0'].str.contains('Keine Angabe', na=False), code] = 'unbekannt'
    df.loc[df['Unnamed: 0'].str.contains('Keine Zuordnung', na=False), code] = 'unbekannt'
    
    # relocate certain column names
    df.iloc[8,0] = df.iloc[6,0]
    df.iloc[8,1] = df.iloc[6,1]
    
    # set header
    df.iloc[8, df.columns.get_loc(code)] = code
    df.columns = df.iloc[8]
    df.columns.name = ''
    
    # rename columns
    df.rename(columns={'Ohne berufl. Ausbildungs- abschluss': 'Ohne berufl Ausbildungsabschluss' , 'mit anerkanntem Berufs- abschluss 1)': 'mit anerkanntem Berufsabschluss', 'mit akademi-schem Berufs-abschluss 2)': 'mit akademischem Berufsabschluss'}, inplace=True)
    df.columns = df.columns.str.lstrip().str.replace(' ','_').str.lower()
    
    # select only desired columns
    if variable == 'SVB':    
        df = df[[code,
                 'insgesamt',
                 'in_vollzeit', # variable only available for sozialversicherungspflichtige Beschäftigte
                 'in_teilzeit', # variable only available for sozialversicherungspflichtige Beschäftigte
                 'helfer',
                 'fachkraft',
                 'spezialist',
                 'experte',
                 'ohne_berufl_ausbildungsabschluss',
                 'mit_anerkanntem_berufsabschluss',
                 'mit_akademischem_berufsabschluss',
                 'ausbildung_unbekannt']]

    else:    
        df = df[[code,
                 'insgesamt',
                 'helfer',
                 'fachkraft',
                 'spezialist',
                 'experte',
                 'ohne_berufl_ausbildungsabschluss',
                 'mit_anerkanntem_berufsabschluss',
                 'mit_akademischem_berufsabschluss',
                 'ausbildung_unbekannt']]
    
    # remove empty rows
    df = df[df[code].notnull()].reset_index(drop=True)
    
    # drop irrelevant first row with column names
    df = df.drop(index={0})
    
    # replace some values
    df = df.replace('*', np.nan) # Cells containing * represent hidden values by the BA due to data privacy reasons
    df = df.replace('-', 0) # Cells containing - represent zero employees
    
    return(df)


'''
clean_begBesch_data

This function reads in the raw file acquired by request from the BA containing the number of initiated employment relationships (begonnene Beschäftigungsverhältnisse) by year
and returns a cleaned version of it.
'''

def clean_begBesch_data(df, # raw dataframe to clean
                        stat_type # statistics type: 'wz' or 'kldb'
                        ):
    
    # define column name according to stat type
    if stat_type == 'wz':
        code = 'wz2008_code'
    elif stat_type =='kldb':
        code = 'kldb2010_code'
    
    # extract WZ code from cell values
    df[code] = df['Unnamed: 0'].str.extract('(^[0-9]{2,4})')
    
    # create especial handling for unbekannt
    df.loc[df['Unnamed: 0'].str.contains('Keine Angabe', na=False), code] = 'unbekannt'    
    
    # set header
    df.iloc[5, df.columns.get_loc(code)] = code
    
    # fix header names
    df.columns = df.iloc[5].astype('str').str.split('.', expand = True)[0]
    df.columns.name = ''
    
    # drop unwanted columns
    df.drop(df.columns[0], axis=1, inplace=True)
    
    # remove unwanted rows
    df = df[df[code].notnull()].reset_index(drop=True)

    # drop irrelevant first row with column names
    df = df.drop(index={0})
    
    # change year columns value type to integer
    cols=[i for i in df.columns if i not in [code]]
    for col in cols:
        df[col] = df[col].astype('Int64')
        
    # melt dataframe
    df = pd.melt(df,
                 id_vars=[code],
                 var_name='year',
                 value_name='count_begBesch_svb')
    
    df['year'] = df['year'].astype('int64')
    
    return(df)


'''
clean_codes

This function reads a dataframe containing a column named 'wz2008_code',
normalises the WZ-codes according to the desired WZ-Level (2, 3, 4 or 5-Steller),
removes rows that are above the desired level and thus cannot be defined,
and returns the cleaned dataframe.
e.g. when selecting '3steller' it replaces the WZ code '12.34.5' with the code '123', and removes rows with code '12'.
'''

def clean_codes(df, # the dataframe to read
                level, # string with desired WZ-Level (1steller, 2steller, 3steller, 4steller or 5steller)
                stat_type # 'wz' or 'kldb'
                ):
    
    if stat_type == 'wz':
        code = 'wz2008_code'
        df_base = pd.read_excel('../data/taxonomy/wz2008_taxonomy.xlsx')
        one_steller_column = 'wz2008_abschnitt_buchstabe' # column name in the taxonomy file, used in groupby function

    elif stat_type =='kldb':
        code = 'kldb2010_code'
        df_base = pd.read_excel('../data/taxonomy/kldb2010_taxonomy.xlsx')
        one_steller_column = 'kldb2010_bereich_code' # column name in the taxonomy file, used in groupby function

    # make sure code column is of string type
    df[code] = df[code].astype(str)   

    # replace empty values in wz2008_code
    df[code] = df[code].replace(to_replace = np.nan, value = 'unbekannt')
    
    # remove dots from wz code
    df[code] = df[code].str.replace('.','', regex=False) 

    if level == '1steller':
        # shorten to 2steller
        df[code] = df[code].str[:2]
        df = df.replace(to_replace = 'un', value = 'unbekannt')
        
        # select desired columns from taxonomy file
        df_base = df_base[[code, one_steller_column]]
        
        # merge both
        df = df.merge(df_base, on=code, how='left')
        
        # groupby 1-Steller and year
        df = df.groupby([one_steller_column, 'year'], as_index=False).sum()
        
        return(df)
    
    elif level == '2steller':
        # shorten to 2steller
        df[code] = df[code].str[:2]
        df = df.replace(to_replace = 'un', value = 'unbekannt')
        
    elif level == '3steller':
        # shorten to 3steller
        df[code] = df[code].str[:3]
        df = df.replace(to_replace = 'unb', value = 'unbekannt')
        
        # remove rows with only 2-Steller or less
        df = df[df[code].str.len() > 2 ]
        
    elif level == '4steller':
        # shorten to 3steller
        df[code] = df[code].str[:4]
        df = df.replace(to_replace = 'unbe', value = 'unbekannt')
                
        # remove rows with only 3-Steller or less
        df = df[df[code].str.len() > 3 ]
    
    elif level == '5steller':
        # shorten to 3steller
        df[code] = df[code].str[:5]
        df = df.replace(to_replace = 'unbek', value = 'unbekannt')
        
        # remove rows with only 4-Steller or less 
        df = df[df[code].str.len() > 4 ]
        
    # group by year and code
    df = df.groupby([code, 'year'], as_index=False).sum()
    
    # make sure code column is of string type
    df[code] = df[code].astype(str)
        
    return(df)