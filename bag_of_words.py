from collections import defaultdict

import numpy as np
from numpy.typing import NDArray

from word import Sentence, Word


class BagOfWords:
    def __init__(self) -> None:
        self.word_set: set[str] = set()
        self.word_count: defaultdict[str, int] = defaultdict(int)

    def add(self, word: Word) -> None:
        """入力された文章をBOWに追加する

        Parameters
        ----------
        - word: 単語
        """
        if word.is_content_word:
            self.word_set.add(word.base_form)
            self.word_count[word.base_form] += 1

    def assign_id(self, min_cnt: int = 1) -> None:
        """単語にIDを割り振る

        Parameters
        ----------
        - min_cnt: 出現回数がmin_cnt未満の単語は削除する
        """
        self.word_to_id: dict[str, int] = {}
        self.id_to_word: dict[int, str] = {}
        for i, word in enumerate(self.word_set):
            if self.word_count[word] < min_cnt:
                continue
            self.word_to_id[word] = i
            self.id_to_word[i] = word

    def get_vector(self, sentence: Sentence | list[Sentence], count_duplicate: bool = False) -> NDArray[np.uint]:
        """入力された文章のベクトルを返す

        Parameters
        ----------
        - text: テキストの一文
        - count_duplicate: 重複をカウントするかどうか
        """
        if type(sentence) is list and type(sentence[0]) is Sentence:
            vector1: NDArray[np.uint] = np.zeros((len(sentence), len(self.word_to_id)), dtype=np.uint)
            for i, sentence_i in enumerate(sentence):
                for word in sentence_i:
                    try:
                        vector1[i, self.word_to_id[word.base_form]] = 1 + (vector1[i, self.word_to_id[word.base_form]] * count_duplicate)
                    except (KeyError, IndexError):
                        pass
            return vector1
        elif type(sentence) is Sentence:
            vector2: NDArray[np.uint] = np.zeros(len(self.word_to_id), dtype=np.uint)
            for word in sentence:
                try:
                    vector2[self.word_to_id[word.base_form]] = 1 + (vector2[self.word_to_id[word.base_form]] * count_duplicate)
                except (KeyError, IndexError):
                    pass
            return vector2
        else:
            raise TypeError("sentence must be Sentence or list[Sentence]")
