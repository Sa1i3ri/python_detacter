import os
from openai import OpenAI
import httpx
import tiktoken  # 用于计算token

max_token = 15000  # 最大token限制
train_start = 30
tran_end = 40 # 训练数据的起始和结束索引

# 创建OpenAI客户端
client = OpenAI(
    base_url="https://api.xty.app/v1",  # API的基础URL
    api_key="sk-8bJniK2upjdWNFnqC53628D8Af5441B5A6145058AaAdA2C4",  # API密钥
    http_client=httpx.Client(
        base_url="https://api.xty.app/v1",  # HTTP客户端的基础URL
        follow_redirects=True,  # 是否跟随重定向
    ),
)

# 检查量子程序中的错误
def check_quantum_program_bug(program_code):
    # 创建聊天完成请求
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"I have a python program with some possible bugs:\n\n{program_code}\n\n"
                           f"it's a commit record. Is there any bug related to this program?"
                           f"If yes, show all line numbers of the buggy code segment."
                           f"Please detect the bugs."
            }
        ],
        model="gpt-3.5-turbo",  # 使用的模型
        temperature=0.7,  # 生成文本的随机性
        top_p=0.3  # 生成文本的多样性
    )
    return chat_completion

# 计算文本的token数量
def count_tokens(text, model="gpt-3.5-turbo"):
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))

# 分割文本为多个段落，每段不超过token限制
def split_into_chunks(program_code, max_tokens=max_token, model="gpt-3.5-turbo"):
    encoder = tiktoken.encoding_for_model(model)
    tokens = encoder.encode(program_code)

    # 将tokens按最大token限制分段
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunk = encoder.decode(chunk_tokens)
        chunks.append(chunk)
        start = end
    return chunks

# 主函数
def main():
    output_folder = 'output'  # 输出文件夹
    os.makedirs(output_folder, exist_ok=True)  # 确保输出文件夹存在

    for index in range(train_start,tran_end):
        filename = os.path.join(output_folder, f'output_{index}.txt')  # 输出文件名
        with open(f"dataSet/train_{index}.txt", "r", errors='replace') as file:  # 读取训练数据文件
            program_code = file.read()  # 读取文件内容

        # 计算文本的token数量
        token_count = count_tokens(program_code)

        # 如果超过token限制，进行分段请求
        if token_count > max_token:
            program_chunks = split_into_chunks(program_code, max_tokens=max_token)
            full_suggestion = ""
            for chunk in program_chunks:
                suggestion = check_quantum_program_bug(chunk)  # 分段检查程序中的错误
                full_suggestion += suggestion.choices[0].message.content  # 拼接结果
        else:
            suggestion = check_quantum_program_bug(program_code)  # 不分段的情况下检查错误
            full_suggestion = suggestion.choices[0].message.content

        print(full_suggestion)  # 打印建议
        print("\n")
        # 将输出内容写入txt文件
        with open(filename, "w") as output_file:
            output_file.write(full_suggestion)  # 写入建议内容

if __name__ == "__main__":
    main()
