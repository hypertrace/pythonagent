from flask import Flask
import mysql

app = Flask(__name__)

def connect_to_mysql():
    return mysql.connector.connect(database='test',
                                  username='root',
                                  password='root',
                                  host='localhost',
                                  port=3306)

cnx = connect_to_mysql()

def get_mysql_current_date() -> str:
    cursor = cnx.cursor()
    query = "SELECT CURDATE()"
    cursor.execute(query)
    current_time = cursor.fetchone()
    cursor.close()
    return current_time[0]

@app.route('/')
def hello_world():
    current_date = get_mysql_current_date()
    return f'Hello World. Today is {current_date}!'
