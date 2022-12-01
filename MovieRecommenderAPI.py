import numpy as np
import pandas as pd
import joblib
from flask_cors import CORS
import json
from flask import Flask, jsonify, request

resultant_matrix = joblib.load('SVDMovie.pkl')
movies_list = pd.read_csv("MovieList.csv")
movies_names = joblib.load('MovieNames.pkl')

corr_mat = np.corrcoef(resultant_matrix)
movies_list = movies_list['0'].tolist()

def filterScore(record,keys):
    if('score' not in keys):
        return 0.95
    elif(type(record['score']) == 'str'):
        score = float(record['score'])
    else:
        score = record['score']
    if(score>0.99):
        return 0.95
    else: 
        return score
def filterLimit(record,keys):
    print("RECORD:::",type(record['limit']))
    if('limit' not in keys):
	    return 5
    elif(type(record['limit']) == 'int'):
	    return record['limit']
    else:
        return int(record['limit'])

def sortAccordingToScore(x_limit, corr_movie_index):
    buffer = np.column_stack((movies_names[x_limit], corr_movie_index[x_limit]))
    buffer = sorted(buffer,key=lambda x: x[1], reverse=True)
    final_list = []
    for i in range (0,len(buffer)):
        final_list.append(buffer[i][0])
    return final_list

def getMovieRecommendationList(input_movie,score,limit): #function to clean the word of any punctuation or special characters
    movie_index = movies_list.index(input_movie)
    print(movie_index)
    corr_movie_index = corr_mat[movie_index]
    #corr_movie_index.sort(reverse = True)
    x_limit = (corr_movie_index>=score) & (corr_movie_index<1.0)
    movie_recommendation_list = sortAccordingToScore(x_limit, corr_movie_index)#list(movies_names[(corr_movie_index>=score) & (corr_movie_index<1.0) ])
    if(len(movie_recommendation_list) > limit):
        return movie_recommendation_list[:limit]
    else:
        return movie_recommendation_list

app = Flask(__name__)
CORS(app) #any url can access this
#app.config['CORS_HEADERS'] = 'Content-Type'
@app.route('/movieBuff/recommendations/', methods=['POST'])
def getParentCategory():
    record = json.loads(request.data)
    input_movie = record['movie_name']
    keys =  record.keys()
    #score = filterScore(record,keys)
    #limit = filterLimit(record,keys)
    #print("filtered score",score)
    if('score' in keys and record['score']<0.99):
	    score = float(record['score'])
    else:
	    score = 0.95

    if('limit' in keys):
	    limit = int(record['limit'])
    else:
	    limit = 5
    movie_recommendation_list = getMovieRecommendationList(input_movie,score,limit)
    print(movie_recommendation_list)
    res = {
    'input_movie' : input_movie, 
    'movie_recommendation_list' : movie_recommendation_list
	}
    #print(prediction[0])
    return res


app.run(host = 'localhost', port = 8088, debug = True)