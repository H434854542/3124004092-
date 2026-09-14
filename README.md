# 论文查重项目

软件工程课程个人项目——基于 Python 的论文查重程序。

## 功能说明

对比原文与抄袭版论文，计算重复率（0.00 ~ 1.00），结果保留两位小数并写入指定文件。

## 项目结构

```
学号/
├── main.py              # 主程序入口
├── requirements.txt     # 依赖文件
├── test_plagiarism.py   # 单元测试（23个用例）
├── PSP表格.md           # PSP 耗时记录
├── 博客文档.md           # 博客正文
└── README.md            # 本文件
```

## 环境要求

- Python 3.8+
- 依赖库：jieba >= 0.42.1

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行方式

```bash
python main.py [原文文件绝对路径] [抄袭版论文绝对路径] [输出答案文件绝对路径]
```

示例：
```bash
python main.py C:\tests\orig.txt C:\tests\orig_add.txt C:\tests\ans.txt
```

## 运行单元测试

```bash
python -m unittest test_plagiarism.py -v
```

## 算法说明

采用双算法加权融合：
- **词频余弦相似度**（权重 0.6）：基于 jieba 分词，识别语义层面抄袭
- **字符 bigram Jaccard 相似度**（权重 0.4）：基于字符 n-gram，识别字符级增删改

最终重复率 = 0.6 × 余弦相似度 + 0.4 × Jaccard 相似度

## 性能指标

- 小文本（< 1000字）：< 1 秒
- 内存占用：< 100 MB
- 满足 5 秒 / 2048 MB 约束
