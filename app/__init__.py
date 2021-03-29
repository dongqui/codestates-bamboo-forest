from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from os import environ


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bamboo.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

PASSWORD = environ.get('password')


class Post(db.Model, SerializerMixin):

    __tablename__ = 'post'

    id = db.Column(db.Integer(), nullable=False, primary_key=True)
    content = db.Column(db.VARCHAR(), nullable=True)
    preview = db.Column(db.VARCHAR(), nullable=True)


@app.before_request
def hook():
    if request.endpoint != 'password' and \
            request.cookies.get('password') != PASSWORD and \
            request.endpoint != 'static':
        return redirect(url_for('password'))


@app.route('/', methods=['GET'])
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/help', methods=['GET'])
def help_page():
    return render_template('help.html')


@app.route('/post', methods=['POST'])
def post():
    content = request.json['content']
    preview = content
    newPost = Post(content=content, preview=preview)
    db.session.add(newPost)
    db.session.commit()

    return jsonify(newPost.to_dict()), 201


@app.route('/password', methods=['GET', 'POST'])
def password():
    if request.method == 'GET':
        return render_template('password.html')

    password = request.json['password']

    if password != PASSWORD:
        return 'Invalid', 403

    response = make_response('success')
    response.set_cookie('password', password)
    return response


if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    app.run()
