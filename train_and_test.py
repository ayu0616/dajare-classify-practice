import numpy as np
from model import DajareClassifier, PreProcess
import random
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from zipfile import ZipFile
from sklearn.model_selection import train_test_split
from word import Sentence
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import MeCab
from setting import DIC_DIR

def main():
    with ZipFile("./data.zip", "r")as zip_f:
        with zip_f.open("data/dajare.txt") as f:
            tagged_dajare = f.read().decode("utf-8")
        with zip_f.open("data/conversation.txt") as f:
            tagged_conversation = f.read().decode("utf-8")


    dajare_sentences = tagged_dajare.split("EOS\n")
    conversation_sentences = tagged_conversation.split("EOS\n")
    dajare_sentences = list(filter(bool, dajare_sentences))
    conversation_sentences = list(filter(bool, conversation_sentences))
    each_data_size = min(len(dajare_sentences), len(conversation_sentences))

    random.seed(0)
    dajare_sentences = random.sample(dajare_sentences, each_data_size)
    conversation_sentences = random.sample(conversation_sentences, each_data_size)
    X = Sentence.from_sentences(dajare_sentences + conversation_sentences)
    y = np.array([1] * each_data_size + [0] * each_data_size)

    with open("X.pkl", "wb") as f:
        pickle.dump(X, f)
    with open("y.pkl", "wb") as f:
        pickle.dump(y, f)
    with open("X.pkl", "rb") as f:
        X = pickle.load(f)
    with open("y.pkl", "rb") as f:
        y = pickle.load(f)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.333, random_state=0)

    print("前処理開始")
    pre_process = PreProcess(consonant_func="max", bow_min_cnt=2)
    X_train = pre_process.fit_transform(X_train)
    with open("pre_process.pkl", "wb") as f:
        pickle.dump(pre_process, f)
    print("前処理終了")

    print("学習開始")
    model = LogisticRegression()
    model.fit(X_train, y_train)
    print("学習終了")

    print("評価開始")
    X_test = pre_process.transform(X_test)
    y_pred = model.predict(X_test)
    confusion_matrix(y_test, y_pred)
    print("正解率:", (y_test == y_pred).sum() / len(y_test))
    print("適合率:", (y_test & y_pred).sum() / y_pred.sum())
    print("再現率:", (y_test & y_pred).sum() / y_test.sum())
    print("F値:", 2 * (y_test & y_pred).sum() / (y_test.sum() + y_pred.sum()))
    pickle.dump(model, open("model.pkl", "wb"))

    sentences = ["竹やぶ焼けた", "秋田新幹線には飽きた", "豊穣の女神、北条氏康", "たとえば、ゴミ箱の中には卵が入っている", "卵焼きを食べたい", "あと一粒の涙で、一言の勇気で", "機械学習で駄洒落を検出する", "たまに検出ミスが起こる", "競技プログラミングに取り組んでいるところです"]
    tagger = MeCab.Tagger(f"-Ochasen -d {DIC_DIR}")
    sentences = [tagger.parse(sentence) for sentence in sentences]
    sentences = Sentence.from_sentences(sentences)
    p = model.predict(pre_process.transform(sentences))
    for i in range(len(sentences)):
        print(sentences[i], p[i])

if __name__ == "__main__":
    main()