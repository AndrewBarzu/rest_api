from flask import Flask
from flask import request
from flask_restful import Resource, Api
from flask_cors import CORS
from threading import Lock
import pyodbc
import pandas as pd


app = Flask(__name__)
CORS(app)
api = Api(app)
mutex = Lock()

sql_conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-2096F3Q\SQLEXPRESS;'
                          'Database=UnihackDB;'
                          'Trusted_Connection=yes;', autocommit=True)

# engine = sal.create_engine("mssql+pyodbc://DESKTOP-2096F3Q\SQLEXPRESS/UnihackDB?driver=SQL Server?Trusted_Connection=yes")

class GetUserData(Resource):
    @staticmethod
    def get():
        uid = request.form["id"]
        print(request.form)
        try:
            mutex.acquire()
            sql_query = pd.read_sql_query("SELECT * FROM Users AS U WHERE U.id = " + '\'' + uid + '\'', sql_conn)
            mutex.release()
            if sql_query.size == 0:
                return pd.DataFrame({"code": ["100"]}).to_json()
            else:
                sql_query["code"] = "100"
            return sql_query.to_json()
        except Exception as e:
            print(e)
            return {"code": "400"}

class GetAllUsers(Resource):
    @staticmethod
    def get():
        try:
            mutex.acquire()
            sql_query = pd.read_sql_query("SELECT * FROM Users", sql_conn)
            mutex.release()
            if sql_query.size == 0:
                return pd.DataFrame({"code": ["100"]}).to_json()
            else:
                sql_query["code"] = "100"
            return sql_query.to_json()
        except Exception as e:
            print(e)
            return {"code": "400"}


class RegisterUser(Resource):
    @staticmethod
    def post():
        request_data = request.form
        print(request_data)
        # request_data = request_data.to_dict(flat=False)
        # print(request_data)
        # uid = request_data["uid"]
        # name = request_data["name"]
        # surname = request_data["surname"]
        # email = request_data["email"]
        # university = request_data["university"]
        # gender = request_data["gender"]
        # date_of_birth = request_data["date_of_birth"]
        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''INSERT INTO Users (id, name, surname, email, university) VALUES (?, ?, ?, ?, ?)''',
                           *request_data.values())
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class UpdateUser(Resource):
    @staticmethod
    def post():
        request_data = request.form
        print(request_data)
        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''UPDATE Users SET name = ?, surname = ?, email = ?, university = ? WHERE id = ?''',
                           request_data["name"], request_data["surname"], request_data["email"], request_data["university"], request_data["id"])
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class GetGroupsOfUser(Resource):
    @staticmethod
    def get():
        uid = request.form["id"]
        try:
            mutex.acquire()
            sql_query = pd.read_sql_query("SELECT G.id, G.name, G.description FROM Groups AS G"
                                          " INNER JOIN Members as M ON G.id = M.gid"
                                          " WHERE M.uid = " + '\'' + uid + '\'', sql_conn)
            mutex.release()
            if sql_query.size == 0:
                return pd.DataFrame({"code": ["100"]}).to_json()
            else:
                sql_query["code"] = "100"
            return sql_query.to_json()
        except Exception as e:
            print(e)
            return {"code": "400"}

class GetMembers(Resource):
    @staticmethod
    def get():
        group_id = request.form["gid"]
        try:
            mutex.acquire()
            sql_query = pd.read_sql_query("SELECT U.id, U.name, U.surname, U.email, U.university, M.is_admin FROM Users AS U"
                                          " INNER JOIN Members AS M ON M.uid = U.id"
                                          " WHERE M.gid = " + '\'' + group_id + '\'', sql_conn)
            mutex.release()
            if sql_query.size == 0:
                return pd.DataFrame({"code": ["100"]}).to_json()
            else:
                sql_query["code"] = "100"
            return sql_query.to_json()
        except Exception as e:
            print(e)
            return {"code": "400"}

