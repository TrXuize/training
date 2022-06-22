Sentiment Analysis

LSTM model trained with Chinese google play comment, deploy with fastapi.


Install all the dependencies
$ python -m venv venv
$ source venv/bin/activate
$ python -m pip install -r requirements.txt

Start the API server.
uvicorn main:app --reload
