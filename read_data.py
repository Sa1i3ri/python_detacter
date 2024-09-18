import pandas as pd
import os

#test = pd.read_parquet('defectors\jit_bug_prediction_splits\\random\\test.parquet.gzip')
train = pd.read_parquet('defectors\line_bug_prediction_splits\\random\\train.parquet.gzip')
#val = pd.read_parquet('defectors\jit_bug_prediction_splits\\random\\train.parquet.gzip')

# 确保输出文件夹存在
output_folder = 'dataSet'
os.makedirs(output_folder, exist_ok=True)

start = 190
end = 200


for index in range(start,end):
    row = train.iloc[index]
    # 生成文件名，这里可以根据需要自定义文件名格式
    filename = os.path.join(output_folder, f'train_{index}.txt')
    # 写入文件
    with open(filename, 'w',encoding='utf-8') as file:
        file.write(row.to_string())
        file.write("\n")
        file.write("\n")

        for i in range(0,len(train.iloc[index,6])):
            file.write(str(train.iloc[index,6][i]))
            file.write(" ")

        file.write("\n")
        file.write("\n")
        file.write(train.iloc[index,4].decode('utf-8'))

print("done")


