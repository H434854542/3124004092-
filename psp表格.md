# PSP 表格 —— 论文查重项目

## 一、PSP 2.1 阶段耗时记录

| PSP2.1 | Personal Software Process Stages | 预估耗时（分钟） | 实际耗时（分钟） |
|--------|-----------------------------------|-----------------|-----------------|
| **Planning** | **计划** | **30** | **25** |
| · Estimate | · 估计这个任务需要多少时间 | 30 | 25 |
| **Development** | **开发** | **300** | **280** |
| · Analysis | · 需求分析（包括学习新技术） | 40 | 35 |
| · Design Spec | · 生成设计文档 | 30 | 25 |
| · Design Review | · 设计复审 | 15 | 10 |
| · Coding Standard | · 代码规范（为目前的开发制定合适的规范） | 15 | 10 |
| · Design | · 具体设计 | 30 | 35 |
| · Coding | · 具体编码 | 90 | 80 |
| · Code Review | · 代码复审 | 30 | 25 |
| · Test | · 测试（自我测试，修改代码，提交修改） | 50 | 60 |
| **Reporting** | **报告** | **120** | **100** |
| · Test Report | · 测试报告 | 30 | 25 |
| · Size Measurement | · 计算工作量 | 15 | 10 |
| · Postmortem & Process Improvement Plan | · 事后总结，并提出过程改进计划 | 75 | 65 |
| **合计** | | **450** | **405** |

---

## 二、各阶段说明

### 1. Planning（计划）
- 阅读作业要求，明确论文查重的功能需求和性能约束
- 评估技术选型（Python + jieba 分词）
- 预估各模块开发时间

### 2. Development（开发）

#### 2.1 Analysis（需求分析）
- 输入：原文文件路径、抄袭版文件路径、输出文件路径（命令行参数）
- 输出：重复率（浮点数，保留两位小数，写入答案文件）
- 约束：5秒内完成、内存不超过2048MB、无异常退出
- 学习：jieba 分词库使用、余弦相似度算法、n-gram 算法

#### 2.2 Design Spec（设计文档）
- 模块划分：预处理模块、分词模块、相似度计算模块、文件读写模块、主函数
- 算法选型：词频余弦相似度（权重0.6）+ 字符 bigram Jaccard 相似度（权重0.4）

#### 2.3 Design Review（设计复审）
- 检查模块间接口是否清晰
- 确认算法能覆盖增删改等抄袭场景
- 评估性能是否满足5秒约束

#### 2.4 Coding Standard（代码规范）
- 遵循 PEP 8 编码规范
- 函数名使用 snake_case，类名使用 PascalCase
- 每个函数添加 docstring 说明功能、参数、返回值
- 关键逻辑添加行内注释

#### 2.5 Design（具体设计）
- 异常类层次：PlagiarismError → FileReadError / FileWriteError / ArgumentError / EmptyContentError
- 核心函数：preprocess()、tokenize()、build_tf_vector()、cosine_similarity()、char_ngram()、jaccard_similarity()、calculate_similarity()
- 流程图：
  ```
  读取命令行参数 → 读取原文/抄袭版文件 → 文本预处理 → 分词/向量化
       → 计算余弦相似度 + n-gram相似度 → 加权融合 → 写入答案文件
  ```

#### 2.6 Coding（具体编码）
- 实现 main.py 全部功能
- 实现 test_plagiarism.py 单元测试（23个用例）
- 编写 requirements.txt

#### 2.7 Code Review（代码复审）
- 检查代码可读性和命名规范
- 修复正则表达式 SyntaxWarning
- 确认所有异常都有妥善处理

#### 2.8 Test（测试）
- 运行23个单元测试用例，全部通过
- 用题目示例验证端到端功能
- 性能测试：小文本 < 1秒，满足5秒约束

### 3. Reporting（报告）

#### 3.1 Test Report（测试报告）
- 单元测试：23个用例全部通过
- 覆盖模块：预处理、分词、余弦相似度、n-gram、文件读写、异常处理
- 端到端测试：题目示例输出 0.52，符合预期

#### 3.2 Size Measurement（计算工作量）
- main.py：约 350 行代码（含注释和空行）
- test_plagiarism.py：约 250 行代码
- 总代码量：约 600 行

#### 3.3 Postmortem & Process Improvement Plan（事后总结）
**做得好的地方：**
- 模块划分清晰，各功能职责单一
- 单元测试覆盖全面，23个用例远超要求的10个
- 异常处理完善，定义了完整的异常类层次
- 代码无警告，符合 Code Quality Analysis 要求

**改进方向：**
- 可进一步优化大文本性能（如使用 SimHash 算法）
- 可增加停用词过滤，提高查重准确性
- 可添加命令行参数校验的更详细提示
- 下次项目可更早开始编写单元测试，采用 TDD 方式
