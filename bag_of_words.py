import MeCab
import numpy as np
from numpy.typing import NDArray

from word import Word


class BagOfWords:
    def __init__(self) -> None:
        self.tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
        self.word_set: set[str] = set()

    def add(self, word: Word) -> None:
        """入力された文章をBOWに追加する

        Parameters
        ----------
        - word: 単語
        """
        if word.is_content_word:
            self.word_set.add(word.base_form)

    def assign_id(self) -> None:
        """単語にIDを割り振る"""
        self.word_to_id: dict[str, int] = {}
        self.id_to_word: dict[int, str] = {}
        for i, word in enumerate(self.word_set):
            self.word_to_id[word] = i
            self.id_to_word[i] = word

    def get_vector(self, sentence: list[Word]) -> NDArray[np.uint]:
        """入力された文章のベクトルを返す

        Parameters
        ----------
        - text: テキストの一文
        """
        vector: NDArray[np.uint] = np.zeros(len(self.word_set), dtype=np.uint)
        for word in sentence:
            try:
                vector[self.word_to_id[word.base_form]] += 1
            except KeyError:
                pass
        return vector
