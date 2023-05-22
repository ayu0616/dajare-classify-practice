import MeCab

from word import Word


def split_consonant(text: str):
    tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
    res: str = tagger.parse(text)
    words = [Word(line) for line in res.splitlines() if line != "EOS"]
