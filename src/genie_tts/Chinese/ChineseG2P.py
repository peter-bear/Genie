# -*- coding: utf-8 -*-
"""
用于中文（普通话）的 G2P。
需要安装: pip install pypinyin
"""

import re
from typing import List, Tuple
from pypinyin import pinyin, Style

# 导入你的 SymbolsV2 配置
from ..Japanese.SymbolsV2 import symbols_v2, symbol_to_id_v2, PINYIN_INITIALS

# 匹配连续的标点符号
_CONSECUTIVE_PUNCTUATION_RE = re.compile(r"([,./?!~…・])\1+")

# 匹配需要转换为中文读法的特殊符号
_SYMBOLS_TO_CHINESE = [
    (re.compile("%"), "百分之"),
    (re.compile("％"), "百分之"),
]

# 匹配中文字符（汉字）
_CHINESE_CHARACTERS_RE = re.compile(r"[\u4e00-\u9fa5]+")

# 匹配非中文字符（标点、空格、字母数字等），用于分割片段
# 我们排除掉汉字，剩下的都视为分隔符
_CHINESE_MARKS_RE = re.compile(r"[^\u4e00-\u9fa5]+")


class ChineseG2P:
    """
    一个简化的、封装好的中文 G2P 转换器。
    
    结构严格参照 JapaneseG2P。
    使用 pypinyin 将汉字转换为 [声母, 韵母] 序列。
    """

    # 预先处理声母列表，按长度倒序排列，用于准确切分拼音
    _initials_sorted = sorted(PINYIN_INITIALS, key=len, reverse=True)

    @staticmethod
    def _text_normalize(text: str) -> str:
        """对输入文本进行基础的规范化处理。"""
        for regex, replacement in _SYMBOLS_TO_CHINESE:
            text = re.sub(regex, replacement, text)
        
        text = _CONSECUTIVE_PUNCTUATION_RE.sub(r"\1", text)
        text = text.strip()
        return text

    @staticmethod
    def _post_replace_phoneme(ph: str) -> str:
        """对单个音素或标点进行后处理替换。"""
        rep_map = {
            "：": ",", "；": ",", "，": ",", "。": ".",
            "！": "!", "？": "?", "\n": ".", "·": ",",
            "、": ",", "...": "…", "—": "-", "“": "'", "”": "'",
            "‘": "'", "’": "'"
        }
        return rep_map.get(ph, ph)

    @staticmethod
    def _split_pinyin_to_initial_final(py_text: str) -> List[str]:
        """
        核心逻辑：将带声调的拼音（如 zhuang4）切分为声母和韵母。
        并处理 SymbolsV2 特有的 i -> i0 规则。
        """
        # 1. 尝试匹配声母
        initial = ""
        rest = py_text
        
        for init in ChineseG2P._initials_sorted:
            if py_text.startswith(init):
                initial = init
                rest = py_text[len(init):]
                break
        
        # 2. 剩下的部分就是韵母
        final = rest

        # 3. 特殊规则处理: 整体认读音节 (zhi, chi, shi, ri, zi, ci, si)
        # 如果韵母以 i 开头（如 i1, i4），且声母是上述之一，则将 i 改为 i0
        if final.startswith("i") and len(final) > 1:
            if initial in ["z", "c", "s", "zh", "ch", "sh", "r"]:
                final = final.replace("i", "i0", 1)

        result = []
        if initial:
            result.append(initial)
        if final:
            result.append(final)
            
        return result

    @staticmethod
    def _pypinyin_g2p(segment: str) -> List[str]:
        """使用 pypinyin 提取音素 (替代 _pyopenjtalk_g2p_prosody)。"""
        # style=Style.TONE3: 生成带数字的拼音 (ni3)
        # 移除了 neutral_tone_with_5 参数以防止报错
        pinyin_list = pinyin(
            segment, 
            style=Style.TONE3, 
            errors='default'
        )
        
        phones = []
        for item in pinyin_list:
            # pypinyin 返回的是 [[p1], [p2]] 结构
            original_pinyin = item[0]
            
            # 手动处理轻声：如果拼音全是字母且没有数字结尾（例如 "ma"），手动加上 "5"
            # 这样就能达到 neutral_tone_with_5=True 的效果
            if original_pinyin.isalpha():
                original_pinyin += "5"
            
            # 拆分声韵母
            split_phones = ChineseG2P._split_pinyin_to_initial_final(original_pinyin)
            phones.extend(split_phones)
            
        return phones

    @staticmethod
    def g2p(text: str) -> List[str]:
        """
        将中文文本转换为音素序列。

        Args:
            text (str): 待转换的中文文本。

        Returns:
            List[str]: 音素和符号的列表。
        """
        if not text.strip():
            return []

        # 1. 文本规范化
        norm_text = ChineseG2P._text_normalize(text)

        # 2. 使用标点符号分割字符串，得到纯中文文本片段
        # 例如: "你好，世界" -> segments=['你好', '世界'], marks=[',']
        chinese_segments = _CHINESE_MARKS_RE.split(norm_text)
        punctuation_marks = _CHINESE_MARKS_RE.findall(norm_text)

        phonemes = []
        for i, segment in enumerate(chinese_segments):
            if segment:
                # 对纯汉字片段进行转换
                phones = ChineseG2P._pypinyin_g2p(segment)
                phonemes.extend(phones)

            # 将对应的标点符号添加回来
            if i < len(punctuation_marks):
                mark = punctuation_marks[i].strip()
                if mark:
                    # 可以在这里处理长标点，比如把 "..." 变成 "…"
                    phonemes.append(mark)

        # 3. 对最终列表中的每个元素进行后处理（主要转换全角标点）
        processed_phonemes = [ChineseG2P._post_replace_phoneme(p) for p in phonemes]

        return processed_phonemes


def chinese_to_phones(text: str) -> list[int]:
    phones = ChineseG2P.g2p(text)
    # 过滤掉不在符号表里的未知符号，转为 UNK
    phones = ["UNK" if ph not in symbols_v2 else ph for ph in phones]
    phones = [symbol_to_id_v2[ph] for ph in phones]
    return phones