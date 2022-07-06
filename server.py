import socket
import json
import threading
import os

HOST = '0.0.0.0'
PORT = 65432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

folders = next(os.walk('.'))[1]
subfolders = []
subjects = []

try:
    with open("./utility/subjects.txt", 'r', encoding='utf-8') as file:
        f = file.read()
        subjects = f.split('.')
        print(subjects)
except:
    print('error in reading subjects')

def commands():
    while True:
        command = str(input())
        if command == 'threads':
            print(thread)

        if command == 'get file':
            print(dataBase)

thread = threading.Thread(target=commands)
thread.start()

dataBase = {}
def makeDataBase():
    print(subfolders)
    for classes in subfolders:
        users = next(os.walk(str("./" + classes)))[1]
        userData = {}
        for user in users:
            questions = next(os.walk(str("./" + classes + "/" + user)))[2]
            questionData = {}
            for question in questions:
                with open("./" + classes + "/" + user + "/" + question, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    questionData[(question.replace('.json',''))] = data
            userData[user] = questionData
        dataBase[classes] = userData


userData = {}
for folder in folders:
    try:
        print(folder)
        with open((folder + "/users.json"), encoding='utf-8') as fh:
            userData[folder] = json.load(fh)
        print(userData)
        subfolders.append(folder.replace('./', ''))
    except:
        pass

users = {}
for section in userData:
    us = []
    for user in userData[section]["users"]:
        us.append(user["name"])
    users[section] = us
print(users)

def auth(client, data):
    print(client)
    nouser = True
    try:
        print(userData)
        for user in userData[data['class']]['users']:
            if data["name"] == user['name']:
                if data["password"] == user['password']:
                    print(f'user {str(data["name"])} connected')
                    client.send('connected'.encode('utf-8'))
                else:
                    client.send('wrongPassword'.encode('utf-8'))
                    auth(client, decoder(client.recv(1024).decode('utf-8')))
                nouser = False
            break
        if nouser:
            client.send('NOUSER'.encode('utf-8'))
            confirmation = client.recv(1024).decode('utf-8')
            if confirmation == "create":
                jsonObj = []
                print(data['class'])
                with open((data['class'] + "/users.json"), 'r', encoding='utf-8') as fh:
                    jsonObj = json.load(fh)
                    print("file opened")
                    jsonObj["users"].append({'name':data['name'],'password':data['password'],'power':1,'new':True})
                with open((data['class'] + "/users.json"), 'w',encoding='utf-8') as fh:
                    json.dump(jsonObj, fh,indent=4)
                    print("client added")
                client.send('added'.encode('utf-8'))
    except:
        client.send('notAllFilled'.encode('utf-8'))
        auth(client, decoder(client.recv(1024).decode('utf-8')))

def decoder(data)->json:
    try:
        data = str(data)
        data = data.replace("\'",'\"')
        data = json.loads(data)
        print(data)
        return data
    except:
        return ({"id":0})

def client_logging(user):
    rcvddata = user.recv(1024).decode('utf-8-sig')
    rcvddata = decoder(rcvddata)
    auth(user, rcvddata)
    data_decode(user, rcvddata)

def send_classes(user):
    message = str(subfolders)
    user.send(message.encode('utf-8'))

def send_subjects(user):
    message = str(subjects)
    user.send(message.encode('utf-8'))

def send_students(user):
    message = str(users)
    user.send(message.encode('utf-8'))

def data_decode(user, userData):
    print('everything OK') 
    while True:
        try:
            rcvddata = user.recv(1024).decode('utf-8')
            rcvddata = decoder(rcvddata)
            if rcvddata["id"] == 2:
                user.send("roger".encode('utf-8'))
                print(rcvddata)
                questions = rcvddata["data"]
                for question in questions["questions"]:
                    jsonData = json.dumps(question['sections'], indent=4, ensure_ascii=False)
                    print(jsonData)
                    filename = (str(userData['class'] + "/" + userData['name'] + "/" + question['question'] + ".json"))
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    with open(filename, "w", encoding='utf8') as f:
                        f.write(jsonData)
                    makeDataBase()
            if rcvddata["id"] == 3:
                print('sending data')
                user.send(str(dataBase[userData['class']]).encode('utf-8'))
                print('data sent')
            if rcvddata["id"] == 4:
                filename = (str("utility/report.json"))
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, mode='a+', encoding='utf8') as f:
                    jsonObj = json.load(f)
                    entry = {"class":rcvddata["class"],"name":rcvddata["name"],"question":rcvddata["question"],"reporter":rcvddata["reporter"],"classRep":rcvddata["classRep"]}
                    jsonObj.dump(jsonObj, entry)
        except:
            print('exception')
            user.close()
            break

def received():
    makeDataBase()
    print('server is running ...')
    while True:
        user, address = s.accept()
        print(f'connection established with {str(address)}')
        send_classes(user)
        send_subjects(user)
        send_students(user)
        thread = threading.Thread(target=client_logging,args=(user,))
        thread.start()

if __name__ == "__main__":
    received()