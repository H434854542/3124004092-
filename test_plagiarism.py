# -*- coding: utf-8 -*-
"""
论文查重程序单元测试
使用 Python 内置 unittest 框架，无需额外安装依赖。
运行方式：python -m unittest test_plagiarism.py -v
"""

import unittest
import os
import sys
import tempfile

# 将当前目录加入路径，以便导入 main 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as plag


class TestPreprocess(unittest.TestCase):
    """测试文本预处理模块"""

    def test_remove_punctuation(self):
        """测试用例1：去除中英文标点符号"""
        text = "你好，世界！Hello, World."
        result = plag.preprocess(text)
        self.assertNotIn("，", result)
        self.assertNotIn("！", result)
        self.assertNotIn(",", result)
        self.assertNotIn(".", result)

    def test_lowercase(self):
        """测试用例2：英文字母统一转为小写"""
        text = "HELLO World"
        result = plag.preprocess(text)
        self.assertEqual(result, "hello world")

    def test_multiple_spaces(self):
        """测试用例3：多个连续空白合并为单个空格"""
        text = "hello    world   foo"
        result = plag.preprocess(text)
        self.assertEqual(result, "hello world foo")

    def test_empty_string(self):
        """测试用例4：空字符串预处理"""
        result = plag.preprocess("")
        self.assertEqual(result, "")

    def test_only_punctuation(self):
        """测试用例5：仅含标点符号的文本"""
        text = "，。！？、"
        result = plag.preprocess(text)
        self.assertEqual(result, "")


class TestTokenize(unittest.TestCase):
    """测试分词模块"""

    def test_chinese_tokenize(self):
        """测试用例6：中文分词基本功能"""
        text = "今天天气很好"
        tokens = plag.tokenize(text)
        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)

    def test_empty_tokenize(self):
        """测试用例7：空文本分词返回空列表"""
        tokens = plag.tokenize("")
        self.assertEqual(tokens, [])

    def test_english_tokenize(self):
        """测试用例8：英文文本分词"""
        text = "hello world"
        tokens = plag.tokenize(text)
        self.assertIn("hello", tokens)
        self.assertIn("world", tokens)


class TestSimilarity(unittest.TestCase):
    """测试相似度计算模块"""

    def test_identical_texts(self):
        """测试用例9：完全相同的文本，重复率应为1.0"""
        text = "今天是星期天，天气晴，今天晚上我要去看电影。"
        sim = plag.calculate_similarity(text, text)
        self.assertAlmostEqual(sim, 1.0, places=1)

    def test_completely_different(self):
        """测试用例10：完全不同的文本，重复率应较低"""
        text1 = "人工智能是计算机科学的一个分支，它企图了解智能的实质。"
        text2 = "篮球比赛每队上场五人，比赛时间四节，每节十二分钟。"
        sim = plag.calculate_similarity(text1, text2)
        self.assertLess(sim, 0.3)

    def test_example_plagiarism(self):
        """测试用例11：题目示例——增删改后的抄袭文本应检测出较高重复率"""
        orig = "今天是星期天，天气晴，今天晚上我要去看电影。"
        plag_text = "今天是周日，天气晴朗，我晚上要去看电影。"
        sim = plag.calculate_similarity(orig, plag_text)
        self.assertGreater(sim, 0.5)

    def test_partial_overlap(self):
        """测试用例12：部分重复的文本"""
        text1 = "机器学习是人工智能的核心，包括监督学习和无监督学习。"
        text2 = "机器学习是人工智能的核心，深度学习是其中的热门方向。"
        sim = plag.calculate_similarity(text1, text2)
        self.assertGreater(sim, 0.4)
        self.assertLess(sim, 0.95)

    def test_empty_original(self):
        """测试用例13：原文为空应抛出异常"""
        with self.assertRaises(plag.EmptyContentError):
            plag.calculate_similarity("", "测试文本")

    def test_empty_plagiarized(self):
        """测试用例14：抄袭版为空应抛出异常"""
        with self.assertRaises(plag.EmptyContentError):
            plag.calculate_similarity("测试文本", "")


class TestCosineSimilarity(unittest.TestCase):
    """测试余弦相似度"""

    def test_identical_vectors(self):
        """测试用例15：相同向量余弦相似度为1"""
        from collections import Counter
        vec = Counter({"a": 2, "b": 3})
        sim = plag.cosine_similarity(vec, vec)
        self.assertAlmostEqual(sim, 1.0)

    def test_orthogonal_vectors(self):
        """测试用例16：正交向量余弦相似度为0"""
        from collections import Counter
        vec1 = Counter({"a": 1})
        vec2 = Counter({"b": 1})
        sim = plag.cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(sim, 0.0)

    def test_empty_vector(self):
        """测试用例17：空向量返回0"""
        from collections import Counter
        sim = plag.cosine_similarity(Counter(), Counter({"a": 1}))
        self.assertEqual(sim, 0.0)


class TestFileOperations(unittest.TestCase):
    """测试文件读写模块"""

    def setUp(self):
        """创建临时目录"""
        self.tmpdir = tempfile.mkdtemp()

    def test_write_and_read(self):
        """测试用例18：写入结果后读取验证"""
        output_path = os.path.join(self.tmpdir, "ans.txt")
        plag.write_result(output_path, 0.8567)
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, "0.86")

    def test_read_nonexistent_file(self):
        """测试用例19：读取不存在的文件应抛出异常"""
        with self.assertRaises(plag.FileReadError):
            plag.read_file("/nonexistent/path/file.txt")

    def test_read_write_roundtrip(self):
        """测试用例20：文件读写往返测试"""
        orig_path = os.path.join(self.tmpdir, "orig.txt")
        plag_path = os.path.join(self.tmpdir, "plag.txt")
        output_path = os.path.join(self.tmpdir, "ans.txt")

        orig_text = "今天是星期天，天气晴，今天晚上我要去看电影。"
        plag_text = "今天是周日，天气晴朗，我晚上要去看电影。"

        with open(orig_path, 'w', encoding='utf-8') as f:
            f.write(orig_text)
        with open(plag_path, 'w', encoding='utf-8') as f:
            f.write(plag_text)

        orig_content = plag.read_file(orig_path)
        plag_content = plag.read_file(plag_path)
        self.assertEqual(orig_content, orig_text)
        self.assertEqual(plag_content, plag_text)

        sim = plag.calculate_similarity(orig_content, plag_content)
        plag.write_result(output_path, sim)

        with open(output_path, 'r', encoding='utf-8') as f:
            result = f.read()
        self.assertEqual(result, f"{sim:.2f}")


class TestNGram(unittest.TestCase):
    """测试 n-gram 模块"""

    def test_bigram_generation(self):
        """测试用例21：字符 bigram 生成"""
        text = "abcdef"
        ngrams = plag.char_ngram(text, n=2)
        self.assertIn("ab", ngrams)
        self.assertIn("bc", ngrams)
        self.assertIn("ef", ngrams)
        self.assertEqual(len(ngrams), 5)

    def test_jaccard_identical(self):
        """测试用例22：相同集合 Jaccard 相似度为1"""
        s = {"a", "b", "c"}
        sim = plag.jaccard_similarity(s, s)
        self.assertEqual(sim, 1.0)

    def test_jaccard_disjoint(self):
        """测试用例23：不相交集合 Jaccard 相似度为0"""
        s1 = {"a", "b"}
        s2 = {"c", "d"}
        sim = plag.jaccard_similarity(s1, s2)
        self.assertEqual(sim, 0.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
