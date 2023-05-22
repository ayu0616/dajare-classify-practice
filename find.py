from collections import deque

import MeCab

tagger = MeCab.Tagger("-Ochasen -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
res = tagger.parse("熱中症防止に帽子をかぶる")
kana = "".join([line.split("\t")[1] for line in res.splitlines()[:-1]])

dajas: list[tuple[tuple[int, int], tuple[int, int]]] = []
for i in range(len(kana) - 1):
    for j in range(i + 1, len(kana) - 1):
        if kana[i : i + 2] == kana[j : j + 2]:
            dajas.append(((i, i + 1), (j, j + 1)))

