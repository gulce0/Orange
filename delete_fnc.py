import sqlite3

def delete_wrong_data():
    # Veritabanına bağlan
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Hatalı veriyi silmek için SQL sorgusu
    cur.execute("DELETE FROM Hotel WHERE city LIKE '%C:/Users%'")
    con.commit()

    # Silme işleminden sonra kontrol etmek için tüm otelleri listele
    cur.execute("SELECT * FROM Hotel")
    hotels = cur.fetchall()
    print("Temizlenmiş Oteller:")
    for hotel in hotels:
        print(hotel)

    # Veritabanı bağlantısını kapat
    con.close()

# Fonksiyonu çalıştır
delete_wrong_data()
