# -*- coding: utf-8 -*-
from flask import Flask, request, render_template


app = Flask(__name__)

@app.route('/')
def index():
    import MySQLdb
    db=MySQLdb.connect(host='localhost',user='root',passwd='g1vnd3',db='test',port=3306)
    db.set_character_set('utf8')
    cursor = db.cursor()
    cursor.execute("select id,title from dumpArticles limit 0,10")
    data = cursor.fetchall()
    artLi=[]
    for i in data:
        artTemp=[]
        artTemp.append(str(i[0]))
        artTemp.append(i[1].decode("utf-8"))
        artLi.append(artTemp)
    print artLi
    db.close()
    return render_template('index.html',article=artLi)

@app.route('/<id>')
def article(id):
    import MySQLdb
    db=MySQLdb.connect(host='localhost',user='root',passwd='g1vnd3',db='test',port=3306)
    db.set_character_set('utf8')
    cursor = db.cursor()
    cursor.execute("select * from dumpArticles WHERE id="+id)
    data = cursor.fetchone()
    article=data[1].decode('utf-8').split('\\n')
    title=data[2].decode('utf-8')
    db.close()
    return render_template('article.html',title=title,article=article)

if __name__ == '__main__':
    app.run(debug=True)
