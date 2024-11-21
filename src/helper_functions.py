import os
import json
import time
import numpy as np
import openai
from statistics import mode
from rouge_score import rouge_scorer
from pydantic import BaseModel, Field

from src.constants import CWES, LANG, PROMPTS_MAP, load_cwe_definitions


class HelperFunctions:
    def __init__(self):
        self.cwes = CWES
        self.defs = load_cwe_definitions()
        self.lang = LANG
        self.prompts_map = PROMPTS_MAP
        super().__init__()

    def fix_edge_cases(self, text):
        """
        处理字符串中的边界情况，例如单个单词过长的问题。

        参数:
            text (str): 输入的文本字符串。

        返回:
            tuple: (bool, str)，第一个值表示是否修复了边界情况，第二个值是修复后的文本。
        """
        # 定义单词的最大长度
        max_length = 100
        # 将文本按空格分割成单词，并计算每个单词的长度
        len_list = list(map(len, text.split()))
        # 检查是否存在单词长度超过最大长度的情况
        if len(len_list) and max(len_list) > max_length:
            # 按空格分割文本为单词列表
            words = text.split()
            # 将超出最大长度的单词截断至最大长度
            truncated_words = [
                word[:max_length] if len(word) > max_length else word
                for word in words
            ]
            # 将处理后的单词重新拼接成字符串
            text = ' '.join(truncated_words)
            # 返回处理结果：修复标志为 True，以及修复后的文本
            return True, text
        # 如果没有超长单词，则返回原始文本和 False 修复标志
        return False, text


    def call_structured_gpt(self, **kwargs):
        """
        调用 GPT 模型并处理请求的函数，具有边界情况处理和错误重试机制。

        参数:
            **kwargs: 可变关键字参数，包含以下必需字段：
                - text (str): 要发送给 GPT 模型的用户输入文本。
                - response_format (str): 希望 GPT 返回的响应格式。

        返回:
            dict 或 None: 如果调用成功，返回 GPT 模型的响应内容；否则返回 None。
        """
        done, itr = False, 5  # 初始化完成标志为 False 和最大重试次数为 5
        while not done and itr:  # 当未完成且重试次数未用完时，继续执行
            try:
                # 检查并修复文本边界情况（例如单词过长的问题）
                fix_required = self.fix_edge_cases(kwargs['text'])  # 调用边界处理函数
                if fix_required[0]:  # 如果需要修复
                    text = fix_required[1]  # 更新修复后的文本
                else:
                    text = kwargs['text']  # 否则使用原始文本
                # 调用 GPT 接口获取响应
                gpt_response = self.gpt_client.beta.chat.completions.parse(
                    model="gpt-4o",  # 指定使用的模型名称
                    messages=[{"role": "user", "content": text}],  # 用户输入内容
                    response_format=kwargs['response_format']  # 指定响应格式
                )
                done = True  # 如果成功获取响应，标记为完成
            except openai.RateLimitError as e:  # 处理 OpenAI 接口速率限制错误
                print("Rate limit reached. Waiting for 60 seconds...")
                time.sleep(60)  # 等待 60 秒后重试
            except openai.APIError as e:  # 处理其他 API 错误
                print(f"Error in extract_pred {e}")  # 输出错误信息
                # 再次检查并修复文本边界情况
                fix_required = self.fix_edge_cases(text)
                if fix_required[0]:  # 如果需要修复
                    text = fix_required[1]  # 更新修复后的文本
                itr -= 1  # 减少剩余重试次数
                print("Retrying...")  # 提示重试
        # 如果成功完成，返回 GPT 的响应内容
        if done:
            response = gpt_response.choices[0].message.parsed  # 提取解析后的响应内容
            return response
        # 如果所有重试都失败，返回 None
        return None

    def extract_pred(self, **kwargs):
        """
        提取 GPT 对于代码是否存在特定安全漏洞的预测结果。

        参数:
            **kwargs: 可变关键字参数，包含以下必需字段：
                - cwe (str): CWE 编号，用于指定待检测的漏洞类型。
                - text (str): 用户提供的文本，通常包含代码和描述。

        返回:
            str 或 None: 返回 GPT 的预测结果（"yes"、"no" 或 "n/a"），
                         如果所有重试都失败，返回 None。
        """
        # 从参数中提取 CWE 编号和文本内容
        cwe = kwargs['cwe']
        content = kwargs['text']

        # 构造要发送给 GPT 的问题（包括上下文文本和问题）
        q = "As a final decision or answer, does the text state that the code contains a security vulnerability known as {}? (Answer yes or no or n/a, incase the text does not provide a definite answer)".format(
            self.cwes[cwe])  # 根据 CWE 编号查找漏洞描述
        text = 'Text: """\n' + content + '\n"""\n' + q  # 拼接完整问题内容

        # 初始化完成标志和重试次数
        done, itr = False, 5
        while not done and itr:  # 如果未完成且仍有重试次数，则继续
            try:
                # 检查并修复文本中的边界情况（如超长单词）
                fix_required = self.fix_edge_cases(text)  # 调用边界处理函数
                if fix_required[0]:  # 如果需要修复
                    text = fix_required[1]  # 使用修复后的文本
                # 调用 GPT 模型发送请求
                gpt_response = self.gpt_client.chat.completions.create(
                    model="gpt-4",  # 使用 GPT-4 模型
                    temperature=0.0,  # 设置生成温度为 0，确保输出稳定
                    messages=[{"role": "user", "content": text}]  # 用户输入内容
                )
                done = True  # 请求成功，标记为完成
            except openai.RateLimitError as e:  # 处理速率限制错误
                print("Rate limit reached. Waiting for 60 seconds...")
                time.sleep(60)  # 等待 60 秒后重试
            except openai.APIError as e:  # 处理其他 API 错误
                print(f"Error in extract_pred {e}")  # 输出错误信息
                # 再次检查并修复文本边界问题
                fix_required = self.fix_edge_cases(text)
                if fix_required[0]:  # 如果需要修复
                    text = fix_required[1]  # 更新修复后的文本
                itr -= 1  # 减少剩余重试次数
                print("Retrying...")  # 提示重试
        if done:  # 如果成功完成
            # 提取 GPT 的预测结果内容
            response = gpt_response.choices[0].message.content  # 获取 GPT 返回的文本
            pred = response.lower()  # 转换为小写（便于后续处理）
            return pred  # 返回预测结果

        # 如果所有重试都失败，返回 None
        return None

    def extract_structured_pred(self, **kwargs):
        """
        提取 GPT 对于代码是否存在特定安全漏洞的结构化预测结果。

        参数:
            **kwargs: 可变关键字参数，包含以下必需字段：
                - cwe (str): CWE 编号，用于指定待检测的漏洞类型。
                - text (str): 用户提供的文本，通常包含代码和描述。

        返回:
            str 或 None: 返回 GPT 的结构化预测结果（"yes"、"no" 或 "n/a"），
                         如果调用失败，返回 None。
        """
        # 从参数中提取 CWE 编号和文本内容
        cwe = kwargs['cwe']
        content = kwargs['text']
        # 构造要发送给 GPT 的问题（包括上下文文本和问题）
        q = f"As a final decision or answer, does the text state that the code contains a security vulnerability known as {self.cwes[cwe]}?"  # 根据 CWE 编号构造问题
        text = f'Text: """\n{content}\n"""\n\n{q}'  # 拼接完整问题内容
        # 定义响应结构，使用 Pydantic 的 BaseModel 验证
        class Response(BaseModel):
            """
            定义 GPT 返回的响应结构。
            """
            answer: str = Field(
                ...,
                description="Answer only in 'yes' or 'no' or 'n/a', in case the text does not provide a definite answer"
            )
        # 调用 GPT 模型以结构化响应格式返回结果
        response = self.call_structured_gpt(text=text, response_format=Response)
        # 如果调用成功，返回 GPT 的预测结果（response.answer）
        if response:
            return response.answer
        # 如果调用失败，返回 None
        return None

    def extract_info(self, **kwargs):
        """
        提取 GPT 对于代码是否存在特定安全漏洞的预测结果，以及原因描述。

        参数:
            **kwargs: 可变关键字参数，包含以下必需字段：
                - cwe (str): CWE 编号，用于指定待检测的漏洞类型。
                - text (str): 用户提供的文本，通常包含代码和描述。

        返回:
            tuple: (str, str)，第一个值为预测结果（"yes"、"no" 或 "n/a"），
                   第二个值为原因描述（或 "n/a" 如果无法提供原因）。
        """
        # 从参数中提取 CWE 编号和文本内容
        cwe = kwargs['cwe']
        content = kwargs["text"]

        # 构造系统提示内容，指定 GPT 的输出格式和规则
        sys = (
            "You are a helpful assistant who extracts answer whether an instance of vulnerability is present or not "
            "and its reason 'why' from the given text in the following format:\nAnswer: ...\nReason: ...\n\n"
            "You must follow these rules while extracting information:\n"
            "1. As a final decision or answer, does the text state that the code contains a security vulnerability known as {}? "
            "(Answer yes or no or n/a, incase the text does not provide a definite answer)\n"
            "2. If the text does not state the reason 'why' an instance of vulnerability is present or not then just write 'n/a' in reason.\n"
            "3. If the answer in 1 is 'n/a' then just write 'n/a' in reason.\n"
            "4. Only if 2 and 3 are not true then briefly describe the reasons mentioned in the text that state 'why' the code does or does not contain a security vulnerability known as {}. Max word limit for reason is 100 words. Write in terms of code, e.g., 'The code/program/function ...'"
        ).format(self.cwes[cwe], self.cwes[cwe])  # 根据 CWE 编号构造规则

        # 初始化完成标志和重试次数
        done, itr = False, 5

        while not done and itr:  # 如果未完成且仍有重试次数，则继续
            try:
                # 检查并修复文本中的边界情况（如超长单词）
                fix_required = self.fix_edge_cases(content)
                if fix_required[0]:  # 如果需要修复
                    content = fix_required[1]  # 更新修复后的文本

                # 调用 GPT 模型发送请求
                gpt_response = self.gpt_client.chat.completions.create(
                    model="gpt-4",  # 使用 GPT-4 模型
                    temperature=0.0,  # 设置生成温度为 0，确保输出稳定
                    messages=[
                        {"role": "system", "content": sys},  # 系统指令
                        {"role": "user", "content": content}  # 用户输入内容
                    ]
                )
                done = True  # 请求成功，标记为完成
            except openai.RateLimitError as e:  # 处理速率限制错误
                print("Rate limit reached. Waiting for 60 seconds...")
                time.sleep(60)  # 等待 60 秒后重试
            except openai.APIError as e:  # 处理其他 API 错误
                print(f"Error in extract_info {e}")  # 输出错误信息
                # 再次检查和修复文本边界问题
                fix_required = self.fix_edge_cases(content)
                if fix_required[0]:  # 如果需要修复
                    content = fix_required[1]  # 更新修复后的文本
                itr -= 1  # 减少剩余重试次数
                print("Retrying...")  # 提示重试

        # 初始化预测结果和原因
        pred, reason = None, None
        if done:  # 如果请求成功
            # 提取 GPT 的预测结果和原因
            response = gpt_response.choices[0].message.content  # 获取 GPT 返回的完整响应
            pred = response.split('\n')[0].split('Answer:')[-1][1:].lower()  # 提取 "Answer" 字段并转换为小写
            if pred == "n/a":  # 如果答案为 "n/a"
                reason = "n/a"  # 原因也设置为 "n/a"
            else:  # 否则提取 "Reason" 字段
                reason = response.split('Reason:')[-1][1:]
        return pred, reason  # 返回预测结果和原因

    def extract_structured_info(self, **kwargs):
        """
        提取 GPT 对于代码是否存在特定安全漏洞的结构化预测结果，以及原因描述。

        参数:
            **kwargs: 可变关键字参数，包含以下必需字段：
                - cwe (str): CWE 编号，用于指定待检测的漏洞类型。
                - text (str): 用户提供的文本，通常包含代码和描述。

        返回:
            tuple: (str, str)，第一个值为预测结果（"yes"、"no" 或 "n/a"），
                   第二个值为原因描述（或 "n/a" 如果无法提供原因）。
        """
        # 从参数中提取 CWE 编号和文本内容
        cwe = kwargs['cwe']
        content = kwargs['text']
        # 构造问题描述
        q = (
            "You are a helpful assistant who extracts answer whether an instance of vulnerability is present or not "
            "and its reason 'why' from the given text."
        )
        # 拼接输入文本和问题
        text = f'Text: """\n{content}\n"""\n\n{q}'
        # 定义响应结构模型，使用 Pydantic 验证
        class Response(BaseModel):
            """
            定义 GPT 返回的结构化响应模型。
            """
            answer: str = Field(
                ...,
                description=f"As a final decision or answer, does the text state that the code contains a security vulnerability known as {self.cwes[cwe]}? (Answer only in 'yes' or 'no' or 'n/a', in case the text does not provide a definite answer)"
            )
            reason: str = Field(
                ...,
                description="Reason described in the text that states 'why' the code does or does not contain a security vulnerability known as {self.cwes[cwe]}. (Describe only in Max 100 words) If the answer is 'n/a' then just write 'n/a' in reason. And if no reason is provided then just write 'n/a' in reason. Write in terms of code, e.g., 'The code/program/function ...'"
            )
        # 调用 GPT 模型以结构化响应格式返回结果
        response = self.call_structured_gpt(text=text, response_format=Response)
        # 如果调用成功，返回结构化的预测结果和原因描述
        if response:
            return response.answer, response.reason
        # 如果调用失败，返回 (None, None)
        return None, None

    def rouge(self, **kwargs):
        """
        计算 ROUGE-1 精确度分数，用于比较预测的原因描述与真实答案之间的相似性。

        参数:
            **kwargs: 可变关键字参数，包含以下必需字段：
                - reason (str): 预测的原因描述。
                - ground_truth (str): 真实答案的原因描述。

        返回:
            float: ROUGE-1 的精确度分数。
        """
        # 初始化一个 ROUGE 评分器，支持 'rouge1' 和 'rougeL' 指标，启用词干化
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
        # 使用提供的 'reason' 和 'ground_truth' 计算 ROUGE 分数
        scores = scorer.score(kwargs['reason'], kwargs['ground_truth'])
        # 返回 ROUGE-1 指标中的精确度分数
        return scores['rouge1'].precision

    def cos_similarity(self, **kwargs):
        """
        计算预测原因描述和真实答案之间的余弦相似度。

        参数:
            **kwargs: 可变关键字参数，包含以下必需字段：
                - reason (str): 预测的原因描述。
                - ground_truth (np.array): 真实答案的向量表示。

        返回:
            float: 预测描述和真实答案之间的余弦相似度。如果失败，返回 None。
        """
        # 初始化完成标志和最大重试次数
        done, itr = False, 5
        while not done and itr:  # 如果未完成且仍有重试次数，则继续
            try:
                # 调用 GPT-3.5 大型嵌入模型获取 `reason` 的向量表示
                resp = self.gpt_client.embeddings.create(
                    input=[kwargs['reason']],  # 输入为预测的原因描述
                    model='text-embedding-ada-002'  # 使用指定的嵌入模型
                )
                # 从返回的响应中提取嵌入向量
                embedding_a = resp.data[0].embedding
                done = True  # 请求成功，标记为完成
            except openai.RateLimitError as e:  # 处理速率限制错误
                print("Rate limit reached. Waiting for 60 seconds...")
                time.sleep(60)  # 等待 60 秒后重试
            except openai.APIError as e:  # 处理其他 API 错误
                print(f"Error in cos_similarity {e}")  # 输出错误信息
                itr -= 1  # 减少剩余重试次数
                print("Retrying...")  # 提示重试
        # 初始化相似度分数为 None
        similarity_score = None
        if done:  # 如果嵌入向量提取成功
            # 使用点积计算嵌入向量和真实答案之间的余弦相似度
            similarity_score = np.dot(embedding_a, kwargs['ground_truth'])
        # 返回计算的余弦相似度分数
        return similarity_score

    def gpt_eval(self, **kwargs):
        """
        使用 GPT 评估预测的原因描述是否与真实答案对齐。

        参数:
            **kwargs: 可变关键字参数，包含以下必需字段：
                - reason (str): 预测的原因描述。
                - ground_truth (str): 真实答案的原因描述。

        返回:
            str 或 None: 返回评估结果（"yes" 或 "no"），如果调用失败则返回 None。
        """
        # 从参数中提取原因描述和真实答案
        reason = kwargs['reason']
        gt = kwargs['ground_truth']
        # 构造用于评估的提示文本
        q = "Evaluate if the reasoning in the response aligns with the ground truth. (Answer yes or no)"
        prompt = (
                q
                + '\n\nResponse: """\n'
                + reason
                + '\n"""\n\nGround Truth: """\n'
                + gt
                + '\n"""'
        )
        # 初始化重试次数
        itr = 5
        while itr:  # 如果仍有重试次数，则继续尝试
            try:
                # 调用 GPT API 生成响应
                gpt_response = self.gpt_client.chat.completions.create(
                    model="gpt-4",  # 使用 GPT-4 模型
                    temperature=0.0,  # 设置生成温度为 0，确保输出稳定
                    messages=[{"role": "user", "content": prompt}]  # 提供用户输入
                )
                # 从 GPT 响应中提取答案并转换为小写
                answer = gpt_response.choices[0].message.content.lower()
                return answer  # 返回评估结果
            except openai.RateLimitError as e:  # 处理速率限制错误
                print("Rate limit reached. Waiting for 60 seconds...")
                time.sleep(60)  # 等待 60 秒后重试
            except openai.APIError as e:  # 处理其他 API 错误
                print(f"Error in gpt_eval {e}")  # 输出错误信息
                itr -= 1  # 减少剩余重试次数
                print("Retrying...")  # 提示重试
        # 如果所有重试都失败，返回 None
        return None

    def gpt_structured_eval(self, **kwargs):
        """
        使用 GPT 以结构化方式评估预测的原因描述是否与真实答案对齐。

        参数:
            **kwargs: 可变关键字参数，包含以下必需字段：
                - reason (str): 预测的原因描述。
                - ground_truth (str): 真实答案的原因描述。

        返回:
            str 或 None: 返回评估结果（"yes" 或 "no"），如果调用失败则返回 None。
        """
        # 从参数中提取原因描述和真实答案
        reason = kwargs['reason']
        gt = kwargs['ground_truth']
        # 构造用于评估的提示文本
        q = "Evaluate if the reasoning in the response aligns with the ground truth."
        prompt = f'{q}\n\nResponse: """\n{reason}\n"""\n\nGround Truth: """\n{gt}\n"""'
        # 定义响应结构模型，使用 Pydantic 验证
        class Response(BaseModel):
            """
            定义 GPT 返回的结构化响应模型。
            """
            answer: bool = Field(
                ...,
                description="True if the reasoning in the response aligns with the ground truth, otherwise False"
            )
        # 调用 GPT 模型以结构化响应格式返回结果
        response = self.call_structured_gpt(text=prompt, response_format=Response)
        # 如果调用成功，返回 'yes' 或 'no'，根据结构化响应的布尔值决定
        if response:
            answer = 'yes' if response.answer else 'no'
            return answer

        # 如果调用失败，返回 None
        return None

    def check_consistency(self, **kwargs):
        """
        检查预测结果在指定条件下是否一致，并包含错误处理。
        """
        prompt = kwargs['prompt']
        temp = kwargs['temp']
        model = kwargs['model']
        result_path = kwargs['result_path']
        result_name = 'temp'
        result_full_path = os.path.join(result_path, result_name + ".json")
        try:
            # 加载结果数据
            with open(result_full_path, "r", encoding='utf-8') as file:
                results = json.load(file)
        except FileNotFoundError:
            print(f"File not found: {result_full_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return False
        # 遍历并检查一致性
        for cwe in results.get(prompt, {}).get(temp, {}).get(model, {}):
            for file in results[prompt][temp][model][cwe]:
                first_pred = results[prompt][temp][model][cwe][file]["1"]["pred"]
                for i in results[prompt][temp][model][cwe][file]:
                    pred = results[prompt][temp][model][cwe][file][i]["pred"]
                    if first_pred != pred:
                        return True
        return False

    def handle_reason(self, r, c, g):
        """
        基于 ROUGE 分数、余弦相似度以及 GPT 评估结果，判断预测的原因描述是否合理。

        参数:
            r (float): ROUGE 分数，用于衡量预测原因和真实答案之间的文本相似性。
            c (float): 余弦相似度分数，用于衡量预测原因和真实答案之间的语义相似性。
            g (str): GPT 评估结果，为 "yes" 或 "no"，表示预测原因是否与真实答案一致。

        返回:
            int: 决策结果（1 表示预测原因合理，0 表示不合理），基于多数表决的结果。
        """
        # 定义阈值
        ROUGE_THRES = 0.34  # ROUGE 分数阈值
        COS_SIM_THRES = 0.84  # 余弦相似度分数阈值
        # 基于三个指标生成决策值列表：
        # - ROUGE 分数高于阈值时为 1，否则为 0。
        # - 余弦相似度分数高于阈值时为 1，否则为 0。
        # - GPT 评估结果为 "yes" 时为 1，否则为 0。
        decisions = [
            1 if r >= ROUGE_THRES else 0,  # 判断 ROUGE 分数是否超过阈值
            1 if c >= COS_SIM_THRES else 0,  # 判断余弦相似度是否超过阈值
            1 if g == 'yes' else 0  # 判断 GPT 评估结果是否为 "yes"
        ]

        # 使用多数表决的方式确定最终决策
        return mode(decisions)

    def get_score(self, data):
        """
        根据回答率、准确率和原因正确率计算综合得分。

        参数:
            data (dict): 包含统计数据的字典，包括以下字段：
                - 'total_answered': 已回答问题的数量（字典，包含 'val' 键）。
                - 'no_answer': 未回答问题的数量（字典，包含 'val' 键）。
                - 'correct': 回答正确的问题数量（字典，包含 'val' 键）。
                - 'correct_pred_correct_reason': 预测正确且原因正确的问题数量（字典，包含 'val' 键）。
                - 'correct_pred_incorrect_reason': 预测正确但原因不正确的问题数量（字典，包含 'val' 键）。

        返回:
            float: 综合得分，基于三个加权指标。
        """
        # 定义权重
        W1, W2, W3 = 0.33, 0.33, 0.33  # 回答率、准确率、原因正确率的权重
        # 计算回答率 (res_rate)
        total_res = data['total_answered']['val'] + data['no_answer']['val']  # 总问题数量
        res_rate = (data['total_answered']['val'] / total_res) if total_res else 0  # 已回答问题的比例
        # 计算准确率 (acc_rate)
        acc_rate = (data['correct']['val'] / data['total_answered']['val']) if data['total_answered']['val'] else 0  # 回答正确的比例
        # 计算原因正确率 (rea_rate)
        total_rea = data['correct_pred_correct_reason']['val'] + data['correct_pred_incorrect_reason']['val']  # 总预测数量
        rea_rate = (data['correct_pred_correct_reason']['val'] / total_rea) if total_rea else 0  # 预测正确且原因正确的比例
        # 计算综合得分
        return (W1 * res_rate) + (W2 * acc_rate) + (W3 * rea_rate)

    def get_best_prompt(self, data, model, prompts):
        """
        根据给定模型和提示集，找到得分最高的提示及其对应的得分。

        参数:
            data (dict): 包含模型和提示的结果数据。
            model (str): 指定的模型名称，用于在数据中定位结果。
            prompts (list): 提示集（prompt），用于评估各提示的表现。

        返回:
            tuple: (float, str)，第一个值为最高得分，第二个值为对应的提示（prompt）。
        """
        # 初始化最高得分和最佳提示
        max_score = 0
        max_prompt = ''
        # 遍历提示集
        for p in prompts:
            # 计算当前提示的得分
            score = self.get_score(data[model][p])
            # 如果当前提示的得分高于最高得分，更新最高得分和最佳提示
            if score > max_score:
                max_score = score
                max_prompt = p
        # 返回最高得分和最佳提示
        return max_score, max_prompt

    def get_model_best_prompts(self, data, model, zt, zr, ft, fr):
        """
        根据模型的多个提示集，找到每组提示集中的最佳提示，并总结结果。

        参数:
            data (dict): 包含模型和提示的结果数据。
            model (str): 指定的模型名称。
            zt (list): 零样本任务的提示集（Zero-shot Task, ZT）。
            zr (list): 零样本原因的提示集（Zero-shot Reason, ZR）。
            ft (list): 少样本任务的提示集（Few-shot Task, FT）。
            fr (list): 少样本原因的提示集（Few-shot Reason, FR）。

        返回:
            dict: 包含以下键值对的字典：
                - 'ZT': 零样本任务中得分最高的提示。
                - 'ZR': 零样本原因中得分最高的提示。
                - 'ZS': 零样本最佳提示（在 ZT 和 ZR 中选择得分最高的）。
                - 'FT': 少样本任务中得分最高的提示。
                - 'FR': 少样本原因中得分最高的提示。
                - 'FS': 少样本最佳提示（在 FT 和 FR 中选择得分最高的）。
        """
        # 找到零样本任务 (ZT) 和零样本原因 (ZR) 的最佳提示及其得分
        zt_s, zt_p = self.get_best_prompt(data, model, zt)
        zr_s, zr_p = self.get_best_prompt(data, model, zr)

        # 找到少样本任务 (FT) 和少样本原因 (FR) 的最佳提示及其得分
        ft_s, ft_p = self.get_best_prompt(data, model, ft)
        fr_s, fr_p = self.get_best_prompt(data, model, fr)

        # 比较 ZT 和 ZR 的得分，选择得分更高的提示作为 ZS
        zs = zt_p if zt_s > zr_s else zr_p

        # 比较 FT 和 FR 的得分，选择得分更高的提示作为 FS
        fs = ft_p if ft_s > fr_s else fr_p

        # 构造结果字典
        result = {
            'ZT': zt_p,  # 零样本任务最佳提示
            'ZR': zr_p,  # 零样本原因最佳提示
            'ZS': zs,  # 零样本总体最佳提示
            'FT': ft_p,  # 少样本任务最佳提示
            'FR': fr_p,  # 少样本原因最佳提示
            'FS': fs  # 少样本总体最佳提示
        }

        return result

    def find_best_prompts(self, **kwargs):
        """
        基于模型的预测结果计算各种指标，选择最佳提示（prompts）。

        参数:
            **kwargs: 可变关键字参数，包含以下必需字段：
                - model (str): 指定的模型名称。
                - result_path (str): 存储预测结果的路径。

        返回:
            dict: 包含最佳提示的 JSON 数据。
        """
        model = kwargs['model']
        result_path = kwargs['result_path']

        # 加载结果数据
        result_name = model + '.json'
        result_full_path = os.path.join(result_path, result_name)
        with open(result_full_path, "r", encoding='utf-8') as file:
            results = json.load(file)

        # 初始化指标数据结构
        metric_data = {}
        if model not in metric_data:
            metric_data[model] = {}

        # 遍历结果文件，计算各项指标
        for cwe in results:
            for file in results[cwe]:
                for prompt in results[cwe][file]:
                    # 初始化每个提示的指标
                    if prompt not in metric_data[model]:
                        metric_data[model][prompt] = {
                            "total_answered": {'val': 0, 'id': []},
                            "no_answer": {'val': 0, 'id': []},
                            "correct": {'val': 0, 'id': []},
                            "total_reasoned": {'val': 0, 'id': []},
                            "no_reason": {'val': 0, 'id': []},
                            "correct_pred_correct_reason": {'val': 0, 'id': []},
                            "incorrect_pred_correct_reason": {'val': 0, 'id': []},
                            "correct_pred_incorrect_reason": {'val': 0, 'id': []},
                            "incorrect_pred_incorrect_reason": {'val': 0, 'id': []}
                        }

                    # 获取预测结果
                    pred = results[cwe][file][prompt]['pred']

                    # 未回答的问题
                    if pred != 'yes' and pred != 'no':
                        metric_data[model][prompt]['no_answer']['val'] += 1
                        metric_data[model][prompt]['no_answer']['id'].append((cwe, file, prompt))
                    else:
                        # 已回答的问题
                        metric_data[model][prompt]['total_answered']['val'] += 1

                        # 判断回答是否正确
                        label = 0 if file[0] == 'p' else 1
                        p = 1 if pred == 'yes' else 0
                        correct = (p == label)
                        if correct:
                            metric_data[model][prompt]['correct']['val'] += 1
                            metric_data[model][prompt]['correct']['id'].append((cwe, file, prompt))

                        # 判断原因描述是否存在
                        reason = results[cwe][file][prompt]['reason']
                        if reason == 'n/a':
                            metric_data[model][prompt]['no_reason']['val'] += 1
                            metric_data[model][prompt]['no_reason']['id'].append((cwe, file, prompt))
                        else:
                            metric_data[model][prompt]['total_reasoned']['val'] += 1

                            # 获取指标：ROUGE 分数、余弦相似度、GPT 评估
                            rouge = results[cwe][file][prompt]['rouge']
                            cos = results[cwe][file][prompt]['cos_sim']
                            gpt = results[cwe][file][prompt]['gpt_eval']

                            # 根据原因正确性更新指标
                            if self.handle_reason(rouge, cos, gpt) == 1:
                                if correct:
                                    metric_data[model][prompt]['correct_pred_correct_reason']['val'] += 1
                                    metric_data[model][prompt]['correct_pred_correct_reason']['id'].append(
                                        (cwe, file, prompt))
                                else:
                                    metric_data[model][prompt]['incorrect_pred_correct_reason']['val'] += 1
                                    metric_data[model][prompt]['incorrect_pred_correct_reason']['id'].append(
                                        (cwe, file, prompt))
                            else:
                                if correct:
                                    metric_data[model][prompt]['correct_pred_incorrect_reason']['val'] += 1
                                    metric_data[model][prompt]['correct_pred_incorrect_reason']['id'].append(
                                        (cwe, file, prompt))
                                else:
                                    metric_data[model][prompt]['incorrect_pred_incorrect_reason']['val'] += 1
                                    metric_data[model][prompt]['incorrect_pred_incorrect_reason']['id'].append(
                                        (cwe, file, prompt))

        # 根据 prompts_map 分类提示为不同类型
        zs_to, zs_ro, fs_to, fs_ro = [], [], [], []
        for p in self.prompts_map:
            if self.prompts_map[p][0] == 'ZS' and self.prompts_map[p][1] == 'TO':
                zs_to.append(p)
            elif self.prompts_map[p][0] == 'ZS' and self.prompts_map[p][1] == 'RO':
                zs_ro.append(p)
            elif self.prompts_map[p][0] == 'FS' and self.prompts_map[p][1] == 'TO':
                fs_to.append(p)
            elif self.prompts_map[p][0] == 'FS' and self.prompts_map[p][1] == 'RO':
                fs_ro.append(p)

        # 获取最佳提示
        best_prompts_json = self.get_model_best_prompts(metric_data, model, zs_to, zs_ro, fs_to, fs_ro)

        return best_prompts_json
