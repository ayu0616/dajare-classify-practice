from word import Sentence


def check(sentence: Sentence) -> bool:
    moras = [mora for word in sentence for mora in word.moras]
    seed_candidate = [word for word in sentence if word.is_content_word and len(word.moras) >= 2]
    cnt = 0
    for seed in seed_candidate:
        tmp_cnt = 1 - seed_candidate.count(seed)
        for i in range(len(moras) - len(seed.moras) + 1):
            if moras[i : i + len(seed.moras)] == seed.moras:
                tmp_cnt += 1
        cnt = max(cnt, tmp_cnt)
    return cnt >= 2
