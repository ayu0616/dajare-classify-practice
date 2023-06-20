from collections.abc import Iterator
from typing import Iterable

import romkan

from setting import CONTENT_WORD_SET


class Mora:
    __DOUBLE_CONSONANT__ = "Q"  # 促音
    __SYLLABIC_NASAL__ = "N"  # 撥音
    __NULL__ = "*"  # 該当なし

    def __init__(self, yomi_roman: str):
        """
        Parameters
        ----------
        - yomi_roman: ローマ字表記の読み仮名で一つのモーラ
        """
        if yomi_roman == "xtsu":
            self.consonant = self.__DOUBLE_CONSONANT__
            self.vowel = self.__NULL__
        elif yomi_roman == "n":
            self.consonant = self.__SYLLABIC_NASAL__
            self.vowel = self.__NULL__
        elif len(yomi_roman) > 1:
            self.consonant = yomi_roman[:-1]
            self.vowel = yomi_roman[-1]
        else:
            self.consonant = self.__NULL__
            self.vowel = yomi_roman[-1]

    @property
    def is_only_vowel(self):
        """母音のみかどうか"""
        return self.consonant == self.__NULL__

    @property
    def is_double_consonant(self):
        """促音かどうか"""
        return self.consonant == self.__DOUBLE_CONSONANT__

    @property
    def is_syllabic_nasal(self):
        """撥音かどうか"""
        return self.consonant == self.__SYLLABIC_NASAL__

    def __repr__(self) -> str:
        return f"({self.consonant}, {self.vowel})"

    def __eq__(self, __value: object) -> bool:
        if type(__value) != Mora:
            return NotImplemented

        return self.consonant == __value.consonant and self.vowel == __value.vowel


class Word:
    def __init__(self, mecab_res: str) -> None:
        """
        Parameters
        ----------
        mecab_res: mecabの出力結果で形態素ごとに改行されたものの一行
        """
        self.surface = mecab_res.split("\t")[0]
        self.yomi = mecab_res.split("\t")[1]
        self.part_of_speech = mecab_res.split("\t")[3].split("-")[0]
        self.base_form = mecab_res.split("\t")[2]
        self.moras = self.__get_moras()

    @property
    def is_content_word(self):
        """内容語かどうか"""
        return self.part_of_speech in CONTENT_WORD_SET

    @property
    def is_symbol(self):
        """記号かどうか"""
        return self.part_of_speech == "記号"

    def __get_romanized_yomi_li(self):
        """読み仮名のローマ字表記を返す

        - 区切り単位はモーラ
        - 拗音は一つ前の仮名と結合してから処理する
        - 長音は前の仮名の母音に変換する
        """
        kanas = list(self.yomi)
        romanized_li: list[str] = []
        added_now = False
        for i in range(1, len(kanas)):
            if added_now:
                added_now = False
                continue
            prev = kanas[i - 1]
            now = kanas[i]
            if now in {"ャ", "ュ", "ョ", "ヮ"}:
                romanized_li.append(romkan.to_roma(prev + now))
                added_now = True
            elif now == "ー":
                roman = romkan.to_roma(prev)
                romanized_li.append(roman)
                romanized_li.append(roman[-1])
                added_now = True
            else:
                romanized_li.append(romkan.to_roma(prev))
        if not added_now:
            romanized_li.append(romkan.to_roma(kanas[-1]))
        return romanized_li

    def __get_moras(self):
        """読み仮名のローマ字表記からモーラを返す"""
        romanized_yomi_li = self.__get_romanized_yomi_li()
        return list(map(Mora, romanized_yomi_li))

    def __repr__(self) -> str:
        return self.surface

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Word):
            return NotImplemented
        return self.base_form == __value.base_form and self.part_of_speech == __value.part_of_speech

    def __hash__(self) -> int:
        return super().__hash__()


class Sentence(list[Word]):
    def __init__(self, words: Iterable[Word]) -> None:
        super().__init__(words)
        self.word_len = len(self)  # 単語数
        self.char_len = sum([len(word.surface) for word in self if not word.is_symbol])  # 記号以外の文字数

    @classmethod
    def from_words(cls, words: Iterable[Word]) -> "Sentence":
        return cls(words)

    @classmethod
    def from_sentence(cls, tagged_sentence: str) -> "Sentence":
        lines = tagged_sentence.splitlines()
        if lines[-1] == "EOS":
            lines.pop()
        return cls([Word(line) for line in lines])

    @property
    def removed_symbol(self):
        """記号を除いた単語のリスト"""
        return self.from_words([word for word in self if not word.is_symbol])

    def __repr__(self) -> str:
        return "".join([word.surface for word in self])

    def __iter__(self) -> Iterator[Word]:
        return super().__iter__()
