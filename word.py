import romkan


class Mora:
    __DOUBLE_CONSONANT__ = "Q"
    __SYLLABIC_NASAL__ = "N"
    __NULL__ = "*"

    def __init__(self, yomi_roman: str):
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
        return str((self.consonant, self.vowel))


class Word:
    def __init__(self, mecab_res: str) -> None:
        self.surface = mecab_res.split("\t")[0]
        self.yomi = mecab_res.split("\t")[1]
        self.part_of_speech = mecab_res.split("\t")[3].split("-")[0]
        self.base_form = mecab_res.split("\t")[2]
        self.moras = self.__get_moras()

    def __get_yomi_roman_li(self):
        """読み仮名のローマ字表記を返す

        - 区切り単位はモーラ
        - 拗音は一つ前の仮名と結合してから処理する
        - 長音は前の仮名の母音に変換する
        """
        kanas = list(self.yomi)
        # roman_li:list[str] = [romkan.to_roma(kana) for kana in kanas]
        roman_li: list[str] = []
        for i in range(1, len(kanas)):
            prev = kanas[i - 1]
            now = kanas[i]
            if now in {"ャ", "ュ", "ョ", "ヮ"}:
                roman_li.append(romkan.to_roma(prev + now))
                i += 1
            elif now == "ー":
                roman = romkan.to_roma(prev)
                roman_li.append(roman)
                roman_li.append(roman[-1])
                i += 1
            else:
                roman_li.append(romkan.to_roma(prev))
        return roman_li

    def __get_moras(self):
        """読み仮名のローマ字表記からモーラを返す"""
        yomi_roman_li = self.__get_yomi_roman_li()
        return list(map(Mora, yomi_roman_li))

    def __repr__(self) -> str:
        return self.surface

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Word):
            return NotImplemented
        return self.base_form == __value.base_form and self.part_of_speech == __value.part_of_speech

    def __hash__(self) -> int:
        return super().__hash__()


if __name__ == "__main__":
    from pprint import pprint

    import MeCab

    tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
    res = tagger.parse("ショベルカーが走っているんだな")
    yomi_li = [Word(line).moras for line in res.splitlines() if line != "EOS"]
    pprint(yomi_li)
