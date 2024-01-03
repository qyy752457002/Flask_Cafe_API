from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from dotenv import load_dotenv
import os

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)

# Load environment variables from .env file
load_dotenv() 

# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # 将当前 Cafe 类 实例对象 中 的属性 转换 成 一个 字典 去 存储
    def to_dict(self):
        # Method 1
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry:
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        '''
        {'id': 1, 'name': 'Cafe1', 'map_url': 'URL1', 'img_url': 'IMG1', ..., 'coffee_price': '$5'}
        '''
        return dictionary

        # Method 2
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

# HTTP GET - Read Record
@app.route("/random", methods = ["GET"])
def get_random_cafe():
    
    query = db.select(Cafe)
    result = db.session.execute(query)

    '''
        [ Cafe(id=1, name='Cafe1', map_url='URL1', img_url='IMG1', ..., coffee_price='$5'),
          Cafe(id=2, name='Cafe2', map_url='URL2', img_url='IMG2', ..., coffee_price='$6'),
          Cafe(id=3, name='Cafe3', map_url='URL3', img_url='IMG3', ..., coffee_price='$7') ]
    '''
    # 返还一个数组 all_cafes
    # 每一行 对应 Cafe表中 的每一行数据
    all_cafes = result.scalars().all()

    '''
        Cafe(id=1, name='Cafe1', map_url='URL1', img_url='IMG1', ..., coffee_price='$5')
    '''
    # 随机选一个cafe
    random_cafe = random.choice(all_cafes)

    # 将 Cafe类 的 实例对象 random_cafe 转换成 字典
    # 对 字典 做 序列化 
    # 返还给 客户端

    '''
    {
        "cafe": {
            "can_take_calls": true,
            "coffee_price": "200",
            "has_sockets": true,
            "has_toilet": true,
            "has_wifi": true,
            "id": 1,
            "img_url": "https://gist.github.com/",
            "location": "Shanghai",
            "map_url": "https://www.google.com",
            "name": "Tim",
            "seats": "Chair"
            }
    }
    
    '''
    return jsonify(cafe = random_cafe.to_dict())

@app.route("/all", methods = ["GET"])
def get_all_cafes():

    query = db.select(Cafe).order_by(Cafe.name)
    result = db.session.execute(query)

    '''
        [ Cafe(id=1, name='Cafe1', map_url='URL1', img_url='IMG1', ..., coffee_price='$5'),
          Cafe(id=2, name='Cafe2', map_url='URL2', img_url='IMG2', ..., coffee_price='$6'),
          Cafe(id=3, name='Cafe3', map_url='URL3', img_url='IMG3', ..., coffee_price='$7') ]
    '''
    # 返还一个数组 all_cafes
    # 每一行 对应 Cafe表中 的每一行数据
    all_cafes = result.scalars().all()

    # 遍历 all_cafes 数组 中的 每一个 Cafe 实例对象
    # 将 实例对象 cafe 转换成 字典
    # 对 字典 做 序列化 
    # 返还给 客户端
    '''
    {
       "cafes": [
                    {
                        "can_take_calls": true,
                        "coffee_price": "200",
                        "has_sockets": true,
                        "has_toilet": true,
                        "has_wifi": true,
                        "id": 1,
                        "img_url": "https://gist.github.com/",
                        "location": "Shanghai",
                        "map_url": "https://www.google.com",
                        "name": "Tim",
                        "seats": "Chair"
                    }
                ]
    }
    '''
    return jsonify(cafes = [cafe.to_dict() for cafe in all_cafes])

@app.route("/search", methods = ["GET"])
def get_cafe_at_location():

    # 从用户输入的route (ex. /search?loc=Peckham) 中 获取 loc 参数 的 值
    query_location = request.args.get("loc")
    query = db.select(Cafe).where(Cafe.location == query_location)
    result = db.session.execute(query)
     # Note, this may get more than one cafe per location
    all_cafes = result.scalars().all()
    # 遍历 all_cafes 数组 中的 每一个 Cafe 实例对象
    # 将 实例对象 cafe 转换成 字典
    cafes = [cafe.to_dict() for cafe in all_cafes]

    '''
    {
        "error": {
            "Not Found": "Sorry, we don't have a cafe at that location."
        }
    }
    '''
    return jsonify(cafes = cafes) if cafes else jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():

    # 对 Cafe 对象 做实例化
    # 建立 new_cafe 实例
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )

    # 加入 Cafe 表
    db.session.add(new_cafe)
    # 提交即保存到数据库:
    db.session.commit()

    '''
    {
        "response": {
            "success": "Successfully added the new cafe."
        }
    }   
    '''
    return jsonify(response={"success": "Successfully added the new cafe."})

# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):

    '''
    http://127.0.0.1:5000/update-price/CAFE_ID?new_price=£5.67
    '''
    new_price = request.args.get("new_price")

    # 从数据库 Cafe 表 中 获取 对应 该 cafe id 的 cafe 实例对象

    # 或者使用 cafe = db.get_or_404(Cafe, cafe_id)
    cafe = db.session.get(Cafe, cafe_id)

    # 如果该 cafe 实例对象 存在
    if cafe:
        # 更新 该 cafe 实例对象 当中 的 price 属性
        cafe.coffee_price = new_price 
        # 提交即保存到数据库
        db.session.commit()

        '''
        {
            "response": {
                "success": "Successfully updated the price."
                }
        }
        '''

        ## Just add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        #404 = Resource not found
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

# HTTP DELETE - Delete Record
    
# Deletes a cafe with a particular id. Change the request type to "Delete" in Postman
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):

    '''
    http://127.0.0.1:5000/report-closed/1?api-key=qyy2614102
    '''

    api_key = request.args.get("api-key")
    if api_key == os.environ.get('TopSecretAPIKey'):
        # 从数据库 Cafe 表 中 获取 对应 该 cafe id 的 cafe 实例对象
        cafe = db.get_or_404(Cafe, cafe_id)

        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403
    
if __name__ == '__main__':
    app.run(debug=True)
