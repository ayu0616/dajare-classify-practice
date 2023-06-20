from word import Sentence


def check(sentence: Sentence) -> bool:
    yomi_sentence = "".join(map(lambda word: word.yomi, sentence))
    seed_candidate = [word for word in sentence if word.is_content_word and len(word.moras) >= 2]
    counters = [yomi_sentence.count(seed.yomi) - seed_candidate.count(seed) for seed in seed_candidate]
    return len(counters) > 0 and max(counters) >= 1
