import math
from collections import defaultdict
from functools import lru_cache

import MeCab

from setting import DIC_DIR
from word import Sentence, Word


class Corpus:
    def __init__(self, sentences: list[Sentence]) -> None:
        """コーパスを初期化する

        Parameters
        ----------
        - sentences: `文の単語リスト` のリスト
        """
        sentences = [sentence.removed_symbol for sentence in sentences]
        line_consonants = [[mora.consonant for word in words for mora in word.moras] for words in sentences]
        self.n_pq: defaultdict[tuple[str, str], int] = defaultdict(int)
        for cons in line_consonants:
            for i in range(len(cons)):
                p = cons[i]
                for j in range(i + 1, len(cons)):
                    q = cons[j]
                    self.n_pq[(p, q)] += 1
        self.n_pair = sum(self.n_pq.values())

    @lru_cache(maxsize=None)
    def p(self, p: str):
        """子音ペアのうち、pが含まれるものの割合を計算する

        Parameters
        ----------
        - p: 子音
        """
        return len(list(filter(lambda x: p in x, self.n_pq.keys()))) / self.n_pair

    @lru_cache(maxsize=None)
    def calc_oer(self, p: str, q: str):
        """O/E比を計算する

        Parameters
        ----------
        - p: 子音（p, qは順不同）
        - q: 子音（p, qは順不同）
        """
        # p==qの場合は計算しない
        if p == q:
            return 0
        constant = 0
        oer = (self.n_pq[(p, q)] + self.n_pq[(q, p)]) / (self.n_pair * self.p(p) * self.p(q))
        if oer == 0:
            return constant
        else:
            return math.log(oer) + constant

    def calc_score(self, sentence: str | Sentence):
        """子音の音韻類似度スコアを計算する

        Parameters
        ----------
        - sentence: `文の単語リスト` または `一文の文字列`
        """
        score = 0.0
        if isinstance(sentence, str):
            tagger = MeCab.Tagger(f"-Ochasen -d {DIC_DIR}")
            results: list[str] = tagger.parse(sentence).splitlines()
            sentence1 = Sentence([Word(res_word) for res_word in results if res_word != "EOS"])
        else:
            sentence1 = sentence

        sentence1 = sentence1.removed_symbol  # 記号を除外
        consonant_seq = [mora.consonant for word in sentence1 for mora in word.moras]
        consonant_cnt = 0
        for word in sentence1:
            consonant_cnt += len(word.moras)
            if not word.is_content_word:
                continue
            for j in range(consonant_cnt, len(consonant_seq) - len(word.moras)):
                for k in range(len(word.moras)):
                    score += self.calc_oer(word.moras[k].consonant, consonant_seq[j + k])
        return score

    def calc_max_score(self, sentence: str | Sentence):
        """子音の音韻類似度スコアを計算する（最大値を返す）

        Parameters
        ----------
        - sentence: `文の単語リスト` または `一文の文字列`
        """
        score = 0.0
        if isinstance(sentence, str):
            tagger = MeCab.Tagger(f"-Ochasen -d {DIC_DIR}")
            results: list[str] = tagger.parse(input).splitlines()
            sentence1 = Sentence([Word(res_word) for res_word in results if res_word != "EOS"])
        else:
            sentence1 = sentence

        sentence1 = sentence1.removed_symbol  # 記号を除外
        consonant_seq = [mora.consonant for word in sentence1 for mora in word.moras]
        consonant_cnt = 0
        for i, word in enumerate(sentence1):
            consonant_cnt += len(word.moras)
            if not word.is_content_word:
                continue
            for j in range(consonant_cnt, len(consonant_seq) - len(word.moras)):
                tmp_s = 0.0
                for k in range(len(word.moras)):
                    tmp_s += self.calc_oer(word.moras[k].consonant, consonant_seq[j + k])
                score = max(score, tmp_s / sentence1.char_len)
        return score
