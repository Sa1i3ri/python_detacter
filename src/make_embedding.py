import pickle

from openai import OpenAI
import os


class Embedding:
    def __init__(self):
        pass

    def prepare(self, **kwargs):
        self.model_client = OpenAI(
            base_url=kwargs['base_url'],
            api_key=kwargs['api_key'])
        self.model = kwargs['model']

    def get_text_embeddings(self,save_path, file_path):
        """
        读取文本文件内容并生成嵌入向量。

        参数:
            file_path (str): 文本文件路径。
            model (str): 嵌入模型名称，默认使用 text-embeddings-ada-002。

        返回:
            list: 嵌入向量。
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()  # 从文件中读取内容

            # 调用 OpenAI 嵌入 API
            response = self.model_client.embeddings.create(
                input=content,  # 将文件内容传递为 input
                model='text-embedding-ada-002'
            )
            embedding = response.data[0].embedding
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                pickle.dump(embedding,f)
        except Exception as e:
            print(f"Error generating embeddings for {file_path}: {e}")
            return None



# 使用示例
if __name__ == "__main__":
    # 实例化嵌入生成器
    embedding_generator = Embedding()

    embedding_generator.prepare(
        base_url="",
        api_key="",
        model="text-embedding-ada-002"
    )

    cwes=['CWE-20','CWE-22','CWE-190','CWE-209','CWE-327','CWE-400','CWE-502','CWE-732']
    name1=['1','2','3','p_1','p_2','p_3']
    for cwe in cwes:
        for name in name1:
            embedding_generator.get_text_embeddings(f"../datasets/hand-crafted/embeddings/{cwe}/{name}",
                                            f"../datasets/hand-crafted/ground-truth/{cwe}/{name}.txt")
