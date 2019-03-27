
import pandas as pd
import pathlib as pl
import re


def process_df(myfile):
    data = pd.read_csv(myfile)
    data = pd.melt(data, id_vars=["UnitID", "Institution Name"], var_name='Category', value_name='Total')

    if len(data[data['Category'].str.contains('expenses')]) > 0:
        data['Cost or Revenue'] = 'Cost'
    else:
        data['Cost or Revenue'] = 'Revenue'

    data['Year'] = data['Category'].map(lambda x:
                                        ''.join(str(e) for e in re.findall(r'\s\(FL?A?G?S?\d{4}.*', x)))
    data[['Category', 'Year2']] = data['Category'].str.split(r'\s\(FL?A?G?S?\d{4}', expand=True).astype(str)
    data.drop(['UnitID', 'Year2'], axis=1)
    data['Year'] = data['Year'].map(lambda x: ' (F{0}{1}'.format(int(x[-3:-1])-1, x[-3:-1]) if 'FLAGS' in x else x)
    data['Year'] = data['Year'].map(lambda x: '20{0}-20{1}'.format(x[3:5], x[5:7]))
    data[['Category', 'Sub Category']] = data['Category'].str.split(r'\s?-\s?', expand=True).astype(str)
    index = data.loc[data['Total'].isnull()].index
    data.drop(index, inplace=True)
    data.loc[data['Cost or Revenue'] == 'Cost', 'Total'] = -data.loc[data['Cost or Revenue'] == 'Cost', 'Total']
    data = data.pivot_table('Total', ['Category', 'Sub Category', 'Year', 'Cost or Revenue'],
                            'Institution Name')
    data = data.reset_index()
    index = data.loc[(data['Boston University'] == 0) & (data['New York University'] == 0)
                     & (data['Northeastern University'] == 0)].index
    data.drop(index, inplace=True)
    data['Sub Category'] = data['Sub Category'].str.replace('Permanentlly', 'Permanently')\
        .str.title().str.replace('None', 'Other').str.replace('All Other', 'Other').str\
        .replace('Total', 'Other').str.replace('Total Amount', 'Other').str.replace('Other Amount', 'Other')
    data['Category'] = data['Category'].str.replace('contrants', 'contracts').str.title()\
        .str.replace('Independent Operations Revenue', 'Independent Operations')\
        .str.replace('Other Expenses', 'Other').str.replace('Other Revenue', 'Other')
    data['Category'] = data['Category'].map(lambda x: 'Other' if len(x) > 50 else x)

    return data


dfs = []
has_updates = None
mypath = r'C:\Users\krussell\Desktop\Data'

files = list(pl.Path(mypath).glob('*.csv'))

for file in files:
    dfs.append(process_df(file))

df = pd.concat(dfs, ignore_index=True, sort=False).drop_duplicates().reset_index(drop=True)
