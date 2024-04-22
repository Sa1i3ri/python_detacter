import pandas as pd

test = pd.read_parquet('defectors\jit_bug_prediction_splits\\random\\test.parquet.gzip')
train = pd.read_parquet('defectors\jit_bug_prediction_splits\\random\\train.parquet.gzip')
val = pd.read_parquet('defectors\jit_bug_prediction_splits\\random\\train.parquet.gzip')
columns = train.columns
len = len(train)


def main():
    print(len)

    firstrow = test.iloc[0]
    print(firstrow)
    print("\n")

    #print(df.iloc[0,4])


if __name__ == "__main__":
    main()
