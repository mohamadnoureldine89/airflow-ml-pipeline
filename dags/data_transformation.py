import os 
import pandas as pd 
import json

def transform_into_csv(n_files=None, filename='data.csv'):
    parent_folder = '/app/raw_files'

    files = sorted(os.listdir(parent_folder), reverse=True)

    if n_files:
        files = files[:n_files]

    dfs = []

    for f in files:
        with open(os.path.join(parent_folder, f), 'r') as file:
            data_temp = json.load(file)
            
        for city_name in data_temp:
            city_data = data_temp[city_name]
            dfs.append(
                {
                    'temperature': city_data['main']['temp'],
                    'city': city_data['name'],
                    'pression': city_data['main']['pressure'],
                    'date': f.split('.')[0]
                }
            )

    df = pd.DataFrame(dfs)

    print('\n', df.head(10))

    with open(os.path.join('/app/clean_data', filename), 'w') as file:
        df.to_csv(file, index=False)


if __name__== "__main__":
    transform_into_csv(20, filename='data.csv')

