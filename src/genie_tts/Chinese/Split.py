import re
import logging

logger = logging.getLogger(__name__)

# 如果句子有效长度小于这个数，会尝试合并到上一句
MIN_SENTENCE_LENGTH = 5

# 定义用于分割句子的标点
# 增加了中文常见的：分号；
SENTENCE_TERMINATORS = "。！？…；!?"

# 定义有效字符的正则表达式
# 这里的范围是：汉字 + 字母 + 数字
VALID_CHAR_PATTERN = re.compile(
    r'[\u4e00-\u9fa5'              # 常用汉字范围
    r'a-zA-Z'                      # 半角字母
    r'\uFF21-\uFF3A\uFF41-\uFF5A'  # 全角字母 (A-Z, a-z)
    r'0-9'                         # 半角数字
    r'\uFF10-\uFF19'               # 全角数字
    r']'
)


def get_valid_text_length(sentence: str) -> int:
    """计算字符串中有效字符（汉字/字母/数字）的数量"""
    return len(VALID_CHAR_PATTERN.findall(sentence))


def split_chinese_text(long_text: str) -> list[str]:
    """
    将长文本分割成短句列表。
    如果分割后的句子太短，会自动合并到前一句。
    """
    if not long_text:
        return []
    
    # 1. 使用正向后行断言 (?<=...) 保留分隔符
    # 这里的逻辑是：只要遇到 SENTENCE_TERMINATORS 里的符号，就切一刀
    raw_sentences = re.split(f'(?<=[{SENTENCE_TERMINATORS}])', long_text)
    
    # 去除首尾空格，并过滤掉空字符串
    raw_sentences = [s.strip() for s in raw_sentences if s.strip()]

    if not raw_sentences:
        # 如果处理后什么都不剩（比如全是空格），如果有原文本则返回原文本，否则空列表
        return [long_text] if long_text.strip() else []

    final_sentences = []
    for sentence in raw_sentences:
        clean_len = get_valid_text_length(sentence)
        
        # 逻辑：
        # 如果 final_sentences 列表里已经有句子了，
        # 并且 当前这句句子的有效长度 < 最小长度 (5)，
        # 那么就不要让它单独存在，把它“粘”到上一句的后面。
        if final_sentences and clean_len < MIN_SENTENCE_LENGTH:
            final_sentences[-1] += sentence
        else:
            final_sentences.append(sentence)
            
    return final_sentences

# --- 测试代码 ---
if __name__ == "__main__":
    text = "你好。这是一个测试文本！它应该被分割。太短了...不分。这就对了。"
    print(split_chinese_text(text))
    # 预期输出: ['你好。', '这是一个测试文本！', '它应该被分割。', '太短了...不分。这就对了。']