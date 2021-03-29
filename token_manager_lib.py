def menu():
    print("-----------------------------------------------------------------------------------------------------")
    print("1. Access codes from database (requires username and keyfile, refreshes every second)") #Done
    print("2. Access codes from token (refreshes every second, not recommended)") #Done
    print("3. Get token from database (requires username and keyfile, not recommended)") #Done
    print("4. Insert new token (Generated or your own) to database") #Done
    print("5. Delete token from database (requires username, keyfile and valid code to confirm)")
    print("0. Quit")
    return int(input(": "))

def connect():
    #print("Connect")
    import psycopg2
    try:
        connection = psycopg2.connect(database="verification", user="Bob", password="##########", host="localhost", port="5433")
        return connection
    except Exception as error:
        print(error)

def RandNewToken():
    #print("RandNewToken")
    import random
    token = random.randrange(1000000000,10000000000)
    return token

def GenKey():
    #print("GenKey")
    from cryptography.fernet import Fernet
    import random
    key = Fernet.generate_key()
    keyfile = str(random.randrange(1, 1000)) + ".key"
    with open("files/" + keyfile, 'wb') as key_file:
        key_file.write(key)
    print(f"Key saved to {keyfile}, do not lose it!")
    return key, keyfile

def GetKey(key_file):
    #print("GetKey")
    with open(f'{key_file}', 'rb') as mykey:
        key = mykey.read()
    return key

def EncryptToken(token):
    #print("EncryptToken")
    from cryptography.fernet import Fernet
    key, keyfile = GenKey()
    f = Fernet(key)
    token_enc = f.encrypt(str(token).encode())
    return token_enc, keyfile

def DecryptToken(key_file, token_enc):
    from cryptography.fernet import Fernet
    key = GetKey(key_file)
    f = Fernet(key)
    return int(str(f.decrypt(token_enc)).strip("b'"))

def EncryptTokenWithExistingKeyFile(token, keyfile):
    from cryptography.fernet import Fernet
    key = GetKey(keyfile)
    f = Fernet(key)
    token_enc = f.encrypt(str(token).encode())
    return token_enc

def InsertToken(user_nick, token, keyfile):
    #print("InsertToken")
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(f"insert into tokens (user_key, token, key_file) values ('{user_nick}',{str(token)[1:]},'{keyfile}');")
    connection.commit()
    return "Success"

def RemoveToken(user_nick, keyfile, code):
    connection = connect()
    cursor = connection.cursor()
    valid_code, _ = GetCodeDatabase(user_nick, keyfile)
    if int(code) == int(valid_code):
        print("Code accepted")
        cursor.execute(f"delete from tokens where user_key='{user_nick}' and key_file='{keyfile}';")
        connection.commit()
        return "Success"
    return "Code invalid"

def GetToken(user_nick, key_file):
    #print("GetToken")
    from cryptography.fernet import Fernet
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(f"select token from tokens where user_key='{user_nick}';")
    token_enc = cursor.fetchall()
    token_enc = token_enc[0][0].encode()
    return DecryptToken(key_file, token_enc)

def GetCode(token: int):
    #print("GetCode")
    from math import floor
    import time
    import random
    left = 10
    timer = floor(time.time())
    while timer%10 != 0:
        timer -= 1
        left = left - 1
    random.seed(token*timer)
    code = (random.randrange(1, 10000) * timer / token)%1000000
    while code < 100000:
        code = code * 10
    return floor(code), left

def GetCodeDatabase(user_nick, key_file):
    #print("GetCodeDatabase")
    token = GetToken(user_nick, key_file)
    return GetCode(token)

def AccessCodesDatabase(user_nick, key_file):
    import time
    while True:
        try:
            time.sleep(1)
            code, left = GetCodeDatabase(user_nick, key_file)
            print("Code: ", code)
            print("Left time: ", left)
        except KeyboardInterrupt:
            break

def AccessCodes(token):
    import time
    while True:
        try:
            time.sleep(1)
            code, left = GetCode(token)
            print("Code: ", code)
            print("Left time: ", left)
        except KeyboardInterrupt:
            break

def MenuInteract():
    try:
        request = menu()
        if request == 0:
            exit()
        elif request == 2:
            token = int(input("Token (must be numerical): "))
            AccessCodes(token)
        elif request == 1:
            user_nick = input("Username: ")
            key_file = input("Path to keyfile: ")
            AccessCodesDatabase(user_nick, key_file)
        elif request == 3:
            print("Warning, token can be used to directly access code, exposing it is bad idea, continue?")
            accept = input("y/N: ")
            if accept.startswith("y") or accept.startswith("Y"):
                user_nick = input("Username: ")
                key_file = input("Keyfile: ")
                token = GetToken(user_nick, key_file)
                print("Token (everyone with that code can access your codes): ", token)
            else:
                print("Going back")
        elif request == 4:
            user_nick = input("Username: ")
            token = input("Encrypted token (optional, must be encrypted, if empty will generate new one): ")
            keyfile = None
            if token == '':
                token, keyfile = EncryptToken(RandNewToken())
            if keyfile == None:
                keyfile = input("KeyFile: ")
            print(InsertToken(user_nick, token=token, keyfile=keyfile))
        elif request == 5:
            print("Warning, removing token from database will make your codes useless and you won't be able to log into services using tokens, continue?")
            accept = input("y/N: ")
            if accept.startswith("y") or accept.startswith("Y"):
                user_nick = input("Username: ")
                key_file = input("Keyfile: ")
                code = input("Valid code: ")
                print(RemoveToken(user_nick, key_file, code))
            else:
                print("Going back")
        else:
            print("Invalid request")
    except ValueError:
        print("Invalid value")
    except IndexError:
        print("Token doesn't exist in database")
