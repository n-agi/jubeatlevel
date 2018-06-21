import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import requests, json, sys

DATABASE = '/var/www/wsgi/db'
LOGFILE = "/var/www/wsgi/log"
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
lv_9_table = [0, 6, 11, 19, 20, 20, 24, 27, 36, 31, 23, 19, 11, 11, 9, 2, 1]
lv_10_table = [0, 14, 18, 16, 20,0, 21,0, 17,0, 15,0, 14,0, 16,0, 17,0, 11,0, 5]
MAX_SCORE = 2731.08
ALL_EXC_SCORE = MAX_SCORE + 3.0
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])
    
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def hello_world():
    data = []
    stats = {}
    cursor = g.db.execute("select count(*) from log where score > 2700")
    d = cursor.fetchone()
    stats["challenger"] = d[0]
    cursor = g.db.execute("select count(*) from log where score > 2610 and score <= 2700")
    d = cursor.fetchone()
    stats['master'] = d[0]
    cursor = g.db.execute("select count(*) from log where score > 2325 and score <= 2610")
    d = cursor.fetchone()
    stats['diamond'] = d[0]
    cursor = g.db.execute("select count(*) from log where score > 1900 and score <= 2325")
    d = cursor.fetchone()
    stats['platinum'] = d[0]
    cursor = g.db.execute("select count(*) from log where score > 1500 and score <= 1900")
    d = cursor.fetchone()
    stats['gold'] = d[0]
    cursor = g.db.execute("select count(*) from log where score > 1200 and score <= 1500")
    d = cursor.fetchone()
    stats['silver'] = d[0]
    cursor = g.db.execute("select count(*) from log where score >= 1000 and score <= 1200")
    d = cursor.fetchone()
    stats['bronze'] = d[0]
    cursor = g.db.execute("select * from log order by score desc")
    d = cursor.fetchall()
    for a in d:
        data.append({"uid":a[0] ,"nickname":a[1], "score":a[3], "tier":a[2]})
    return render_template('main.html', data=data,stats=stats)
@app.route('/search',methods=['POST'])
def red():
    if request.method == 'POST':
        url = 'user/' + request.form['uid']
        return redirect('https://nagi.moe/jp/%s'%(url))
    else:
        print request.method
@app.route('/user/')
def hello_world2():
    return render_template('main.html')