class DeleteUser(Resource):
    @staticmethod
    def post():
        user_id = request.form["id"]
        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''DELETE FROM Users WHERE id = ?''', user_id)
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class CreateGroup(Resource):
    @staticmethod
    def post():
        request_data = request.form
        user_id = request_data["id"]
        name = request_data["name"]
        description = request_data["description"]
        try:
            print(name, description)
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''INSERT INTO Groups (name, description) VALUES (?, ?)''', name, description)

            cursor.execute('''SELECT id=@@IDENTITY''')
            group_id = cursor.fetchone().id

            cursor.execute('''INSERT INTO Members (uid, gid, is_admin) VALUES (?, ?, ?)''',
                           user_id, group_id, 1)
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class DeleteGroup(Resource):
    @staticmethod
    def post():
        request_data = request.form
        user_id = request_data["uid"]
        group_id = request_data["gid"]
        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''EXECUTE delete_group ?, ?''', user_id, group_id)
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class AddUserToGroup(Resource):
    @staticmethod
    def post():
        request_data = request.form
        user_id = request_data["uid"]
        group_id = request_data["gid"]
        other_uid = request_data["other_uid"]
        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''EXECUTE add_member_to_group ?, ?, ?''', user_id, group_id, other_uid)
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class RemoveUserFromGroup(Resource):
    @staticmethod
    def post():
        request_data = request.form
        user_id = request_data["uid"]
        group_id = request_data["gid"]
        other_uid = request_data["other_uid"]
        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''EXECUTE remove_member_from_group ?, ?, ?''', user_id, group_id, other_uid)
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class AddReminder(Resource):
    @staticmethod
    def post():
        request_data = request.form
        user_id = request_data["id"]
        description = request_data["description"]
        try:
            if len(description) == 0:
                raise Exception("Empty description")
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''INSERT INTO Reminders (description, uid) VALUES (?, ?)''', description, user_id)
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class DeleteReminder(Resource):
    @staticmethod
    def post():
        request_data = request.form
        user_id = request_data["uid"]
        reminder_id = request_data["rid"]
        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''DELETE FROM Reminders WHERE uid = ? and id = ?''', user_id, reminder_id)
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class GetReminders(Resource):
    @staticmethod
    def get():
        request_data = request.form
        user_id = request_data["uid"]
        try:
            mutex.acquire()
            sql_query = pd.read_sql_query("SELECT id, description FROM Reminders WHERE uid = " + '\'' + user_id + '\'', sql_conn)
            mutex.release()
            if sql_query.size == 0:
                return pd.DataFrame({"code": ["100"]}).to_json()
            else:
                sql_query["code"] = "100"
            print(sql_query)
            return sql_query.to_json()
        except Exception as e:
            print(e)
            return {"code": "400"}

class AddPost(Resource):
    @staticmethod
    def post():
        request_data = request.form
        user_id = request_data["uid"]
        group_id = request_data["gid"]
        title = request_data["title"]
        body = request_data["body"]
        post_time = request_data["post_time"]

        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''INSERT INTO Posts (gid, uid, title, body, post_time) VALUES (?, ?, ?, ?, ?)''',
                           group_id, user_id, title, body, post_time)
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class DeletePost(Resource):
    @staticmethod
    def post():
        request_data = request.form
        user_id = request_data["uid"]
        post_id = request_data["pid"]

        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''DELETE FROM Posts WHERE uid = ? and id = ?''',
                           user_id, post_id)
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class GetPosts(Resource):
    @staticmethod
    def get():
        request_data = request.form
        group_id = request_data["gid"]

        try:
            mutex.acquire()
            sql_query = pd.read_sql_query("SELECT * FROM Posts WHERE gid = " + '\'' + group_id + '\'',
                                          sql_conn)
            mutex.release()
            if sql_query.size == 0:
                return pd.DataFrame({"code": ["100"]}).to_json()
            else:
                sql_query["code"] = "100"
            print(sql_query)
            return sql_query.to_json()
        except Exception as e:
            print(e)
            return {"code": "400"}

class AddAssignment(Resource):
    @staticmethod
    def post():
        request_data = request.form
        user_id = request_data["id"]
        name = request_data["name"]
        description = request_data["description"]
        due_date = request_data["due_date"]

        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''INSERT INTO Assignments (uid, name, description, due_date) VALUES (?, ?, ?, ?)''',
                           user_id, name, description, due_date)
            mutex.release()
            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class DeleteAssignment(Resource):
    @staticmethod
    def post():
        request_data = request.form
        assignment_id = request_data["id"]

        try:
            mutex.acquire()
            cursor = sql_conn.cursor()

            cursor.execute('''DELETE FROM Assignments WHERE id = ?''', assignment_id)
            mutex.release()

            return {"code": "100"}
        except Exception as e:
            print(e)
            return {"code": "400"}

class GetAssignments(Resource):
    @staticmethod
    def get():
        request_data = request.form
        user_id = request_data["id"]

        try:
            mutex.acquire()
            sql_query = pd.read_sql_query("SELECT * FROM Assignments WHERE uid = " + '\'' + user_id + '\'',
                                          sql_conn)
            mutex.release()
            if sql_query.size == 0:
                return pd.DataFrame({"code": ["100"]}).to_json()
            else:
                sql_query["code"] = "100"
            print(sql_query)
            return sql_query.to_json()
        except Exception as e:
            print(e)
            return {"code": "400"}

class IsAdmin(Resource):
    @staticmethod
    def get():
        group_id = request.form["gid"]
        user_id = request.form["uid"]
        try:
            mutex.acquire()
            sql_query = pd.read_sql_query("SELECT M.gid, M.uid FROM Members AS M"
                                          " WHERE M.gid = " + '\'' + group_id + '\'' +
                                          " AND M.uid = " + '\'' + user_id + '\'' +
                                          " AND M.is_admin = 1", sql_conn)
            mutex.release()
            if sql_query.size == 0:
                return {"code": "100", "is_admin": "false"}
            else:
                return {"code": "100", "is_admin": "true"}
        except Exception as e:
            print(e)
            return {"code": "400"}


api.add_resource(GetUserData, "/get_user_data")
api.add_resource(RegisterUser, "/register")
api.add_resource(DeleteUser, "/delete")
api.add_resource(CreateGroup, "/create_group")
api.add_resource(DeleteGroup, "/delete_group")
api.add_resource(GetGroupsOfUser, "/get_user_groups")
api.add_resource(GetAllUsers, "/get_all_users")
api.add_resource(UpdateUser, "/update_user")
api.add_resource(GetMembers, "/get_members")
api.add_resource(AddReminder, "/add_reminder")
api.add_resource(DeleteReminder, "/delete_reminder")
api.add_resource(GetReminders, "/get_reminders")
api.add_resource(AddUserToGroup, "/add_user_to_group")
api.add_resource(RemoveUserFromGroup, "/remove_user_from_group")
api.add_resource(AddPost, "/add_post")
api.add_resource(DeletePost, "/delete_post")
api.add_resource(GetPosts, "/get_group_posts")
api.add_resource(GetAssignments, "/get_assignments")
api.add_resource(IsAdmin, "/is_admin")
api.add_resource(AddAssignment, "/add_assignment")
api.add_resource(DeleteAssignment, "/delete_assignment")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
