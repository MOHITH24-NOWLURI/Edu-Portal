from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import errors

app = Flask(__name__)

DB_HOST = "127.0.0.1"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "Rishi@2003"

def connect_to_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def create_table():
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student(
            student_id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL,
            password TEXT NOT NULL,
            mobile_no VARCHAR(15) NOT NULL UNIQUE,
            student_email TEXT NOT NULL UNIQUE
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    id = data.get("student_id")
    name = data.get("student_name")
    password = data.get("password")
    mobile = data.get("mobile_no")
    email = data.get("email")

    if not id or not password or not name or not email or not mobile:
        return jsonify({"error": "Please provide sufficient details"}), 400

    connection = connect_to_db()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO student (student_id, student_name, password, mobile_no, student_email)
            VALUES (%s, %s, %s, %s, %s);
        """, (id, name, password, mobile, email))
        connection.commit()
    except errors.UniqueViolation:
        connection.rollback()
        return jsonify({"error": "Student details already exist"}), 400
    finally:
        cursor.close()
        connection.close()

    return jsonify({"message": "Student registered", "student_id": id})

@app.route("/view", methods=["GET"])
def view():
    data = request.json
    id = data.get("id")
    password = data.get("password")

    if not id or not password:
        return jsonify({"error": "Enter details correctly"}), 400

    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT student_id, student_name, mobile_no, student_email
        FROM student
        WHERE student_id = %s AND password = %s;
    """, (id, password))
    details = cursor.fetchall()
    cursor.close()
    connection.close()

    if not details:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify([
        {"Student_id": d[0], "Student_Name": d[1], "Mobile_no": d[2], "Email": d[3]}
        for d in details
    ])
@app.route("/update", methods = ["PUT"])
def update():
    id = request.json["student_id"]
    password = request.json["password"]

    if not id or not password:
        return jsonify({"error": "Enter details correctly"}), 400
    
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM student WHERE student_id=%s AND password=%s;""",(id,password))
    student = cursor.fetchall()
    if student:
        stid = request.json["new_id"]
        name = request.json["new_name"]
        password1 = request.json["new_password"]
        mobile = request.json["new_mobile"]
        email = request.json["new_email"]
        if not stid or not name or not password1 or not mobile or not email:
            return jsonify({
                "Message":"Fill all The Details"
            })

        cursor.execute("""
        UPDATE student
        SET student_id = %s, student_name = %s,password = %s,mobile_no = %s,student_email = %s
        WHERE student_id = %s;""", (stid,name,password1,mobile,email,id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({
            "Message":"Student Details Updated Successfully",
            "Student_id":stid,
            "Student_name":name,
            "Message":"Password Successfully Updated",
            "Student_Mobile":mobile,
            "Student_email":email
            })
    else :
        return jsonify({
            "Message":"Enter Valies Details"
        })

@app.route("/delete",methods = ["DELETE"])
def delete():
    id = request.json["student_id"]
    password = request.json["password"]

    if not id or not password:
        return jsonify({"error": "Enter details correctly"}), 400
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM STUDENT WHERE student_id=%s AND password = %s;""",(id,password))
    data = cursor.fetchall()
    if data:
        cursor.execute("""DELETE FROM student WHERE student_id=%s;""",(id,))
        connection.commit()
        return "Student Details Deleted Successfully"
    else :
        return "No student found with that ID"
if __name__ == "__main__":
    create_table()
    app.run(debug=True)
