通过一些艰苦卓绝的奋斗..这是目前的代码大纲，接下来跑数据就行了，基本没啥事了。

现在加进去的是两个实验（详情参见experiment_cn.py)

一个是每种prompt和cwe还有参数的组合做十次，如果十次都是一个效果就说明accuracy没问题

一个是每个prompt模板和cwe做一遍，看哪个最好

数据集在/datasets文件夹：

有些prompt模板是few-shot的，所以few-shot文件夹下是每个cwe的一个样例及其补丁。
hand-crafted都是我手动搞的，每个cwe都有3个scenario，每个scenario各有一个对应的补丁。
ground-truth是手动写的每个scenario和对应补丁的100字以内的说明（以便检验llm结果）。embeddings是ground-truth里对应的嵌入向量（生成嵌入向量的函数在save.py，有需要的可以自己再跑）

检验方式：rouge、余弦相似度、gpt-4判断的结果。这三个一起投票表决，两个及以上认为和正确答案相似即认定为相似。

prompt设置：参见论文：LLMsCannot Reliably Identify and Reason About Security Vulnerabilities (Yet?): AComprehensive Evaluation, Framework, and Benchmarks