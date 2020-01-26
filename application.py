from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import json
# from datetime import datetime
import math

application = Flask(__name__)

quiz_result = """{
    "name" : "Aman",
    "colors" : [
    [124,104,3],[124,124,35],[124,24,35]
        
        ]}"""


min_score = np.array([0,0,0])
max_score = np.array([255,255,255])

color_attributes = ["R", "G", "B"]
@application.route('/', methods=['POST'])
def func():
    if request.method == 'POST':
        data = request.get_data(as_text=True)
        return jsonify(get_recomendations(data)), 201
    else:
        return jsonify({"data": "improper request"})


def get_recomendations(input):
    data = json.loads(input)
    excelFile = 'colors.csv'
    colors = pd.read_csv(excelFile)
    feedback = np.array(data['colors'])

    mean = np.mean(feedback, axis=0)

    color_list=get_colors(colors)
    def get_similarity(id):
        result_vector = mean
        vec1 = result_vector
        vec2 = get_color_vectors(id, color_list, color_attributes)
        similarity = cosine_similarity(vec1, vec2)
        return similarity

    color_list['score'] = color_list.hex.apply(get_similarity)
    sorted = color_list.sort_values(by='score', ascending=0).reset_index(drop=True)
    recommendation = (sorted[['s_color', 'hex','score']].head())
    rec = np.array(recommendation).tolist()
    print(rec)
    result_data = {


        "Name": data['name'],
        "Type": "KBR",
        "recommendedColors": rec,
    }

    return result_data

def cosine_similarity(v1, v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i];
        y = v2[i]
        sumxx += x * x
        sumyy += y * y
        sumxy += x * y
    return sumxy / math.sqrt(sumxx * sumyy)

def get_colors(wines):
    i = 0
    for attribute in color_attributes:
        wines[attribute] = pd.to_numeric(wines[attribute])
        x = wines[attribute].values.reshape(-1, 1)
        min_vec = np.empty(x.size)
        l = min_score.item(i)
        h = max_score.item(i)
        min_vec.fill(l)
        max_vec = np.empty(x.size)
        max_vec.fill(h)
        x_scaled = (x - min_vec) / (max_vec - min_vec)
        wines[attribute] = pd.Series(x_scaled[:, 0])
        i += 1
    return wines

def get_color_vectors(id, wines, wine_attrs):
    wine = wines[wines['hex'] == id]
    wine_vector = np.array(wine[wine_attrs].values.tolist()).flatten()
    return wine_vector

if __name__ == "__main__":
    application.run(debug=True)
