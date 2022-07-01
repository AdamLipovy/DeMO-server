import socket 
import json
import threading
import os

HOST = '' 
PORT = 65432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

subfolders = next(os.walk('.'))[1]

def commands():
    while True:
        command = str(input())
        if command == 'list':
            print(users)
        if command == 'threads':
            print(thread)
        if command == 'clear':
            print('do you really want to destroy all connections?')
            command = str(input())
            if command == 'y' or command == 'yes':
                users.clear()
        if command == 'get file':
            print(dataBase)

thread = threading.Thread(target=commands)
thread.start()



for index in range(len(subfolders)):
    subfolders[index] = subfolders[index].replace('./', '')

dataBase = {}
def makeDataBase():
    for classes in ['OC']:
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
for folder in subfolders:
    print(folder)
    with open((folder + "\\users.json"), encoding='utf-8') as fh:
        userData[folder] = json.load(fh)

def auth(client, data):
    print(client)
    nouser = True
    try:
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
                with open((data['class'] + "\\users.json"), encoding='utf-8') as fh:
                    jsonObj = json.load(fh)
                    jsonObj["users"].append({'name':data['name'],'password':data['password'],'power':1,'new':True})
                with open((data['class'] + "\\users.json"), 'w',encoding='utf-8') as fh:
                    json.dump(jsonObj, fh,indent=4)
                client.send('added'.encode('utf-8'))
    except:
        client.send('notAllFilled'.encode('utf-8'))
        auth(client, decoder(client.recv(1024).decode('utf-8')))

users = []

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
    rcvddata = user.recv(1024).decode('utf-8')
    rcvddata = decoder(rcvddata)
    auth(user, rcvddata)
    data_decode(user, rcvddata)
    
def send_classes(user):
    print(f'sending classes to {str(user)}')
    message = str(subfolders)
    user.send(message.encode('utf-8'))

def data_decode(user, userData):
    print('everything OK')   
    try:
        rcvddata = user.recv(1024).decode('utf-8')
        rcvddata = decoder(rcvddata)
        if rcvddata["id"] == 2:
            user.send("roger".encode('utf-8'))
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
        
        if rcvddata["id"] == 4:
            filename = (str("utility/report.json"))
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, mode='a+', encoding='utf8') as f:
                jsonObj = json.load(f)
                entry = {"class":rcvddata["class"],"name":rcvddata["name"],"question":rcvddata["question"],"reporter":rcvddata["reporter"],"classRep":rcvddata["classRep"]}
                jsonObj.dump(jsonObj, entry)
    except:
        print('exception')
        users.remove(user)
        user.close()

def received():
    makeDataBase()
    print('server is running ...')
    while True:        
        user, address = s.accept()
        print(f'connection established with {str(address)}')
        users.append(user)
        print(users)
        send_classes(user)
        thread = threading.Thread(target=client_logging,args=(user,))
        thread.start()

if __name__ == "__main__":
    received()
