# -*- coding: utf-8 -*-
"""
论文查重程序
功能：对比原文与抄袭版论文，计算重复率并输出到指定文件。
用法：python main.py [原文文件路径] [抄袭版论文路径] [输出答案文件路径]
"""

import sys
import re
import math
from collections import Counter

# 尝试导入 jieba 分词库；若未安装则降级为字符级分词
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False


# ============================================================
# 异常类定义
# ============================================================
class PlagiarismError(Exception):
    """查重模块基础异常类"""
    pass


class FileReadError(PlagiarismError):
    """文件读取异常"""
    pass


class FileWriteError(PlagiarismError):
    """文件写入异常"""
    pass


class ArgumentError(PlagiarismError):
    """命令行参数异常"""
    pass


class EmptyContentError(PlagiarismError):
    """文件内容为空异常"""
    pass


# ============================================================
# 文本预处理模块
# ============================================================
def preprocess(text):
    """
    文本预处理：去除标点符号、多余空白，统一为小写。

    参数:
        text (str): 原始文本
    返回:
        str: 预处理后的文本
    """
    if not isinstance(text, str):
        raise TypeError("text 必须为字符串类型")

    # 去除常见中英文标点符号
    # 字符类中 ] 放在首位、- 放在末位即可免转义，其余元字符在 [] 内无需转义
    punctuation = r"""[][，。！？、；：""''（）【】《》—…·,!?;:'"(){}<>~. -]"""
    text = re.sub(punctuation, ' ', text)

    # 统一为小写（对英文有效）
    text = text.lower()

    # 将多个连续空白替换为单个空格
    text = re.sub(r'\s+', ' ', text)

    # 去除首尾空白
    text = text.strip()

    return text


# ============================================================
# 分词模块
# ============================================================
def tokenize(text):
    """
    对文本进行分词。优先使用 jieba 精确模式，
    若 jieba 不可用则降级为字符级分词（按单个汉字/英文单词切分）。

    参数:
        text (str): 预处理后的文本
    返回:
        list: 分词结果列表
    """
    if not text:
        return []

    if JIEBA_AVAILABLE:
        # 使用 jieba 精确模式分词
        tokens = list(jieba.cut(text, cut_all=False))
        # 过滤掉空白词
        tokens = [t.strip() for t in tokens if t.strip()]
    else:
        # 降级方案：英文按单词、中文按单字切分
        tokens = []
        for word in text.split():
            if re.match(r'^[a-zA-Z0-9]+$', word):
                tokens.append(word)
            else:
                tokens.extend(list(word))

    return tokens


# ============================================================
# 词频向量与相似度计算模块
# ============================================================
def build_tf_vector(tokens):
    """
    构建词频向量（Term Frequency）。

    参数:
        tokens (list): 分词结果列表
    返回:
        Counter: 词频字典（词 -> 出现次数）
    """
    return Counter(tokens)


