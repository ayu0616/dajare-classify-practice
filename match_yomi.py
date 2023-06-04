from word import Word


def check(words: list[Word]) -> bool:
    yomi_sentence = "".join(map(lambda word: word.yomi, words))
    seed_candidate_yomi = [word.yomi for word in words if word.is_content_word]
    counters = [yomi_sentence.count(seed) for seed in seed_candidate_yomi]
    return len(counters) > 0 and max(counters) >= 2
