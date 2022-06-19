from urllib.request import Request
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.hash import bcrypt
import jwt
from keras.models import load_model
import pickle
import re
import jieba
import numpy as np
from keras.preprocessing import sequence
import uvicorn

app = FastAPI(
    title="Sentiment Model API",
    description="A simple API that use NLP model to predict the sentiment of google play reviews",
    version="0.1",
)

JWT_SCRET = "09d25e094faa6ca2556c818166b7a9563b93f7099a6f0f4caa7cf63b88e8d3e7"
model = load_model('LSTM/model/my_model.h5')

def regex_filter(s_line):
    # 英文、數字，以及空格
    special_regex = re.compile(r"[a-zA-Z0-9\s]+")
    # 英文標點符號和特殊符號
    en_regex = re.compile(r"[.…{|}#$%&\'()*+,!-_./:~^;<=>?@★●，。]+")
    # 中文標點符號
    zn_regex = re.compile(r"[《》、，“”；～？！：（）【】]+")

    s_line = special_regex.sub(r"", s_line)
    s_line = en_regex.sub(r"", s_line)
    s_line = zn_regex.sub(r"", s_line)
    return s_line

templates = Jinja2Templates(directory="templates")

@app.get("/predict")
def home(request: Request):
    result = "Input comment"
    return templates.TemplateResponse('form.html', context={'request': request, 'result': result})

@app.post("/predict")
def predict(request: Request, sentence: str = Form(...)):
    with open('LSTM/model/word_dict.pickle', 'rb') as handle:
        word2index = pickle.load(handle)
    print(sentence)
    xx = np.empty(1, dtype=list)
    # 數據預處理
    sentence = regex_filter(sentence)
    words = jieba.cut(sentence)
    seq = []
    for word in words:
        if word in word2index:
            seq.append(word2index[word])
        else:
            seq.append(word2index['UNK'])
    xx[0] = seq
    xx = sequence.pad_sequences(xx, maxlen=80)

    label2word = {0: '1 or 2', 1: '3', 2: '4 or 5'}
    for x in model.predict(xx):
        x = x.tolist()
        label = x.index(max(x[0], x[1], x[2]))
        result = {"prediction": '{}'.format(label2word[label])}
    
    return templates.TemplateResponse('form.html', context={'request': request, 'result': result["prediction"]})

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)
    
    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)

register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')

async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user

@app.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        return {'error': 'invaild password'}
    user_obj = await User_Pydantic.from_tortoise_orm(user)
    token = jwt.encode(user_obj.dict(), JWT_SCRET)
    return {'access_token': token, 'token_type': 'bearer'}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SCRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
            detail= 'invaild username or password')
    return await User_Pydantic.from_tortoise_orm(user)

@app.post('/users', response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    user_obj = User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)

@app.get('/users/me', response_model=User_Pydantic)
async def get_user(user: User_Pydantic = Depends(get_current_user)):
    return user

# uvicorn main:app --reload
# docker run -p 8000:8000 sentiment_analysis