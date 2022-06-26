Sentiment Analysis

crawler.py爬下google play comment後，去除英文、數字、特殊符號，
並用jieba斷詞。使用LSTM訓練模型，fastapi部屬網站。


Install all the dependencies
``` python
$ python -m venv venv
$ source venv/bin/activate
$ python -m pip install -r requirements.txt
```
Start server.
``` python
uvicorn main:app --reload
```
