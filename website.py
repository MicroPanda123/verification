from flask import Flask, make_response, request, url_for, redirect, flash, session, jsonify, send_from_directory
import random
import token_manager_lib
import os

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    return "Dupa"

@app.route('/accesscodes', methods=['GET', 'POST'])
def accesscodes():
    if request.method == 'POST':
        user_nick = request.form.get('user_nick', False)
        file = request.files['file']
        if 'file' in request.files:
            res = make_response('<meta http-equiv="refresh" content="1" />')
            print("File found")
            flash("File found")
            filename = file.filename
            file.save(f'files/{filename}')
            res.set_cookie('user_nick', value=user_nick)
            res.set_cookie('key_file', value=f'files/{filename}')
            return res
    if request.cookies.get('user_nick') and request.cookies.get('key_file'):
        codes, timer = token_manager_lib.GetCodeDatabase(request.cookies.get('user_nick'), request.cookies.get('key_file'))
        return '''<meta http-equiv="refresh" content="2" />
        Current code: {} <br>
        Left time: {} <br>
        <button onclick="window.location.href='/cleardata';")">Clear data</button>
        '''.format(str(codes), str(timer))
    return '''
    <!doctype html>
    <h1>Upload data</h1>
    <form method='POST' enctype=multipart/form-data>
    <p><input type=text name=user_nick>
    <p><input type=file name=file>
    <p><input type=submit value=submit>
    </form>'''

@app.route('/VerCode', methods=['GET', 'POST'])
def verifyCode():
    print("Received")
    if request.method == 'POST':
        print("Post")
        user_nick = request.form['user_nick']
        code = request.form['code']
        connection = token_manager_lib.connect()
        cursor = connection.cursor()
        cursor.execute(f"select key_file from tokens where user_key='{user_nick}';")
        key_file = cursor.fetchall()
        key_file = key_file[0][0]
        codes, _ = token_manager_lib.GetCodeDatabase(user_nick, key_file)
        if int(code) == int(codes):
            data = {'accept': True}
        else:
            data = {'accept': False}
        print("DUPAAAAA")
        return jsonify(data)

@app.route('/NewToken', methods=['GET', 'POST'])
def newToken():
    if request.method == 'POST':
        user_nick = request.form['user_nick']
        token, keyfile = token_manager_lib.EncryptToken(token_manager_lib.RandNewToken())
        return token_manager_lib.InsertToken(user_nick, token=token, keyfile=keyfile)
        send_from_directory(keyfile)
    return '''
    <!doctype html>
    <h1>Upload data</h1>
    <form method='POST' enctype=multipart/form-data>
    <p><input type=text name=user_nick>
    <p><input type=submit value=submit>
    </form>'''

@app.route('/RemToken', methods=['GET', 'POST'])
def remToken():
    if request.method == 'POST':
        user_nick = request.form['user_nick']
        code = request.form['code']
        connection = token_manager_lib.connect()
        cursor = connection.cursor()
        cursor.execute(f"select key_file from tokens where user_key='{user_nick}';")
        key_file = cursor.fetchall()
        key_file = key_file[0][0]
        codes, _ = token_manager_lib.GetCodeDatabase(user_nick, key_file)
        if int(code) == int(codes):
            cursor.execute(f"delete from tokens where user_key='{user_nick};'")
            connection.commit()
            return "Success"
        else:
            return "Invalid code"

@app.route('/cleardata')
def cleardata():
    res = make_response(redirect(url_for('accesscodes')))
    res.set_cookie('user_nick', value='', max_age=0)
    res.set_cookie('key_file', value='', max_age=0)
    return res

app.run(host='0.0.0.0')
