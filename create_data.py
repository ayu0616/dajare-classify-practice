# 学習用データを作成するためのプログラム

import os
import re

import MeCab
import pandas as pd

from setting import DIC_DIR

RAW_DATA_DIR = "./raw_data"  # 元データのディレクトリ
OUTPUT_DIR = "./data"  # 出力先のディレクトリ
EOS = "EOS"
MIN_LEN = 5  # 最小の文章の長さ

full = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ（）｛｝＜＞！？"  # 全角
half = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz(){}<>!?"  # 半角
full_to_half_trans = str.maketrans(full, half)  # 全角→半角変換用


with open(os.path.join(RAW_DATA_DIR, "dajare.txt"), "r") as f:
    dajare_sentences = f.read().splitlines()

with open(os.path.join(RAW_DATA_DIR, "conversation.txt"), "r") as f:
    normal_sentences = f.read().splitlines()


def preprocess(s: str):
    """下処理をする"""
    s = s.translate(full_to_half_trans)  # 全角→半角変換
    s = re.sub(r"\s", "", s)  # 空白を削除
    s = re.sub(r"\(.*\)", "", s)  # 括弧内を削除
    s = re.sub(r"\{.*\}", "", s)  # 波括弧内を削除
    s = re.sub(r"\<.*\>", "", s)  # 尖括弧内を削除
    return s


def is_valid_data(s: str):
    """データとして使える文章かどうか確認する（固有名詞が伏せられているなど）"""
    f = True
    f &= "＊" not in s
    f &= re.match(r"\W*[A-Z]\W*", s) is None
    f &= re.match(r"\W*[A-Z][0-9]{3}\W*", s) is None
    # f &= len(s) >= MIN_LEN
    return f


dajare_sentences = [preprocess(s) for s in dajare_sentences]
dajare_sentences = [s for s in dajare_sentences if is_valid_data(s)]
dajare_sentences = list(set(dajare_sentences))  # 重複を削除
normal_sentences = [preprocess(s) for s in normal_sentences]
normal_sentences = [s for s in normal_sentences if is_valid_data(s)]
normal_sentences = list(set(normal_sentences))  # 重複を削除

tagger = MeCab.Tagger(f"-Ochasen -d {DIC_DIR}")
tagged_dajare = tagger.parse("\n".join(dajare_sentences))
tagged_normal = tagger.parse("\n".join(normal_sentences))

with open(os.path.join(OUTPUT_DIR, "dajare.txt"), "w") as f:
    f.write(tagged_dajare)

with open(os.path.join(OUTPUT_DIR, "conversation.txt"), "w") as f:
    f.write(tagged_normal)
