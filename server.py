from datetime import time
import datetime
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame
import requests
import pandas as pd
import datetime as dt

def getCovidFromWiki():
    database = pd.read_json('database.json', dtype='str')

    url = "https://vi.wikipedia.org/wiki/B%E1%BA%A3n_m%E1%BA%ABu:D%E1%BB%AF_li%E1%BB%87u_%C4%91%E1%BA%A1i_d%E1%BB%8Bch_COVID-19/S%E1%BB%91_ca_nhi%E1%BB%85m_theo_t%E1%BB%89nh_th%C3%A0nh_t%E1%BA%A1i_Vi%E1%BB%87t_Nam#cite_note-1"
    getUrl = requests.get(url)
    soup = BeautifulSoup(getUrl.text, 'html.parser')
    dataTable = soup.find('table', class_="wikitable")
    web_data = pd.read_html(str(dataTable))[0].astype('str')
    web_data.columns = ['Tỉnh thành', 'Ca nhiễm', 'Đang điều trị', 'Khác', 'Hồi phục', 'Tử vong']
    df_new = web_data[:63]

    today_string = dt.datetime.today().strftime("%d/%m/%Y")
    df_new['Ngày'] = today_string

    df_old = database[-63:].copy()

    flag = False
    if today_string not in set(database['Ngày'].values):
        database = pd.concat([database, df_new], sort=False).reset_index(drop=True)
        flag = True
    else:
        is_same = df_new.equals(df_old.reset_index(drop=True))
        if not is_same:
            database[-63:] = df_new
            flag = True

    # Only save if have new records
    if flag:
        database.to_json('database.json')


def getCovidFromFile():
    global dfInfo
    dfInfo = pd.read_json('database.json', dtype='str')


def getData():
    with open('data.txt', 'r') as f:
        lines = f.readlines()

    for i in range(0, len(lines), 2):
        Userlist.append(lines[i].strip())
        passlist.append(lines[i + 1].strip())

    f.close()

def saveData():
    f = open('data.txt', 'w')

    for i in range(0, len(Userlist), 1) :
        f.write(Userlist[i] + '\n')
        f.write(passlist[i] + '\n')

    f.close()

# def updateDatebase(database):
#     # lay df today
#     today_string = datetime.datetime.today().strftime("%d/%m/%Y")
#     today_database = database[database["Ngày"] == today_string]

    # crawl du lieu
    # data_web (moi)

    # check xem data_web nay giong today_database khong?

    # neu khong giong thi dua vao database va luu json

    # return database

def accept_incoming_connections():
    """Sets up handling for incoming clients"""
    while True:
        client, client_address = SERVER.accept()
        print("%s - %s has connected" % client_address)
        addresses[client] = client_address
        Thread(target = handle_client, args = (client, client_address)).start()

        #if (# Kiem tra hien tai co bang 8g ):
            # goi ham cap nhat database()

def handle_client(client, client_address):  # Takes client socket as argument
    """Handles a single client connection"""
    getCovidFromWiki()
    getCovidFromFile()
    while True:
        # Phần nhập Username và in ra
        try:
            name = client.recv(BUFSIZ).decode("utf8")
        except:
            print('Client disconnected')
            return
        # Phần nhập Password và in ra
        try:
            password = client.recv(BUFSIZ).decode("utf8")
        except:
            print('Client disconnected')
            return

        status = name[len(name) - 1: len(name)]
        name = name[0: len(name) - 2]

        del Userlist[:]
        del passlist[:]
        getData()

        if status == "1":
            ok = False
            for i in range (0, len(Userlist), 1):
                if name == Userlist[i]:
                    if password == passlist[i]:
                        ok = True
                        try:
                            client.send(bytes("success", "utf8"))
                        except:
                            print('Client disconnected')
                            break
            if ok == True:
                break
            elif ok == False:
                try:
                    client.send(bytes("unsuccess", "utf8"))
                except:
                    print('Client disconnected')
                    break
        elif status == "2":
            ok = True
            for i in range (0, len(Userlist), 1):
                if name == Userlist[i]:
                    client.send(bytes("unsuccess", "utf8"))
                    ok = False
                    break
            if ok == True:
                Userlist.append(name)
                passlist.append(password)
                saveData()
                client.send(bytes("success", "utf8"))
                break
    
    clients[client] = name

    while True:
        try:
            msg = client.recv(BUFSIZ)
        except:
            print("Client disconnect")
            break
        try:
            client.send(bytes(name + ": ", "utf8") + msg)
        except:
            print("Client disconnect")
            break
        if msg != bytes("{quit}", "utf8"):
            query = {}
            _msg = msg.decode('utf-8')
            idx = _msg.find('^')
            tt = _msg[0:idx]
            if tt in map_alias.keys():
                tt = map_alias[tt]
            query["Tỉnh thành"] = tt
            query["Ngày"] = _msg[idx + 1:]
            print(query["Tỉnh thành"], query["Ngày"])
            res = dfInfo[(dfInfo["Tỉnh thành"] == query["Tỉnh thành"]) & (dfInfo["Ngày"] == query["Ngày"])]
            if not res.empty:
                rep = "Tỉnh thành: " + str(res['Tỉnh thành'].values[0]) + '\n' + "Số ca nhiễm: " + str(res['Ca nhiễm'].values[0]) + '\n' + "Số ca đang điều trị: " + str(res['Đang điều trị'].values[0]) + '\n' + "Khác: " + str(res['Khác'].values[0]) + '\n' + "Số ca hồi phục: " + str(res['Hồi phục'].values[0]) + '\n' + "Số ca tử vong: " + str(res['Tử vong'].values[0])
            else :
                rep = "Invalid Data"
            #msg1 = input("Replied to " + name + ': ')
            client.send(bytes(rep + '\n', "utf8"))
        else:
            try:
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del clients[client]
                break
            except:
                print("Client disconnect")
                break

