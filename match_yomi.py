from word import Sentence


def check(sentence: Sentence) -> bool:
    yomi_sentence = "".join(map(lambda word: word.yomi, sentence))
    seed_candidate_yomi = [word.yomi for word in sentence if word.is_content_word and len(word.yomi) >= 2]
    counters = [yomi_sentence.count(seed) - seed_candidate_yomi.count(seed) for seed in seed_candidate_yomi]
    return len(counters) > 0 and max(counters) >= 1
