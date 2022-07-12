import os
import pandas as pd
import random

comments = pd.DataFrame()

folder = './yt'
files = [f for f in os.listdir(
    folder) if os.path.isfile(os.path.join(folder, f))]

for f in files:
    temp = pd.read_pickle(os.path.join(folder, f))
    print(temp.shape)
    comments = pd.concat([comments, temp])
    
print(comments.head(60))
