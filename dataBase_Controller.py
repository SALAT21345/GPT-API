import sqlite3 

def create_table():
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute('''
                CREATE TABLE IF NOT EXISTS users 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                Login TEXT NOT NULL, 
                email TEXT UNIQUE NOT NULL, 
                password TEXT NOT NULL,
                SessionId INTEGER NOT NULL, 
                Tokens INTEGER,
                Context TEXT
                )''')
    bd.commit()

def CreateAccount(login,email,password,session):
    create_table()
    _IsHaveAccount = IsHaveAccount(login,email)
    if _IsHaveAccount == True:
        return "Error: The user with this Username or emain already exists."
    else:  
        bd = sqlite3.connect('Users.bd')
        cur = bd.cursor()
        cur.execute("INSERT INTO users (Login, email, password,SessionId) VALUES (?, ?, ?,?)", (login, email, password,session))
        bd.commit()
        bd.close()
        print("Щас вернется тру")
        return "Account created successfully."

def IsHaveAccount(login, email):
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("SELECT * FROM users WHERE Login=?", (login,))
    HaveAccount = cur.fetchone()
    cur.execute("SELECT * FROM users WHERE email =?", (email,))
    email_isValid = cur.fetchall()
    bd.close()
    if HaveAccount != None and email_isValid != None:
        return True
    else:
        return False

def CheckAllUsers():
    create_table()
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    bd.close()
    return data

def AddContext(login, Prompt, Answer):
    create_table()
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("SELECT Context From Users WHERE Login = ?", (login,))
    Context = cur.fetchone()
    if Context[0] == None:
        NewContext = f"User: {Prompt}\nChatGPT: {Answer}\n"
        cur.execute("UPDATE Users SET Context =? WHERE Login =?", (NewContext, login))
    else:
        LastContext = Context[0]
        NewContext = f"{LastContext} User: {Prompt}\nChatGPT: {Answer}\n"
        cur.execute("UPDATE Users SET Context =? WHERE Login =?", (NewContext, login))
    bd.commit()
    bd.close()

def GetContext(login):
    create_table()
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("SELECT Context FROM Users WHERE Login =?", (login,))
    Context = cur.fetchone()
    bd.close()
    if Context is None:
        return "No context found for this user."
    else:
        return Context[0]
    
def loginAccount(login, password,session):
    create_table()
    bd = sqlite3.connect('Users.bd')
    cur = bd.cursor()
    cur.execute("SELECT * FROM users WHERE Login=? AND password=?", (login, password))
    data = cur.fetchone()
    if data != None:
        cur.execute("Update users SET SessionId=? Where Login =?", (session, login))
        return True
    else:
        return False

if __name__ == "__main__":
    print(CheckAllUsers())


    