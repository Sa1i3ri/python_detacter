import pandas as pd
import os

test = pd.read_parquet('defectors\jit_bug_prediction_splits\\random\\test.parquet.gzip')
train = pd.read_parquet('defectors\jit_bug_prediction_splits\\random\\train.parquet.gzip')
val = pd.read_parquet('defectors\jit_bug_prediction_splits\\random\\train.parquet.gzip')

# 确保输出文件夹存在
output_folder = 'dataSet'
os.makedirs(output_folder, exist_ok=True)

start = 10
num = 10

# 遍历数据并写入单独的文件
for index in range(start,start+num):
    row = train.iloc[index]
    # 生成文件名，这里可以根据需要自定义文件名格式
    filename = os.path.join(output_folder, f'train_{index}.txt')
    # 写入文件
    with open(filename, 'a') as file:
        file.write(row.to_string())
        file.write(train.iloc[index,4])


