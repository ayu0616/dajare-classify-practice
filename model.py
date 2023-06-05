import MeCab
import numpy as np
from numpy.typing import NDArray
from sklearn.decomposition import PCA
from sklearn.svm import SVC

import match_yomi
from bag_of_words import BagOfWords
from consonant import Corpus
from setting import DIC_DIR
from word import Word


class DajareClassifier(SVC):
    def __init__(self):
        self.bow = BagOfWords()
        self.tagger = MeCab.Tagger(f"-Ochasen -d {DIC_DIR}")

    def set_bow(self, X: list[list[Word]]):
        """BoWを設定する

        Parameters
        ----------
        - X: 文章のリスト
        """
        for sentence in X:
            for word in sentence:
                self.bow.add(word)
        self.bow.assign_id()

    def get_bow_vector(self, sentences: list[list[Word]]):
        """BoWのベクトルを取得する

        Parameters
        ----------
        - sentences: 文章のリスト
        """
        v = self.bow.get_vector(sentences)  # 次元数が大きいベクトル
        pca = PCA(n_components=20)
        pca.fit(v)
        return pca.transform(v)  # 次元数が小さいベクトル

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
        bow = self.get_bow_vector(X_words)
        match_yomi_res_li = list(map(match_yomi.check, X_words))
        match_yomi_res = np.array(match_yomi_res_li, dtype=np.uint)

        self.corpus = Corpus(X_words)
        consonant_score = np.array(list(map(self.corpus.calc_score, X_words)), dtype=np.uint)

        X_in = np.concatenate([bow, match_yomi_res.reshape(-1, 1), consonant_score.reshape(-1, 1)], axis=1)

        super().fit(X_in, y)

    def predict(self, X: list[str]) -> NDArray[np.uint]:
        """予測する

        Parameters
        ----------
        - X: 予測データのリスト（文字列で1文）
        """
        X_words = list(map(lambda Xi: Word.from_sentence(Xi, self.tagger), X))
        bow = np.array(list(map(self.get_bow_vector, X_words)))
        match_yomi_res = np.array(list(map(match_yomi.check, X_words)), dtype=np.uint)
        consonant_score = np.array(list(map(self.corpus.calc_score, X_words)), dtype=np.uint)
        X_in = np.concatenate([bow, match_yomi_res.reshape(-1, 1), consonant_score.reshape(-1, 1)], axis=1)
        return super().predict(X_in)
