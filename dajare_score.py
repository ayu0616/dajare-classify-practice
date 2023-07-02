from word import Mora, Sentence, Word

ADDITIONAL_MORAS = [Mora.DOUBLE_CONSONANT_MORA(), Mora.SYLLABIC_NASAL_MORA()]
THRESHOLD = 0.66  # どのスコアから駄洒落らしいと評価するかの閾値
NULL_WORD = Word("*	*	*	記号-一般		")


def __calc(moras: list[Mora], seed_mora: list[Mora]) -> float:
    """seed_moraと一致するモーラの数を数える

    Parameters
    ----------
    - moras: 文章全体のモーラのリスト
    - seed_mora: seedとなるモーラのリスト
    - seed_score: 文章中に含まれる種表現と同一の単語の数
    """
    if len(seed_mora) <= 1:
        return 0
    res: list[float] = []
    for i in range(len(moras) - len(seed_mora) + 1):
        s = 0
        m = moras[i : i + len(seed_mora)]
        f = True  # すべての母音が一致しているか
        for j in range(len(seed_mora)):
            if m[j].vowel != seed_mora[j].vowel:
                f = False
                break
        if not f:
            continue
        for j in range(len(m)):
            if m[j].consonant == seed_mora[j].consonant:
                s += 1
        res.append(s / len(seed_mora))
    res.sort(reverse=True)
    return res[0] if len(res) > 0 else 0


def calc_score(sentence: Sentence) -> float:
    score = 0.0  # 文章全体のスコアの合計（最大値を取る）
    for i, seed in enumerate(sentence.removed_symbol):
        if not seed.is_content_word or len(seed.moras) <= 1:
            continue
        sentence_1 = sentence.removed_symbol[:i] + [NULL_WORD] + sentence.removed_symbol[i + 1 :]
        moras = [mora for word in sentence_1 for mora in word.moras]
        s = 0.0  # 種表現ごとのスコア（最大値を取る）
        s = max(s, __calc(moras, seed.moras))
        for i in range(len(seed.moras)):
            for additional_mora in ADDITIONAL_MORAS:
                m = seed.moras[: i + 1] + [additional_mora] + seed.moras[i + 1 :]
                s = max(s, __calc(moras, m))
            if seed.moras[i].is_only_vowel:
                m = seed.moras[: i + 1] + [seed.moras[i]] + seed.moras[i + 1 :]
                s = max(s, __calc(moras, m))
            elif seed.moras[i].is_double_consonant or seed.moras[i].is_syllabic_nasal:
                m = seed.moras[:i] + seed.moras[i + 1 :]
                s = max(s, __calc(moras, m))
        score = max(score, s)
    return score
