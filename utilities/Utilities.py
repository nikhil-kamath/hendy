import json
import os

import pandas as pd

# removes line from file
def f_remove(filepath, line):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    with open(filepath, 'w') as f:
        for line in lines:
            if line.strip('\n') != line:
                f.write(line)

def store(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file)
        
def save_dataframe_as_pickle(dir: str, filename: str, data: pd.DataFrame):
    # save new comments to pickle file
    if not os.path.exists(dir):
        os.mkdir(dir)
    data.to_pickle(os.path.join(dir, filename))
