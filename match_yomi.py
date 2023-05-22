import MeCab

from setting import CONTENT_WORD_SET
from word import Word


def check(text: str) -> bool:
    tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
    res: str = tagger.parse(text)
    words = [Word(line) for line in res.splitlines() if line != "EOS"]
    yomi_sentence = "".join(map(lambda word: word.yomi, words))
    seed_candidate_yomi = [word.yomi for word in words if word.part_of_speech in CONTENT_WORD_SET]
    counters = [yomi_sentence.count(seed) for seed in seed_candidate_yomi]
    return max(counters) >= 2


if __name__ == "__main__":
    texts = """ゆで卵を茹でた孫
    布団が吹っ飛んだ
    お腹が空いた
    今日と明日は京都に行きます
    京都と奈良に行きたい
    期待通りに行きたい
    玉ねぎをたまたま買い忘れた
    八百屋で玉ねぎをたまたま値切る
    おやおや、八百屋に親が来た"""
    for text in texts.splitlines():
        t = text.strip()
        print(t, "Yes" if check(t) else "No")
