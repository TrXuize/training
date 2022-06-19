import pandas as pd 

csv_name = '2.csv'
df = pd.read_csv(csv_name, dtype=str)
df['comment'] = df['comment'].apply(lambda x:x.replace('\r\n', '')) # 去換行

df.to_csv(csv_name, index=False, encoding='utf-8')

#df.drop_duplicates(inplace=True)
#df = df.sample(frac=1).reset_index(drop=True)   # 打散

#train_df = df.iloc[:25564]
#dev_df = df.iloc[25564:28759]
#test_df = df.iloc[28759:]
#train_df.to_csv('train.csv', sep=',', index=False)
#dev_df.to_csv('dev.csv', sep=',', index=False)
#test_df.to_csv('test.csv', sep=',', index=False)