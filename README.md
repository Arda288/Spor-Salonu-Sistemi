# 🏋️ Golds Gym Otomasyon Sistemi

Spor salonu üyelerinin takibini, antrenman programlarını ve üyelik sürelerini yönetmek amacıyla geliştirilmiş masaüstü otomasyon uygulaması.

## 🖥️ Özellikler

- Kullanıcı kayıt ve giriş sistemi
- Üye yönetimi (ekleme, düzenleme, listeleme)
- Antrenman programı atama (Hacim, Definasyon, Full Body)
- Üyelik süresi takibi (otomatik 30 gün deneme süresi)
- SQL Server veritabanı entegrasyonu
- Koyu tema arayüz

## 🛠️ Kullanılan Teknolojiler

- Python 3.9
- Tkinter (Arayüz)
- pyodbc (Veritabanı bağlantısı)
- Pillow / PIL (Görsel işleme)
- Microsoft SQL Server (SQLEXPRESS)

## ⚙️ Kurulum

1. Repoyu klonlayın:
https://github.com/Arda288/Spor-Salonu-Sistemi

2. Gerekli kütüphaneleri yükleyin:

3. SQL Server'da `SporSalonuDB` adında bir veritabanı oluşturun.

4. `main.py` içindeki bağlantı dizesini kendi sunucu adınıza göre düzenleyin:
```python
   r"SERVER=.\SQLEXPRESS;"
```

5. Uygulamayı çalıştırın:

## 👥 Katkıda Bulunanlar

- Arda Savaş — [@Arda288](https://github.com/Arda288)
