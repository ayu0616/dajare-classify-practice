import math
from collections import defaultdict
from typing import overload

import MeCab

from word import Word


class Corpus:
    def __init__(self, text: str) -> None:
        """コーパスを初期化する

        Parameters
        ----------
        - text: コーパスのテキスト（各文は改行で分割）
        """
        tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
        results: list[str] = [tagger.parse(line).splitlines() for line in text.splitlines()]
        line_words: list[list[Word]] = []
        for res_line in results:
            line: list[Word] = []
            for res_word in res_line:
                if res_word != "EOS":
                    line.append(Word(res_word))
            line_words.append(line)
        line_consonants = [[mora.consonant for word in words for mora in word.moras] for words in line_words]
        self.n_pq: defaultdict[tuple[str, str], int] = defaultdict(int)
        for cons in line_consonants:
            for i in range(len(cons)):
                p = cons[i]
                for j in range(i + 1, len(cons)):
                    q = cons[j]
                    self.n_pq[(p, q)] += 1
        self.n_pair = sum(self.n_pq.values())

    def p(self, p: str):
        """子音ペアのうち、pが含まれるものの割合を計算する

        Parameters
        ----------
        - p: 子音
        """
        return len(list(filter(lambda x: p in x, self.n_pq.keys()))) / self.n_pair

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

    def calc_score(self, input: str | list[Word]):
        """子音の音韻類似度スコアを計算する

        Parameters
        ----------
        - input: `文の単語リスト` または `一文の文字列`
        """
        score = 0.0
        if isinstance(input, str):
            tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
            results: list[str] = tagger.parse(input).splitlines()
            words = [Word(res_word) for res_word in results if res_word != "EOS"]
        else:
            words = input
        consonant_seq = [mora.consonant for word in words for mora in word.moras]
        for i, word in enumerate(words):
            if not word.is_content_word:
                continue
            for j in range(len(consonant_seq) - len(word.moras)):
                for k in range(len(word.moras)):
                    score += self.calc_oer(word.moras[k].consonant, consonant_seq[j + k])
        return score


if __name__ == "__main__":
    t = """布団が吹っ飛んだ
    タバコは体に悪い
    あなたは私の妹ですか
    スタバでコーヒーを飲む
    あひるは鳴きます
    とりあえず映画を見る
    今日はとても暑いですね
    エアコンをつけても涼しくなりません
    私は昨日、図書館で面白い本を見つけました
    タイトルは「未来の世界」です
    彼はピアノがとても上手です
    毎日練習しているそうです
    あなたはどんな音楽が好きですか
    私はジャズが好きです
    明日は友達と映画に行きます
    楽しみにしています
    """
    tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
    corpus = Corpus(t)
    test = """布団が吹っ飛んだ
    タバコは体に悪い
    あなたは私の妹ですか
    アルミ缶のリサイクルは大切です
    アルミ缶の上にある蜜柑がみっかんない
    深い海は不快だ
    トマトが野菜かどうかは議論があるところだが私は野菜だと思う"""
    for te in test.splitlines():
        te = te.strip()
        print(te, end=" ")
        print(corpus.calc_score(te))
