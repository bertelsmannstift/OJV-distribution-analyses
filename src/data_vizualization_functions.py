import re

###############################################################

'''
Functions to select data
'''


def select_1steller(df):
    if 'wz2008_level' in df.columns:
        df = df[df['wz2008_level'] == 'abteilung']
        df = df.groupby(['wz2008_abschnitt_buchstabe', 'wz2008_abschnitt_label', 'wz2008_abschnitt_buchstabe_and_label', 'year'], as_index=False).sum()
    elif 'kldb2010_level' in df.columns:
        df = df[df['kldb2010_level'] == 'berufsbereich']
        df = df.groupby(['kldb2010_bereich_code', 'kldb2010_bereich_label', 'kldb2010_bereich_code_and_label', 'year'], as_index=False).sum()
    else:
        print('Missing column: function select_1steller produced no changes to dataframe')
    return(df)


def select_2steller(df):
    if 'wz2008_level' in df.columns:
        df = df[df['wz2008_level'] == 'abteilung']
    elif 'kldb2010_level' in df.columns:
        df = df[df['kldb2010_level'] == 'berufshauptgruppe']
    else:
        print('Missing column: function select_2steller produced no changes to dataframe')
    return(df)


def select_3steller(df):
    if 'wz2008_level' in df.columns:
        df = df[df['wz2008_level'] == 'gruppe']
    elif 'kldb2010_level' in df.columns:
        df = df[df['kldb2010_level'] == 'berufsgruppe']
    else:
        print('Missing column: function select_3steller produced no changes to dataframe')
    return(df)


###############################################################

'''
Functions to calculate new columns
'''

def add_proportions(df,
                    years_list
                    ):
    
    variables_list = []
    
    # find relevant variables in the dataframe
    for column in df.columns:
        if 'count_' in column:
            substring = re.search(r'(?:count_)(.+)', column).group(1) # retreives string after 'count_'
            variables_list.append(substring)
    
    # create prop column
    for year in years_list:
        for var in variables_list:
            df.loc[df['year'] == year, f'prop_{var}'] = (df.loc[df['year'] == year, f'count_{var}'] / df.loc[df['year'] == year, f'count_{var}'].sum()) * 100
    return(df)



def add_totals(df,
               years_list                    
               ):
    
    variables_list = []
    
    # find relevant variables in the dataframe
    for column in df.columns:
        if 'count_' in column:
            substring = re.search(r'(?:count_)(.+)', column).group(1) # retreives string after 'count_'
            variables_list.append(substring)
    
    # create total column
    for year in years_list:
        for var in variables_list:
            df.loc[df['year'] == year, f'total_{var}'] = df.loc[df['year'] == year, f'count_{var}'].sum()
            df[f'total_{var}'] = df[f'total_{var}'].astype('Int64')

    return(df)


def add_zufluss(df):
    if ('count_begBesch_svb' in df.columns) and ('count_besch_svb' in df.columns):
        df['zuflussverhältnis'] = df['count_begBesch_svb'] / df['count_besch_svb']
    
    return(df)


def add_abdeckung_ojv_nutzung(df,
                              ojv_column_name
                              ):
    
    if ('count_begBesch_svb' in df.columns) and (ojv_column_name in df.columns):
        df['abdeckung_ojv_nutzung'] = df[ojv_column_name] / df['count_begBesch_svb']
    
    return(df)
    
    
###############################################################

'''
Formatting and renaming functions
'''

