import pandas as pd
import numpy as np
import json
import math

excelFile = 'C:/Users/AACER/PycharmProjects/untitled1/notebooks/teachers.xls'
teachers = pd.read_excel(excelFile)

quiz_result = """{
    "rollNumber" : "be/6002/15",
    "name" : "Aman",
    "preferences" : {
    "curosity" : "3",
    "patience" : "2",
    "extroversion" : "4",
    "speed" : "3",
    "agreebleness":"3"
    }
}"""

min_score = np.array([1, 1, 1, 1, 1])
max_score = np.array([5, 5, 5, 5, 5])
tr_attr = ['curosity', 'patience', 'extroversion', 'speed', 'agreebleness']


def get_result_vector(qr):
    d = json.loads(qr)
    r_attrs = tr_attr
    result = pd.io.json.json_normalize(d['preferences'], record_prefix=False)
    p = np.array(result[r_attrs].values.tolist()).flatten()
    p = ','.join(p)
    result_vector = np.fromstring(p, dtype=np.float, sep=',')

    result_vector = (result_vector - min_score) / (max_score - min_score)
    return result_vector


def get_teachers(wines):
    i = 0
    for attribute in tr_attr:
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


def get_teachers_vectors(id, wines, wine_attrs):
    wine = wines[wines['teacherId'] == id]
    wine_vector = np.array(wine[wine_attrs].values.tolist()).flatten()
    return wine_vector


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


def get_resId(qr):
    d = json.loads(qr)
    rid = d['rollNumber']
    return rid


def get_name(qr):
    d = json.loads(qr)
    rid = d['name']
    return rid


def get_recommendation(quiz_result):
    teacher_list = get_teachers(teachers)

    def get_similarity(id):
        result_vector = get_result_vector(quiz_result)
        vec1 = result_vector
        vec2 = get_teachers_vectors(id, teacher_list, tr_attr)
        similarity = cosine_similarity(vec1, vec2)
        return similarity

    teacher_list['score'] = teacher_list.teacherId.apply(get_similarity)
    sorted = teacher_list.sort_values(by='score', ascending=0).reset_index(drop=True)
    recommendation = (sorted[['Teacher', 'Subject', 'Medium', 'score']].head())
    rec = np.array(recommendation).tolist()

    result_data = {

        "rollNumber": get_resId(quiz_result),
        "Name": get_name(quiz_result),
        "Type": "KBR",
        "recommendedTeachers": rec,
    }

    return result_data


print(get_recommendation(quiz_result))