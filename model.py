from typing import Literal

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix, hstack
from scipy.sparse.linalg import svds
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

import match_yomi
from bag_of_words import BagOfWords
from consonant import Corpus
from dajare_score import calc_score
from word import Sentence


class SparsePCA:
    """疎行列に対応したPCA"""

    def __init__(self, cum_explained_variance_ratio: float = 0.95, k: int = 6):
        self.cum_explained_variance_ratio = cum_explained_variance_ratio
        self.k = k
        pass

    def fit(self, X: csr_matrix):
        self.u, self.s, self.vt = svds(X, k=self.k)
        scores = (self.s**2) / np.sum(self.s**2)
        for i in range(self.s.size):
            self.use_num = self.s.size - i - 1
            if np.sum(scores[self.s.size - i - 1 :]) >= self.cum_explained_variance_ratio:
                break

    def transform(self, X: csr_matrix):
        return X @ self.vt.T[:, self.use_num :]

    def fit_transform(self, X: csr_matrix):
        self.fit(X)
        return self.transform(X)


class PreProcess:
    def __init__(
        self, cum_explained_variance_ratio: float = 0.95, bow_count_dup: bool = False, consonant_func: Literal["normal", "max"] = "normal", bow_min_cnt: int = 1
    ):
        """前処理

        Parameters
        ----------
        - cum_explained_variance_ratio: BoWの変数を残すPCAの累積寄与率の基準
        - bow_count_dup: BoWの単語の重複をカウントするかどうか
        - consonant_func: 子音類似度の計算方法
        """
        self.bow = BagOfWords()
        self.pca = PCA(n_components=200)
        self.standard_scaler = StandardScaler(with_mean=False)
        self.cum_explained_variance_ratio = cum_explained_variance_ratio
        self.bow_count_dup = bow_count_dup
        self.consonant_func = consonant_func
        self.bow_min_cnt = bow_min_cnt

    def transform(self, X: list[Sentence]):
        X_bow = self.bow.get_vector(X, self.bow_count_dup)
        X_bow = self.pca.transform(X_bow)
        cum_score = np.cumsum(self.pca.explained_variance_ratio_)
        X_bow = X_bow[:, cum_score < self.cum_explained_variance_ratio]

        X_score = np.array(list(map(calc_score, X)))
        X_res = np.concatenate([X_bow, X_score.reshape(-1, 1)], axis=1)
        X_res = self.standard_scaler.transform(X_res)
        return X_res

    def fit_transform(self, X: list[Sentence]):
        for s in X:
            for w in s:
                self.bow.add(w)
        self.bow.assign_id(self.bow_min_cnt)
        X_bow = self.bow.get_vector(X, self.bow_count_dup)
        X_bow = self.pca.fit_transform(X_bow)
        cum_score = np.cumsum(self.pca.explained_variance_ratio_)
        X_bow = X_bow[:, cum_score < self.cum_explained_variance_ratio]
        X_score = np.array(list(map(calc_score, X)))
        X_res = np.concatenate([X_bow, X_score.reshape(-1, 1)], axis=1)
        X_res = self.standard_scaler.fit_transform(X_res)
        return X_res


class DajareClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, estimator_class, bow_reduction_rate: float = 1.0, **estimator_params):
        """駄洒落判定器

        Parameters
        ----------
        - estimator: 分類器
        - bow_reduction_rate: BoWの次元削減率
        """
        self.estimator = estimator_class(**estimator_params)
        self.bow = BagOfWords()
        self.bow_reduction_rate = bow_reduction_rate
        self.pca: None | PCA = None
        self.standard_scaler = StandardScaler(with_mean=False)
        self.lr = LinearRegression()

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
            - 0: 駄洒落でない
        """
        X_words = list(map(Sentence.from_sentence, X))
        self.set_bow(X_words)
        bow = self.bow.get_vector(X_words)
        # if self.bow_reduction_rate < 1.0:
        #     self.pca = PCA(n_components=int(bow.shape[1] * self.bow_reduction_rate))
        #     bow = self.pca.fit_transform(bow)
        match_yomi_res_li = list(map(match_yomi.check, X_words))
        match_yomi_res = np.array(match_yomi_res_li, dtype=np.uint)

        self.corpus = Corpus(X_words)
        consonant_score = np.array(list(map(self.corpus.calc_max_score, X_words)), dtype=np.uint)

        self.lr.fit(consonant_score.reshape(-1, 1), y)
        consonant_bin = self.lr.predict(consonant_score.reshape(-1, 1))

        # X_in = np.concatenate([bow, match_yomi_res.reshape(-1, 1), consonant_bin.reshape(-1, 1)], axis=1)
        X_in = csr_matrix(bow)
        X_in = hstack([X_in, csr_matrix(match_yomi_res.reshape(-1, 1))])
        X_in = hstack([X_in, csr_matrix(consonant_bin.reshape(-1, 1))])
        X_in = self.standard_scaler.fit_transform(X_in)

        return self.estimator.fit(X_in, y)

    def predict(self, X: list[str]) -> NDArray[np.uint]:
        """予測する

        Parameters
        ----------
        - X: 予測データのリスト（文字列で1文）
        """
        X_words = list(map(Sentence.from_sentence, X))
        bow = self.bow.get_vector(X_words)
        # if self.pca is not None:
        #     bow = self.pca.transform(bow)
        match_yomi_res = np.array(list(map(match_yomi.check, X_words)), dtype=np.uint)
        consonant_score = np.array(list(map(self.corpus.calc_max_score, X_words)), dtype=np.uint)
        consonant_bin = self.lr.predict(consonant_score.reshape(-1, 1))
        # X_in = np.concatenate([bow, match_yomi_res.reshape(-1, 1), consonant_bin.reshape(-1, 1)], axis=1)
        X_in = csr_matrix(bow)
        X_in = hstack([X_in, csr_matrix(match_yomi_res.reshape(-1, 1))])
        X_in = hstack([X_in, csr_matrix(consonant_bin.reshape(-1, 1))])
        X_in = self.standard_scaler.transform(X_in)
        return self.estimator.predict(X_in)
