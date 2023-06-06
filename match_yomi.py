from word import Sentence


def check(sentence: Sentence) -> bool:
    yomi_sentence = "".join(map(lambda word: word.yomi, sentence))
    seed_candidate_yomi = [word.yomi for word in sentence if word.is_content_word]
    counters = [yomi_sentence.count(seed) for seed in seed_candidate_yomi]
    return len(counters) > 0 and max(counters) >= 2
