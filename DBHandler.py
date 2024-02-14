
import pymysql
class DBHandler:
    def __init__(self,host,user,password,database):
        self.host=host
        self.user = user
        self.password=password
        self.database=database

    def login(self,User):
        mydb = None
        mydbCursor=None
        exist = False
        try:
            # Get DB Connection
            mydb = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            # Get cursor object
            mydbCursor = mydb.cursor()
            sql = "Select * from users where username = %s and password = %s"
            args = (User.username, User.password)
            mydbCursor.execute(sql, args)
            row = mydbCursor.fetchone()
            if row != None:
                exist = True
        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor != None:
                mydbCursor.close()

            if mydb != None:
                mydb.close()
            return exist
