"""
The flask application package.
"""

from flask import Flask, request, render_template, jsonify
import os
import sqlite3
import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

PEOPLE_FOLDER = os.path.join('static', 'images')

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir, 'ex.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

db = sqlite3.connect(os.path.join(basedir, 'ex.db'), check_same_thread=False)


@app.route('/images',methods=["GET"])
def getImageOfItem():
    q = request.args.get('image_id',default=1,type=int)
    try:
        file = open(os.path.join(os.getcwd(),"API",app.config['UPLOAD_FOLDER'], str(q)+".jpg"),'r')
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], str(q)+".jpg")
        
    except:
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], "16.png")
    return render_template("show_image.html",user_image=full_filename)

@app.route('/app/item',methods=["GET"])
def getItems():
    q = request.args.get('item_id',default=1,type=int)
    cursor = db.execute("select * from lots where id = "+str(q)+";");
    rv = cursor.fetchall()
    keyword = {}
    keyword["count"] = len(rv)
    keyword["data"] = []
    for row in rv:
        id = row[0]
        title = row[1]
        desc = row[2]
        price = row[3]
        weight = row[4]
        section = row[5]
        keyword["data"].append({"id" : id, "title" : title, "desc" : desc, "price" : price, "weight" : weight, "section" : section})
    cursor.close()
    return jsonify(keyword)

@app.route('/app/items',methods=["GET"])
def getItem():
    q = request.args.get('section_code',default=1,type=int)
    if q == 1:
        cursor = db.execute("select * from lots order by section;");
    else:
        cursor = db.execute("select * from lots where section = "+str(q)+";");
    rv = cursor.fetchall()
    keyword = {}
    keyword["count"] = len(rv)
    keyword["data"] = []
    for row in rv:
        id = row[0]
        title = row[1]
        desc = row[2]
        price = row[3]
        weight = row[4]
        section = row[5]
        keyword["data"].append({"id" : id, "title" : title, "desc" : desc, "price" : price, "weight" : weight, "section" : section})
    cursor.close()
    return jsonify(keyword)


@app.route('/user/get',methods=["GET"])
def getUserInfo():
    user = request.args.get('user',default=1,type=int)
    query = "select * from user_shop where id = " + str(user) + ";";
    cursor = db.execute(query)
    rv = cursor.fetchall()
    keyword = {}
    keyword["count"] = len(rv)
    keyword["data"] = []
    for row in rv:
        id = row[0]
        first_name = row[1]
        email = row[2]
        phone = row[3]
        keyword["data"].append({"id" : id, "first_name" : first_name, "email" : email , "phone" : phone})
    cursor.close()
    return jsonify(keyword)

@app.route('/basket/get',methods=["GET"])
def getBasketOrders():
    user = request.args.get('user',default=1,type=int)
    query = "select * from basket where id_user = " + str(user) + ";"
    cursor = db.execute(query)
    rv = cursor.fetchall()
    keyword = {}
    keyword["count"] = len(rv)
    keyword["data"] = []
    for row in rv:
        id_user = row[0]
        item = row[1]
        count = row[2]
        keyword["data"].append({item:{"count" : count}})
    cursor.close()
    return jsonify(keyword)


@app.route('/basket/set',methods = ["GET"])
def addIntoBasketOrders():
    user = request.args.get('user_id',default=1,type=int)
    item = request.args.get('item_id',default=1,type = int)
    count = request.args.get('count',default=1,type=int)
    keyword = {}
    query = "select * from user_shop where id = {};".format(user)
    cursor = db.execute(query)
    rv = cursor.fetchall()
    if len(rv) == 0:
        keyword["status"] = 0
        return jsonify(keyword)
    query = "select * from basket where id_user = {} and id_item = {};".format(user,item)
    cursor = db.execute(query)
    rv = cursor.fetchall()
    if(len(rv) == 0):
        query = "insert into basket values({},{},{});".format(user,item,count)
    else:
        query = "update basket set count = {} where id_user = {} and id_item = {};".format(count,user,item)
    cursor.close()
    cursor = db.execute(query)
    cursor.close()
    keyword["status"] = 1
    return jsonify(keyword)


def isEmPhIsAlreadyExists(email,phone):
    keyword = {"phone":phone}
    query = "select * from user_shop where {} = {};"
    for key in keyword.keys() :
        cursor = db.execute(query.format(key,keyword[key]))
        rv = cursor.fetchall()
        cursor.close()
        if (len(rv) > 0):
            return True;
    return False;


@app.route('/user/add',methods = ["GET"])
def createUser():
    first_name = request.args.get('first_name',default="Anonimus",type=str)
    email = request.args.get('email',default="error@error.error",type=str)
    phone = request.args.get('phone',default="111111111",type=int)
    keyword = {}
    if isEmPhIsAlreadyExists(email,phone):
        keyword["status"] = 0
    else:
        query = "insert into user_shop values(NULL,'{}','{}',{});"
        cursor = db.execute(query.format(first_name,email,phone))
        cursor.close()
        keyword["status"] = 1
    return jsonify(keyword)

@app.route('/user/login',methods=["GET"])
def loginUser():
    user = request.args.get("user",type=int)
    query = "select * from user_shop where id = {};".format(user)
    cursor = db.execute(query)
    rv = cursor.fetchall()
    keyword = {}
    if(len(rv)>0):
        keyword["status"] = 1
    else:
        keyword["status"] = 0
    cursor.close()
    return jsonify(keyword)


@app.route('/orders/get', methods=["GET"])
def getOrdersForUser():
    user = request.args.get('user', default = 1 , type=int)
    query_1 = "select * from orders_users where user_id = {};"
    query_2 = "select * from orders_items where id_order = {};"
    query_3 = "select * from lots where id = {};"
    result = {};
    cursor = db.execute(query_1.format(user))
    rv = cursor.fetchall()
    result["count"] = len(rv)
    result["data"] = {}
    result["data"]["total"] = {}
    for row in rv:
        order = row[1]
        date = row[2]
        cursor_2 = db.execute(query_2.format(order))
        rv_2 = cursor_2.fetchall()
        if(len(rv_2) == 0):
            result["count"] = 0
            break
        result["data"][date] = {}
        for row_2 in rv_2:
            item = row_2[0]
            count = row_2[2]
            cursor_3 = db.execute(query_3.format(item))
            rv_3 = cursor_3.fetchall()
            total_summ = 0
            for row_3 in rv_3:
                id = row_3[0]
                title = row_3[1]
                desc = row_3[2]
                price = row_3[3]
                weight = row_3[4]
                price_total = int(price) * int(count) 
                total_summ = total_summ + price_total
                result["data"][date][id] = {"title" : title, "desc" : desc, "price" : price, "weight" : weight, "count" : count, "price_total" : price_total}
            cursor_3.close()
            result["data"]["total"][date] = total_summ
        cursor_2.close()
    cursor.close()
    return jsonify(result)



