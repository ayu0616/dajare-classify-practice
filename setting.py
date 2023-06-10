import os

import dotenv

dotenv.load_dotenv()

__DIC_DIR = os.getenv("DIC_DIR")  # 辞書ディレクトリ
if __DIC_DIR is None:
    raise EnvironmentError("DIC_DIR is not set")
DIC_DIR = __DIC_DIR

CONTENT_WORD_SET = {"名詞", "固有名詞", "動詞", "形容詞", "副詞", "感動詞"}  # 内容語の品詞リスト
