import glob
import json

path_list = glob.glob("dajare_data/*.json")
dajare_text_set: set[str] = set()
cnt = 1
for path in path_list:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        text: str = item["text"]
        for t in text.splitlines():
            if t not in dajare_text_set:
                t = t.strip()
                dajare_text_set.add(t)
                print(cnt, t)
                cnt += 1

dajare_text_set -= {"", " ", "　", "\n", "\t"}

with open("./dajare_data/dajare.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(dajare_text_set)))
