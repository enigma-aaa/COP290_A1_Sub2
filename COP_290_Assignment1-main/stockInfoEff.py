import pandas as pd 
from concurrent.futures import ThreadPoolExecutor
df = pd.read_csv('./Data_folder/NSE_Stock_List.csv')
symbols = df['Symbol']
print(symbols)