def rename_columns(df, 
                   language # either 'German' or 'English'
                   ):
    
    if language == 'German':
        
        df = df.rename({'wz2008_abschnitt_buchstabe': 'WZ-Abschnitt-Buchstabe',
                        'wz2008_abschnitt_label': 'WZ-Abschnitt-Label',
                        'wz2008_abschnitt_buchstabe_and_label': 'WZ-Abschnitt',
                        'wz2008_code': 'WZ-Code',
                        'wz2008_level': 'WZ-Ebene', 
                        'wz2008_label': 'WZ-Label', 
                        'wz2008_code_and_label': 'WZ-Code+Label', 
                        'kldb2010_bereich_code': 'KldB-Bereich-Code',
                        'kldb2010_bereich_label': 'KldB-Bereich-Label',
                        'kldb2010_bereich_code_and_label': 'KldB-Bereich',
                        'kldb2010_code': 'KldB-Code',
                        'kldb2010_level': 'KldB-Ebene', 
                        'kldb2010_label': 'KldB-Label', 
                        'kldb2010_code_and_label': 'KldB-Code+Label', 
                        'year': 'Jahr',
                        'count_besch_svb': 'Beschäftigte (SVB)', 
                        'count_besch_gb': 'Beschäftigte (GB)', 
                        'count_besch_svb+gb': 'Beschäftigte (SVB+GB)',
                        'count_begBesch_svb': 'Begonnene Beschäftigungsverhältnisse (SVB)', 
                        'count_jobid': 'Job-IDs (SVB+GB)',
                        'zuflussverhältnis': 'Zuflussverhältnis (beg. Besch-Verh. (SVB) geteilt durch Beschäftigte (SVB))', 
                        'abdeckung_ojv_nutzung': 'Abdeckung der Nutzung von OJVs (Job-IDs (SVB+GB) geteilt durch beg. Besch-Verh. (SVB))', 
                        'prop_besch_svb': 'Beschäftigte (SVB, %)',
                        'prop_besch_gb': 'Beschäftigte (GB, %)', 
                        'prop_besch_svb+gb': 'Beschäftigte (SVB+GB, %)', 
                        'prop_begBesch_svb': 'Begonnene Beschäftigungsverhältnisse (SVB, %)', 
                        'prop_jobid': 'Job-IDs (SVB+GB, %)',
                        'total_besch_svb': 'Gesamtzahl Beschäftigte (SVB, jährlich, übergreifend)', 
                        'total_besch_gb': 'Gesamtzahl Beschäftigte (GB, jährlich, übergreifend)', 
                        'total_besch_svb+gb': 'Gesamtzahl Beschäftigte (SVB+GB, übergreifend)',
                        'total_begBesch_svb': 'Gesamtzahl beg. Beschäftigungsverhältnisse (SVB, übergreifend)', 
                        'total_jobid': 'Gesamtzahl Job-IDs (SVB+GB, übergreifend)'
                        },
                       axis='columns',
                       errors='ignore')
        
    elif language == 'English':

        df = df.rename({'wz2008_abschnitt_buchstabe': 'WZ sector letter',
                        'wz2008_abschnitt_label': 'WZ sector label',
                        'wz2008_abschnitt_buchstabe_and_label': 'WZ sector',
                        'wz2008_code': 'WZ code',
                        'wz2008_level': 'WZ level', 
                        'wz2008_label': 'WZ label', 
                        'wz2008_code_and_label': 'WZ code+label', 
                        'kldb2010_bereich_code': 'KldB area code',
                        'kldb2010_bereich_label': 'KldB area label',
                        'kldb2010_bereich_code_and_label': 'KldB area',
                        'kldb2010_code': 'KldB code',
                        'kldb2010_level': 'KldB level', 
                        'kldb2010_label': 'KldB label', 
                        'kldb2010_code_and_label': 'KldB code+label', 
                        'year': 'Year',
                        'count_besch_svb': 'Employees (SVB)', 
                        'count_besch_gb': 'Employees (GB)', 
                        'count_besch_svb+gb': 'Employees subject (SVB+GB)',
                        'count_begBesch_svb': 'Initiated employment relationships (SVB)', 
                        'count_jobid': 'Job-IDs (SVB+GB)',
                        'zuflussverhältnis': 'Inflow ratio (initiated employment rel (SVB). divided by employees (SVB))', 
                        'abdeckung_ojv_nutzung': 'Coverage of usage of OJVs (Job-IDs (SVB+GB) divided by init. employment rel. (SVB))', 
                        'prop_besch_svb': 'Employees (SVB, %)',
                        'prop_besch_gb': 'Employees (GB, %)', 
                        'prop_besch_svb+gb': 'Employees (SVB+GB, %)', 
                        'prop_begBesch_svb': 'Initiated employment relationships (SVB, %)', 
                        'prop_jobid': 'Job-IDs (SVB, %)',
                        'total_besch_svb': 'Total employees (SVB, overall)', 
                        'total_besch_gb': 'Total employees (GB, overall)', 
                        'total_besch_svb+gb': 'Total employees (SVB+GB, overall)',
                        'total_begBesch_svb': 'Total initiated employment relationships (SVB, overall)', 
                        'total_jobid': 'Total Job-IDs (SVB+GB, overall)'
                        },
                       axis='columns',
                       errors='ignore')
    
    return(df)