import MeCab

from setting import CONTENT_WORD_SET
from word import Word


def check(text: str) -> bool:
    tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
    res: str = tagger.parse(text)
    words = [Word(line) for line in res.splitlines() if line != "EOS"]
    yomi_sentence = "".join(map(lambda word: word.yomi, words))
    seed_candidate_yomi = [word.yomi for word in words if word.is_content_word]
    counters = [yomi_sentence.count(seed) for seed in seed_candidate_yomi]
    return max(counters) >= 2
