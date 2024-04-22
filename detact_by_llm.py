from openai import OpenAI
import httpx

client = OpenAI(
    base_url="https://api.xty.app/v1",
    api_key="sk-8bJniK2upjdWNFnqC53628D8Af5441B5A6145058AaAdA2C4",
    http_client=httpx.Client(
        base_url="https://api.xty.app/v1",
        follow_redirects=True,
    ),
)


def check_quantum_program_bug(program_code):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"I have a python program with a possible bug:\n\n{program_code}\n\n"
                           f"it's a commit record.Is there any bug related to this program?"
                           f"If yes, how can I fix it?",
            }
        ],
        model="gpt-3.5-turbo",
        temperature=0.7,
        top_p=0.3
    )
    return chat_completion


def main():
    with open("dataSet/train_0.txt", "r") as file:
        program_code = file.read()

    suggestion = check_quantum_program_bug(program_code)

    print(suggestion)
    print("\n")
    # 将输出内容写入txt文件
    with open("output.txt", "w") as output_file:
        print(suggestion.choices[0].message.content)
        output_file.write(suggestion.choices[0].message.content)


if __name__ == "__main__":
    main()