clients = {}
addresses = {}
map_alias = {"AG": "An Giang", "BV": "Bà Rịa - Vũng Tàu", "BL": "Bạc Liêu", "BK": "Bắc Kạn", "BG": "Bắc Giang",
"BN": "Bắc Ninh", "BT": "Bến Tre", "BD": "Bình Dương", "BDi": "Bình Định", "BP": "Bình Phước", "BTh": "Bình Thuận",
"CM": "Cà Mau", "CB": "Cao Bằng", "CT": "Cần Thơ", "ĐNa": "Đà Nẵng", "ĐL": "Đắk Lắk", "ĐNo": "Đắk Nông", "ĐB": "Điện Biên",
"ĐN": "Đồng Nai", "ĐT": "Đồng Tháp", "GL": "Gia Lai", "HG": "Hà Giang", "HNa": "Hà Nam", "HN": "Hà Nội", "HT": "Hà Tĩnh",
"HD": "Hải Dương", "HP": "Hải Phòng", "HGi": "Hậu Giang", "HB": "Hòa Bình", "SG": "TP. Hồ Chí Minh", "HY": "Hưng Yên",
"KH": "Khánh Hoà", "KG": "Kiên Giang", "KT": "Kon Tum", "LC": "Lai Châu", "LS": "Lạng Sơn", "LCa": "Lào Cai", "LĐ": "Lâm Đồng",
"LA": "Long An", "NĐ": "Nam Định", "NA": "Nghệ An", "NB": "Ninh Bình", "NT": "Ninh Thuận", "PT": "Phú Thọ", "PY": "Phú Yên",
"QB": "Quảng Bình", "QNa": "Quảng Nam", "QNg": "Quảng Ngãi", "QN": "Quảng Ninh", "QT": "Quảng Trị", "ST": "Sóc Trăng", "SL": "Sơn La",
"TN": "Tây Ninh", "TB": "Thái Bình", "TNg": "Thái Nguyên", "TH": "Thanh Hóa", "TTH": "Thừa Thiên – Huế", "TG": "Tiền Giang",
"TV": "Trà Vinh", "TQ": "Tuyên Quang", "VL": "Vĩnh Long", "VP": "Vĩnh Phúc", "YB": "Yên Bái", "Thừa Thiên - Huế": "Thừa Thiên – Huế"}
Userlist = []
passlist = []
dfInfo = pd.DataFrame()
HOST = ''
PORT = 33000
BUFSIZ = 1024 * 4
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(10)

   # server_GUI = tkinter.Tk()
    #server_GUI.title("Get COVID Information - Server")
    #server_GUI.geometry('600x625')

    #frame = tkinter.Frame(server_GUI)
    #scroll = tkinter.Scrollbar(frame)
    #sv_list = tkinter.Listbox(frame, height = 35, width = 125, yscrollcommand = scroll.set)
    #scroll.pack(side = tkinter.RIGHT, fill = tkinter.Y)
    #sv_list.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
    #sv_list.pack()
    #frame.pack()

    #sv_list.insert(tkinter.END, 'Waiting for connection from Client!')
    print('Waiting for connection from Client')
    
    ACCEPT_THREAD = Thread(target = accept_incoming_connections)
    
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    #server_GUI.mainloop()
    SERVER.close()