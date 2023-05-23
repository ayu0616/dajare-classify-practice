import MeCab

from word import Word


class BagOfWords:
    def __init__(self) -> None:
        self.tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
        self.word_set: set[str] = set()

    def add(self, text: str) -> None:
        res: str = self.tagger.parse(text)
        for line in res.splitlines():
            if line == "EOS" or line == "":
                continue
            word = Word(line)
            # part_of_speech = line.split("\t")[3].split("-")[0]
            if word.is_content_word:
                self.word_set.add(word.base_form)

    def assign_id(self) -> None:
        self.word_to_id: dict[str, int] = {}
        self.id_to_word: dict[int, str] = {}
        for i, word in enumerate(self.word_set):
            self.word_to_id[word] = i
            self.id_to_word[i] = word

    def get_vector(self, text: str) -> list[int]:
        res: str = self.tagger.parse(text)
        vector: list[int] = [0] * len(self.word_set)
        for line in res.splitlines():
            if line == "EOS" or line == "":
                continue
            word = Word(line)
            try:
                vector[self.word_to_id[word.base_form]] += 1
            except KeyError:
                pass
        return vector


if __name__ == "__main__":
    bow = BagOfWords()
    bow.add("私の部屋は綺麗な部屋とは程遠い")
    bow.add("アルミ缶の上にある蜜柑がみっかんない")
    bow.add("私はラーメンが好きです")
    bow.add("富士山は日本一高い山です")
    bow.add("私は富士山が好きです")
    print(bow.word_set)

    bow.assign_id()

    vec = bow.get_vector("私は好きなラーメンを食べたいと思っています")
    print(vec)

    tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
    res1 = tagger.parse("走る")
    res2 = tagger.parse("走った")
    w1 = Word(res1.splitlines()[0])
    w2 = Word(res2.splitlines()[0])
    print(w1, w2)
    print(w1 == w2)
