import MeCab

from word import Word


class BagOfWords:
    def __init__(self) -> None:
        self.tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
        self.word_set: set[str] = set()

    def add(self, text: str) -> None:
        """入力された文章をBOWに追加する

        Parameters
        ----------
        - text: コーパスのテキストの一文
        """
        res: str = self.tagger.parse(text)
        for line in res.splitlines():
            if line == "EOS" or line == "":
                continue
            word = Word(line)
            # part_of_speech = line.split("\t")[3].split("-")[0]
            if word.is_content_word:
                self.word_set.add(word.base_form)

    def assign_id(self) -> None:
        """単語にIDを割り振る"""
        self.word_to_id: dict[str, int] = {}
        self.id_to_word: dict[int, str] = {}
        for i, word in enumerate(self.word_set):
            self.word_to_id[word] = i
            self.id_to_word[i] = word

    def get_vector(self, text: str) -> list[int]:
        """入力された文章のベクトルを返す

        Parameters
        ----------
        - text: テキストの一文
        """
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