def cosine_similarity(vec1, vec2):
    """
    计算两个词频向量的余弦相似度。

    参数:
        vec1 (Counter): 第一个文本的词频向量
        vec2 (Counter): 第二个文本的词频向量
    返回:
        float: 余弦相似度，范围 [0, 1]
    """
    if not vec1 or not vec2:
        return 0.0

    # 计算点积
    dot_product = sum(vec1[word] * vec2[word] for word in vec1 if word in vec2)

    # 计算各自的模长
    norm1 = math.sqrt(sum(count ** 2 for count in vec1.values()))
    norm2 = math.sqrt(sum(count ** 2 for count in vec2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def char_ngram(text, n=2):
    """
    生成字符级 n-gram 集合。

    参数:
        text (str): 预处理后的文本
        n (int): n-gram 的 n 值，默认为 2（bigram）
    返回:
        set: n-gram 字符串集合
    """
    # 去除空格后按字符切分
    chars = text.replace(' ', '')
    if len(chars) < n:
        return set(chars)

    ngrams = set()
    for i in range(len(chars) - n + 1):
        ngrams.add(chars[i:i + n])

    return ngrams


def jaccard_similarity(set1, set2):
    """
    计算两个集合的 Jaccard 相似度。

    参数:
        set1 (set): 第一个集合
        set2 (set): 第二个集合
    返回:
        float: Jaccard 相似度，范围 [0, 1]
    """
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    if union == 0:
        return 0.0
    return intersection / union


# ============================================================
# 核心查重模块
# ============================================================
def calculate_similarity(orig_text, plag_text):
    """
    综合计算原文与抄袭版的重复率。
    采用词频余弦相似度 + 字符 bigram Jaccard 相似度的加权平均，
    兼顾词级语义和字符级结构，提高对增删改抄袭的检测能力。

    参数:
        orig_text (str): 原文文本
        plag_text (str): 抄袭版文本
    返回:
        float: 重复率，范围 [0, 1]
    """
    # 文本预处理
    orig_clean = preprocess(orig_text)
    plag_clean = preprocess(plag_text)

    # 空内容检查
    if not orig_clean:
        raise EmptyContentError("原文文件内容为空")
    if not plag_clean:
        raise EmptyContentError("抄袭版文件内容为空")

    # 方法一：词频余弦相似度（权重 0.6）
    orig_tokens = tokenize(orig_clean)
    plag_tokens = tokenize(plag_clean)
    orig_tf = build_tf_vector(orig_tokens)
    plag_tf = build_tf_vector(plag_tokens)
    word_sim = cosine_similarity(orig_tf, plag_tf)

    # 方法二：字符 bigram Jaccard 相似度（权重 0.4）
    orig_ngrams = char_ngram(orig_clean, n=2)
    plag_ngrams = char_ngram(plag_clean, n=2)
    ngram_sim = jaccard_similarity(orig_ngrams, plag_ngrams)

    # 加权综合
    final_sim = 0.6 * word_sim + 0.4 * ngram_sim

    # 确保结果在 [0, 1] 范围内
    final_sim = max(0.0, min(1.0, final_sim))

    return final_sim


# ============================================================
# 文件读写模块
# ============================================================
def read_file(file_path):
    """
    读取文本文件内容，尝试多种编码方式。

    参数:
        file_path (str): 文件绝对路径
    返回:
        str: 文件内容
    异常:
        FileReadError: 文件不存在或读取失败
    """
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            raise FileReadError(f"文件不存在: {file_path}")
        except PermissionError:
            raise FileReadError(f"没有权限读取文件: {file_path}")
        except OSError as e:
            raise FileReadError(f"读取文件失败: {file_path}, 错误: {e}")

    raise FileReadError(f"无法识别文件编码: {file_path}")


def write_result(file_path, similarity):
    """
    将重复率写入答案文件，保留两位小数。

    参数:
        file_path (str): 输出文件绝对路径
        similarity (float): 重复率
    异常:
        FileWriteError: 文件写入失败
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"{similarity:.2f}")
    except PermissionError:
        raise FileWriteError(f"没有权限写入文件: {file_path}")
    except OSError as e:
        raise FileWriteError(f"写入文件失败: {file_path}, 错误: {e}")


# ============================================================
# 主函数
# ============================================================
def main():
    """
    主函数：解析命令行参数，执行查重，输出结果。
    命令行格式：python main.py [原文文件] [抄袭版文件] [答案文件]
    """
    # 检查命令行参数数量
    if len(sys.argv) != 4:
        print("用法: python main.py [原文文件路径] [抄袭版论文路径] [输出答案文件路径]")
        print(f"当前参数数量: {len(sys.argv) - 1}，需要 3 个参数")
        sys.exit(1)

    orig_path = sys.argv[1]
    plag_path = sys.argv[2]
    output_path = sys.argv[3]

    try:
        # 读取文件
        orig_text = read_file(orig_path)
        plag_text = read_file(plag_path)

        # 计算重复率
        similarity = calculate_similarity(orig_text, plag_text)

        # 写入结果
        write_result(output_path, similarity)

        # 控制台输出（便于调试，不影响文件结果）
        print(f"原文文件: {orig_path}")
        print(f"抄袭版文件: {plag_path}")
        print(f"重复率: {similarity:.2f}")
        print(f"结果已写入: {output_path}")

    except ArgumentError as e:
        print(f"[参数错误] {e}")
        sys.exit(1)
    except FileReadError as e:
        print(f"[文件读取错误] {e}")
        sys.exit(1)
    except FileWriteError as e:
        print(f"[文件写入错误] {e}")
        sys.exit(1)
    except EmptyContentError as e:
        print(f"[内容错误] {e}")
        sys.exit(1)
    except PlagiarismError as e:
        print(f"[查重错误] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[未知错误] {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