@app.route('/user/<uid>')
def make_profile(uid=None):
    uid = uid.lower()
    data = {}
    diff_data = {}
    url = 'https://qubellinfo.com/%s/api' % (uid)
    req = requests.get(url).text
    req = json.loads(req)
    score = 0.0
    try:
        if req['result'] is not None:
            return render_template('profile.html')
    except:
        pass
    data['nickname'] = req['nickname']
    cursor = g.db.execute("select * from difficulty where difficulty>=9")
    diff_table = cursor.fetchall()
    avgs_9 = {10:0,11:0, 12:0, 13:0, 14:0, 15:0, 16:0}
    avgs_10 = {10:0, 12:0, 14:0, 16:0, 18:0, 20:0}
    processed_9 = {10:0, 11:0,12:0,13:0,14:0,15:0,16:0}
    processed_10 = {10:0,12:0,14:0,16:0,18:0,20:0}
    blanks = []
    cnt = [0,0,0,0,0,0,0,0,0,0,0]
    pre_sum=[0,0]
    pre_calced=[0,0]
    for diff in diff_table:
        actual_diff = diff[1]
        try:
            my_score = req['musics'][str(diff[0])]["ext"]["score"]
            if my_score >= 990000:
                if actual_diff == 9:
                    cnt[9] += 1
                    pre_sum[0] += my_score
                    pre_calced[0] += 1
                elif actual_diff == 10:
                    cnt[10] += 1
                    pre_sum[1] += my_score
                    pre_calced[1] += 1
        except:
            pass
    print cnt[9] , cnt[10]
    print pre_sum[0] / pre_calced[0]
    print pre_sum[1] / pre_calced[1]
    if (cnt[9] < 20 and cnt[9] * 2 < cnt[10]) or pre_sum[1] / pre_calced[1] == 1000000:
        level_10_user = True
    else:
        level_10_user = False
    for diff in diff_table:
        try:
            my_score = req['musics'][str(diff[0])]["ext"]["score"]
            diff_y = diff[2]
            diff_x = diff[3]
            if my_score <= 0:
                if(diff[1] == 9 and level_10_user == True):
                    print "wow2"
                    if diff_y % 2 == 1:
                        diff_y += 3
                    blanks.append([diff[0], 10, diff_y, -1])
                else:
                    print "not found"
                    blanks.append(diff)
                continue
            if(diff[1] == 9):
                table = lv_9_table
                avgs = avgs_9
                processed = processed_9
            elif(diff[1] == 10):
                table = lv_10_table
                avgs = avgs_10
                processed = processed_10
            avgs[diff_y] += my_score
            processed[diff_y] += 1
            score += (float(my_score) / 1000000 * (float(diff_y) + float(table[diff_y] - diff_x) / float(table[diff_y]) ))
        except:
            if(diff[1] == 9 and level_10_user == True):
                print "wow"
                if diff_y % 2 == 1:
                    diff_y += 3
                blanks.append([diff[0], 10, diff_y, -1])
            else:
                blanks.append(diff)
            pass
    for blank in blanks:
        print blank
        diff_y = blank[2]
        diff_x = blank[3]
        if diff_x == -1 and diff_y < 10:
            diff_y = 10
        if(blank[1] == 10):
            table = lv_10_table
            avgs = avgs_10
            processed = processed_10
        elif(blank[1] == 9):
            table = lv_9_table
            avgs = avgs_9
            processed = processed_9
        if processed[diff_y] == 0:
            print "not processed wtf"
            continue
        my_score = float(avgs[diff_y]) / processed[diff_y]
        if diff_x == -1:
            score += (float(my_score) / 1000000 * (float(diff_y) - 0.6 ))
        else:
            score += (float(my_score) / 1000000 * (float(diff_y) + (float(table[diff_y] - diff_x) / float(table[diff_y])) ))
    score = round(score, 2)
    if score >= 1800.0:
        delta = (score - 1800.0) ** 1.3333
    else:
        delta = 0.0
    score = round(delta+1000,2)
    if score >= MAX_SCORE:
        print pre_sum[1] / pre_calced[1]
        if((pre_sum[1] / pre_calced[1]) > 999900):
            score = MAX_SCORE
        else:
            score = MAX_SCORE - float((pre_sum[1] / pre_calced[1])%100/20.0)
    if(pre_sum[1] / pre_calced[1] == 1000000):
        score = MAX_SCORE
        if(pre_sum[0] / pre_calced[0] == 1000000):
            score += 3.0
    score = round(score, 2)
    if(score == ALL_EXC_SCORE):
        tier = "EXCELLENT MASTER"
        img = "challenger_1.png"
    elif(score == MAX_SCORE):
        tier = "LEVEL 10 MASTER"
        img = "challenger_1.png"
    elif(score > 2700):
        tier = "Challenger I"
        img = "challenger_1.png"
    elif(score > 2610):
        tier = "Master I"
        img = "master_1.png"
    elif(score > 2575):
        tier = "Diamond I"
        img = "diamond_1.png"
    elif(score > 2525):
        tier = "Diamond II"
        img = "diamond_1.png"
    elif(score > 2475):
        tier = "Diamond III"
        img = "diamond_1.png"
    elif(score > 2425):
        tier = "Diamond IV"
        img = "diamond_1.png"
    elif(score > 2325):
        tier = "Diamond V"
        img = "diamond_1.png"
    elif(score > 2275):
        tier = "Platinum I"
        img = "platinum_1.png"
    elif(score > 2200):
        tier = "Platinum II"
        img = "platinum_1.png"
    elif(score > 2125):
        tier = "Platinum III"
        img = "platinum_1.png"
    elif(score > 1975):
        tier = "Platinum IV"
        img = "platinum_1.png"
    elif(score > 1900):
        tier = "Platinum V"
        img = "platinum_1.png"
    elif(score > 1800):
        tier = "Gold I"
        img = "gold_1.png"
    elif(score > 1750):
        tier = "Gold II"
        img = "gold_1.png"
    elif(score > 1675):
        tier = "Gold III"
        img = "gold_1.png"
    elif(score > 1600):
        tier = "Gold IV"
        img = "gold_1.png"
    elif(score > 1500):
        tier = "Gold V"
        img = "gold_1.png"
    elif(score > 1450):
        tier = "Silver I"
        img = "silver_1.png"
    elif(score > 1400):
        tier = "Silver II"
        img = "silver_1.png"
    elif(score > 1350):
        tier = "Silver III"
        img = "silver_1.png"
    elif(score > 1300):
        tier = "Silver IV"
        img = "silver_1.png"
    elif(score > 1200):
        tier = "Silver V"
        img = "silver_1.png"
    elif(score > 1000):
        tier = "Bronze"
        img = "bronze_1.png"
    else:
        tier = "Unranked"
        img = "bronze_1.png"
    query = "insert or replace into log(uid, nickname, score, tier) values(?,?, ?, ?)"
    g.db.execute(query, (uid, data['nickname'], score,tier))
    g.db.commit()
    return render_template('profile.html', data=data, score=score, img=url_for('static',filename=img),tier=tier)
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False,port=9091)
