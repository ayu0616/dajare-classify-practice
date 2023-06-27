from word import Mora, Sentence

ADDITIONAL_MORAS = [Mora.DOUBLE_CONSONANT_MORA(), Mora.SYLLABIC_NASAL_MORA()]


def count(moras: list[Mora], seed_mora: list[Mora], seed_count) -> int:
    """seed_moraと一致するモーラの数を数える

    Parameters
    ----------
    - moras: 文章全体のモーラのリスト
    - seed_mora: seedとなるモーラのリスト
    - seed_count: 文章中に含まれる種表現と同一の単語の数
    """
    cnt = 0
    for i in range(len(moras) - len(seed_mora) + 1):
        if moras[i : i + len(seed_mora)] == seed_mora:
            cnt += 1
    res = cnt - seed_count
    return res


def check(sentence: Sentence) -> bool:
    moras = [mora for word in sentence for mora in word.moras if not word.is_symbol]
    seed_candidate = [word for word in sentence if word.is_content_word and len(word.moras) >= 2]
    cnt = 0
    for seed in seed_candidate:
        seed_count = sentence.count(seed)
        cnt = max(cnt, count(moras, seed.moras, seed_count))
        for i in range(len(seed.moras)):
            for additional_mora in ADDITIONAL_MORAS:
                m = seed.moras[: i + 1] + [additional_mora] + seed.moras[i + 1 :]
                cnt = max(cnt, count(moras, m, 0))
            if seed.moras[i].is_only_vowel:
                m = seed.moras[: i + 1] + [seed.moras[i]] + seed.moras[i + 1 :]
                cnt = max(cnt, count(moras, m, 0))
            elif seed.moras[i].is_double_consonant or seed.moras[i].is_syllabic_nasal:
                m = seed.moras[:i] + seed.moras[i + 1 :]
                c = 0 if 0 < i < len(seed.moras) - 1 else seed_count
                cnt = max(cnt, count(moras, m, c))
        if cnt >= 1:
            return True
    return False
