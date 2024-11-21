import os
import json
import pickle

from openai import OpenAI
from tqdm import tqdm
import openai

class ExperimentRunner:
    ############################
    # 实验
    ############################

    def run_temp_test(self, **kwargs):
        '''
        这个函数对给定模型的指定温度运行测试。

        参数:
        ----------
            api_key: openai 的 api 密钥 (str)
            temp: 模型的推荐温度 (float)
            model: 模型名称 (str)
            k: 运行实验的次数 (int)
            do_reason: 是否需要评估原因? (bool)
            cwe_files: 要运行测试的 CWE 和文件的名称 (tuple(str, str)) 例如 ("cwe-787", "1.c")
            prompt: 测试时使用的提示 (str) ['RecTemp' 用于测试推荐温度]
            dataset_path: 数据集的路径 (str)
            result_path: 结果文件的路径 (str)

        返回值:
        --------
            无

        操作:
        --------
            在给定模型上运行实验 'k' 次，并将结果保存在结果文件中。
            {
                "prompt": {
                    "temp": {
                        "cwe": {
                            "file": {
                                "1": {
                                    "content": "response",
                                    "pred": "yes/no/n/a",
                                    "reason": "reason/n/a",
                                    "rouge": "rouge 分数",
                                    "cos_sim": "余弦相似度分数",
                                    "gpt_eval": "yes/no"
                                },
                                ...
                                "k": {
                                    "content": "response",
                                    "pred": "yes/no/n/a",
                                    "reason": "reason/n/a",
                                    "rouge": "rouge 分数",
                                    "cos_sim": "余弦相似度分数",
                                    "gpt_eval": "yes/no"
                                }
                            },
                            ...
                        },
                        ...
                    },
                    ...
                }
            }
        '''
        self.gpt_client = OpenAI(
            base_url=kwargs['base_url'],
            api_key=kwargs['api_key']
        )
        self.temp = kwargs['temp']
        temp = str(self.temp)
        model = kwargs['model']
        k = kwargs['k']
        do_reason = kwargs['do_reason']
        do_extract = kwargs['do_extract'] if 'do_extract' in kwargs else True
        cwe_files = kwargs['cwe_files']
        prompt = kwargs['prompt']
        dataset_path = kwargs['dataset_path']
        result_path = kwargs['result_path']
        result_full_path = os.path.join(result_path, model + ".json")

        # 检查结果文件是否存在
        try:
            with open(result_full_path, "r", encoding='utf-8') as file:
                file_contents = file.read()
                results = json.loads(file_contents) if file_contents else {}
        except FileNotFoundError:
            print("文件未找到。")
            results = {}
        except json.JSONDecodeError:
            print("无效的 JSON。")
            results = {}

        try:
            # 检查提示是否存在（即测试是否已运行，或是否在运行中）
            print("\n正在运行实验 {}".format(prompt))
            if prompt not in results:
                print("为 {} 创建新条目".format(prompt))
                results[prompt] = {}

            # 检查温度是否存在（即测试是否已运行，或是否在运行中，或新的测试正在运行）
            print("\n正在运行实验 {}".format(self.temp))
            if temp not in results[prompt]:
                print("为 {} 创建新条目".format(self.temp))
                results[prompt][temp] = {}

            # 对所有文件运行实验
            for cwe, file in cwe_files:
                cwe_path = os.path.join(dataset_path, 'dataset', cwe.upper(), file)
                print("\n正在为 {} 运行实验".format(cwe_path))
                # 检查 CWE 是否存在（即测试是否已运行，或是否在运行中）
                if cwe not in results[prompt][temp]:
                    results[prompt][temp][cwe] = {}

                # 检查文件是否存在（即测试是否已运行，或是否在运行中）
                if file not in results[prompt][temp][cwe]:
                    results[prompt][temp][cwe][file] = {}

                code = open(cwe_path, "r", encoding='utf-8').read()
                # 将实验运行 'k' 次
                for i in range(1, k + 1):
                    ix = str(i)
                    print("\n第 {} 次迭代".format(ix))
                    # 检查实验是否已运行
                    if ix not in results[prompt][temp][cwe][file]:
                        results[prompt][temp][cwe][file][ix] = {}

                    # 检查内容是否已生成
                    if "content" not in results[prompt][temp][cwe][file][ix]:
                        response = self.prompts[prompt](cwe=cwe, code=code)
                        if not response:
                            open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))
                            return
                        results[prompt][temp][cwe][file][ix]["content"] = response
                    print("响应已完成!!")

                    # 提取信息
                    # 如果 do_reason 为 False，则仅提取预测结果
                    if not do_reason and do_extract:
                        if "pred" not in results[prompt][temp][cwe][file][ix]:
                            pred = self.extract_structured_pred(cwe=cwe,
                                                                text=results[prompt][temp][cwe][file][ix]["content"])
                            if pred == None:
                                open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))
                                return
                            results[prompt][temp][cwe][file][ix]["pred"] = pred
                        print("提取完成!!")
                    # 如果 do_reason 为 True，则提取预测结果和原因
                    if do_reason:
                        if "pred" not in results[prompt][temp][cwe][file][ix] or "reason" not in \
                                results[prompt][temp][cwe][file][ix]:
                            pred, reason = self.extract_structured_info(cwe=cwe,
                                                                        text=results[prompt][temp][cwe][file][ix][
                                                                            "content"])
                            if pred == None or reason == None:
                                open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))
                                return
                            results[prompt][temp][cwe][file][ix]["pred"] = pred
                            results[prompt][temp][cwe][file][ix]["reason"] = reason
                        print("提取完成!!")

                        # 检查原因是否为 n/a
                        if results[prompt][temp][cwe][file][ix]["reason"] == "n/a":
                            results[prompt][temp][cwe][file][ix]["rouge"] = None
                            results[prompt][temp][cwe][file][ix]["cos_sim"] = None
                            results[prompt][temp][cwe][file][ix]["gpt_eval"] = None

                        # 使用真实值进行评估
                        gt = open(os.path.join(dataset_path, 'ground-truth', cwe.upper(), file.split(".")[0] + ".txt"),
                                  "r", encoding='utf-8').read()

                        # 1) 计算 rouge 分数
                        if "rouge" not in results[prompt][temp][cwe][file][ix]:
                            rouge_score = self.rouge(reason=results[prompt][temp][cwe][file][ix]["reason"],
                                                     ground_truth=gt)
                            results[prompt][temp][cwe][file][ix]["rouge"] = rouge_score
                        print("Rouge 完成!!")

                        # 2) 计算余弦相似度
                        if "cos_sim" not in results[prompt][temp][cwe][file][ix]:
                            gt_emb = None
                            with open(os.path.join(dataset_path, 'embeddings', cwe.upper(), file.split(".")[0]),
                                      "rb") as f:
                                gt_emb = pickle.load(f)
                            cos_sim = self.cos_similarity(reason=results[prompt][temp][cwe][file][ix]["reason"],
                                                          ground_truth=gt_emb)
                            if cos_sim == None:
                                open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))
                                return
                            results[prompt][temp][cwe][file][ix]["cos_sim"] = cos_sim
                        print("余弦相似度计算完成!!")

                        # 3) 计算 GPT 评估
                        if "gpt_eval" not in results[prompt][temp][cwe][file][ix]:
                            gpt_eval = self.gpt_structured_eval(reason=results[prompt][temp][cwe][file][ix]["reason"],
                                                                ground_truth=gt)
                            if not gpt_eval:
                                open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))
                                return
                            results[prompt][temp][cwe][file][ix]["gpt_eval"] = gpt_eval
                        print("GPT 评估完成!!")
        finally:
            # 保存结果
            open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))

    def run_prompts_experiments(self, **kwargs):
        '''
        这个函数使用给定的提示对指定模型运行实验。

        参数:
        ----------
            api_key: OpenAI 的 API 密钥 (str)
            temp: 模型的推荐温度 (float)
            model: 模型名称 (str)
            dataset_path: 数据集路径 (str)
            result_path: 结果文件路径 (str)

        返回值:
        --------
            无

        操作:
        --------
            在给定模型上运行实验并将结果保存在结果文件中。
            {
                "CWE-X": {
                    "file": {
                        "prompt": {
                            "content": "response",
                            "label": "0/1",
                            "pred": "yes/no/n/a",
                            "reason": "reason/n/a",
                            "rouge": "rouge 分数",
                            "cos_sim": "余弦相似度分数",
                            "gpt_eval": "yes/no"
                        },
                        ...
                    },
                    ...
                },
            }
        '''
        self.gpt_client = OpenAI(api_key=kwargs['api_key'])
        self.temp = kwargs['temp']
        model = kwargs['model']
        dataset_path = kwargs['dataset_path']
        result_path = kwargs['result_path']
        result_full_path = os.path.join(result_path, model + ".json")

        # 如果结果文件存在则加载内容，否则初始化为空字典
        results = {} if not os.path.isfile(result_full_path) else json.loads(
            open(result_full_path, "r", encoding='utf-8').read())

        try:
            print("\n正在为模型 {} 运行实验".format(model))
            # 遍历所有目录 (CWEs)
            for dir in tqdm(os.listdir(os.path.join(dataset_path, 'dataset'))):
                # 检查目录名称是否有效
                cwe = dir.lower()
                if cwe not in self.cwes:
                    continue

                print("\n正在为 CWE {} 运行实验".format(cwe))
                if cwe not in results:
                    results[cwe] = {}

                # 遍历所有文件
                for file in os.listdir(os.path.join(dataset_path, 'dataset', dir)):
                    print("\n正在处理文件 {}".format(file))
                    if file.endswith(".c") or file.endswith(".py"):
                        label = 0 if file[0] == 'p' else 1  # 根据文件名称确定标签

                        # 如果文件不存在于结果中，初始化该文件的条目
                        if file not in results[cwe]:
                            results[cwe][file] = {}

                        # 读取代码内容
                        code = open(os.path.join(dataset_path, 'dataset', dir, file), "r", encoding='utf-8').read()

                        # 遍历所有提示
                        for prompt in self.prompts:
                            print("\n-> 正在处理提示: {}".format(prompt))
                            if prompt not in results[cwe][file]:
                                results[cwe][file][prompt] = {}
                            if "content" not in results[cwe][file][prompt]:
                                response = self.prompts[prompt](cwe=cwe, code=code)
                                if not response:
                                    open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))
                                    return
                                results[cwe][file][prompt]["content"] = response
                                results[cwe][file][prompt]["label"] = label
                            print("响应生成完成!!")

                            # 提取信息
                            if "pred" not in results[cwe][file][prompt] or "reason" not in results[cwe][file][prompt]:
                                pred, reason = self.extract_structured_info(cwe=cwe,
                                                                            text=results[cwe][file][prompt]["content"])
                                if pred is None or reason is None:
                                    open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))
                                    return
                                results[cwe][file][prompt]["pred"] = pred
                                results[cwe][file][prompt]["reason"] = reason
                            print("信息提取完成!!")

                            # 检查 reason 是否为 n/a
                            if results[cwe][file][prompt]["reason"] == "n/a":
                                results[cwe][file][prompt]["rouge"] = None
                                results[cwe][file][prompt]["cos_sim"] = None
                                results[cwe][file][prompt]["gpt_eval"] = None

                            # 使用真实值进行评估
                            gt = open(
                                os.path.join(dataset_path, 'ground-truth', cwe.upper(), file.split(".")[0] + ".txt"),
                                "r", encoding='utf-8').read()

                            # 1) 计算 rouge 分数
                            if "rouge" not in results[cwe][file][prompt]:
                                rouge_score = self.rouge(reason=results[cwe][file][prompt]["reason"], ground_truth=gt)
                                results[cwe][file][prompt]["rouge"] = rouge_score
                            print("Rouge 分数计算完成!!")

                            # 2) 计算余弦相似度
                            if "cos_sim" not in results[cwe][file][prompt]:
                                gt_emb = None
                                with open(os.path.join(dataset_path, 'embeddings', cwe.upper(), file.split(".")[0]),
                                          "rb") as f:
                                    gt_emb = pickle.load(f)
                                cos_sim = self.cos_similarity(reason=results[cwe][file][prompt]["reason"],
                                                              ground_truth=gt_emb)
                                if cos_sim is None:
                                    open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))
                                    return
                                results[cwe][file][prompt]["cos_sim"] = cos_sim
                            print("余弦相似度计算完成!!")

                            # 3) 计算 GPT 评估
                            if "gpt_eval" not in results[cwe][file][prompt]:
                                gpt_eval = self.gpt_structured_eval(reason=results[cwe][file][prompt]["reason"],
                                                                    ground_truth=gt)
                                if not gpt_eval:
                                    open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))
                                    return
                                results[cwe][file][prompt]["gpt_eval"] = gpt_eval
                            print("GPT 评估完成!!")
        finally:
            # 保存结果到文件
            open(result_full_path, "w").write(json.dumps(results, indent=4, sort_keys=True))

    def run_all(self, **kwargs):
        '''
        此函数在给定模型上运行所有实验。

        参数：
        ----------
            api_key: OpenAI API 密钥 (str)
            model: 模型名称 (str)

        返回值：
        --------
            None
        '''
        base_url = kwargs['base_url']
        api_key = kwargs['api_key']
        model = kwargs['model']
        dataset_path = os.path.join(os.path.dirname(__file__), '..', 'datasets')

        # 创建 `results` 目录
        result_path = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(result_path, exist_ok=True)

        ### 确定性响应实验
        print("\n#######################################")
        print("确定性响应实验开始！！")
        print("#######################################\n")

        # 创建目录以存储结果
        det_res_result_path = os.path.join(result_path, 'determinism')
        os.makedirs(det_res_result_path, exist_ok=True)
        # 为实验选择的文件
        cwe_files = [("cwe-79", "2.py"), ("cwe-79", "p_2.py"), ("cwe-89", "2.py"), ("cwe-89", "p_2.py")]
        # 在选定的提示语上运行实验
        for prompt in ['promptS1', 'promptS2', 'promptS3', 'promptS4', 'promptS5', 'promptS6']:
            # 在指定的温度上运行
            for temp in [0.2, 0.0]:
                self.run_temp_test(
                    base_url= base_url,
                    api_key=api_key,
                    temp=temp,
                    model=model,
                    k=10,
                    do_reason=True,
                    do_extract=True,
                    cwe_files=cwe_files,
                    prompt=prompt,
                    dataset_path=os.path.join(dataset_path, 'hand-crafted'),
                    result_path=det_res_result_path
                )
        print("\n#######################################")
        print("确定性响应实验完成！！")
        print("#######################################\n")

        # ### 参数范围实验
        # print("\n#######################################")
        # print("参数范围实验开始！！")
        # print("#######################################\n")
        #
        # # 创建目录以存储结果
        # range_param_result_path = os.path.join(result_path, 'range-params')
        # os.makedirs(range_param_result_path, exist_ok=True)
        # # 为实验选择的文件、提示语和温度范围
        # cwe_files = [("cwe-787", "3.c"), ("cwe-787", "p_3.c"), ("cwe-89", "3.py"), ("cwe-89", "p_3.py")]
        # prompt = 'promptS4'
        # temps = [0.2, 0.0, 0.25, 0.5, 0.75, 1.0]
        # for temp in temps:
        #     self.run_temp_test(
        #         api_key=api_key,
        #         temp=temp,
        #         model=model,
        #         k=10,
        #         do_reason=True,
        #         do_extract=True,
        #         cwe_files=cwe_files,
        #         prompt=prompt,
        #         dataset_path=os.path.join(dataset_path, 'hand-crafted'),
        #         result_path=range_param_result_path
        #     )
        # print("\n#######################################")
        # print("参数范围实验完成！！")
        # print("#######################################\n")
        #
        # ### 提示语实验
        # print("\n#######################################")
        # print("提示语实验开始！！")
        # print("#######################################\n")
        #
        # # 创建目录以存储结果
        # prompts_result_path = os.path.join(result_path, 'prompts')
        # os.makedirs(prompts_result_path, exist_ok=True)
        # # 在所有提示语上运行实验
        # self.run_prompts_experiments(
        #     api_key=api_key,
        #     temp=0.0,
        #     model=model,
        #     dataset_path=os.path.join(dataset_path, 'hand-crafted'),
        #     result_path=prompts_result_path
        # )
        # print("\n#######################################")
        # print("提示语实验完成！！")
        # print("#######################################\n")
        #
        # # 计算最佳提示语
        # best_prompts_path = os.path.join(result_path, 'best_prompts.json')
        # if not os.path.isfile(best_prompts_path):
        #     best_prompts_loaded = {}
        # else:
        #     best_prompts_loaded = json.loads(open(best_prompts_path, "r", encoding='utf-8').read())
        # best_prompts_loaded[model] = self.find_best_prompts(result_path=prompts_result_path, model=model)
        # open(os.path.join(result_path, 'best_prompts.json'), "w").write(
        #     json.dumps(best_prompts_loaded, indent=4, sort_keys=True))



