import sqlite3
import PySimpleGUI as sg

# Veritabanından otel bilgilerini listeleme fonksiyonu
def list_hotels():
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    cur.execute("SELECT hid, city, brand FROM Hotel")
    hotels = cur.fetchall()  # Sadece otel verilerini alıyoruz
    con.close()
    return hotels


# GUI Başlangıcı
layout = [
    [sg.Button("List All Hotels"), sg.Button("Close")]
]

window = sg.Window("Hotel Management", layout)

# GUI Döngüsü
while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, "Close"):
        break

    # Otelleri Listeleme
    if event == "List All Hotels":
        hotels = list_hotels()
        if hotels:
            # Sadece doğru formatta veri yazdır
            clean_hotels = [f"ID: {hotel[0]}, City: {hotel[1]}, Brand: {hotel[2]}" for hotel in hotels if len(hotel) == 3]
            sg.popup_scrolled("All Hotels", "\n".join(clean_hotels), size=(50, 10))
        else:
            sg.popup("No hotels found.")
