from typing import Literal

import MeCab
import numpy as np
from numpy.typing import NDArray
from sklearn.decomposition import PCA
from sklearn.svm import SVC

import match_yomi
from bag_of_words import BagOfWords
from consonant import Corpus
from setting import DIC_DIR
from word import Sentence, Word


class DajareClassifier(SVC):
    def __init__(self, C: float = 1.0, gamma: float | Literal["scale", "auto"] = "scale", bow_reduction_rate: float = 1.0):
        """駄洒落判定器

        Parameters
        ----------
        - C: SVMのパラメータ
        - gamma: SVMのパラメータ
        - bow_reduction_rate: BoWの次元削減率
        """
        super().__init__(C=C, gamma=gamma)
        self.bow = BagOfWords()
        self.tagger = MeCab.Tagger(f"-Ochasen -d {DIC_DIR}")
        self.bow_reduction_rate = bow_reduction_rate
        self.pca: None | PCA = None

    def set_bow(self, X: list[Sentence]):
        """BoWを設定する

        Parameters
        ----------
        - X: 文章のリスト
        """
        for sentence in X:
            for word in sentence:
                self.bow.add(word)
        self.bow.assign_id()

    def fit(self, X: list[str], y: NDArray[np.uint]):
        """学習する

        Parameters
        ----------
        - X: 学習データのリスト（文字列で1文）
        - y: 学習データのラベル
            - 1: 駄洒落
            - -1: 駄洒落でない
        """
        X_words = list(map(lambda Xi: Word.from_sentence(Xi, self.tagger), X))
        self.set_bow(X_words)
        bow = self.bow.get_vector(X_words)
        if self.bow_reduction_rate < 1.0:
            self.pca = PCA(n_components=int(bow.shape[1] * self.bow_reduction_rate))
            bow = self.pca.fit_transform(bow)
        match_yomi_res_li = list(map(match_yomi.check, X_words))
        match_yomi_res = np.array(match_yomi_res_li, dtype=np.uint)

        self.corpus = Corpus(X_words)
        consonant_score = np.array(list(map(self.corpus.calc_max_score, X_words)), dtype=np.uint)
        X_in = np.concatenate([bow, match_yomi_res.reshape(-1, 1), consonant_score.reshape(-1, 1)], axis=1)

        super().fit(X_in, y)

    def predict(self, X: list[str]) -> NDArray[np.uint]:
        """予測する

        Parameters
        ----------
        - X: 予測データのリスト（文字列で1文）
        """
        X_words = list(map(lambda Xi: Word.from_sentence(Xi, self.tagger), X))
        bow = self.bow.get_vector(X_words)
        if self.pca is not None:
            bow = self.pca.transform(bow)
        match_yomi_res = np.array(list(map(match_yomi.check, X_words)), dtype=np.uint)
        consonant_score = np.array(list(map(self.corpus.calc_max_score, X_words)), dtype=np.uint)
        X_in = np.concatenate([bow, match_yomi_res.reshape(-1, 1), consonant_score.reshape(-1, 1)], axis=1)
        return super().predict(X_in)
