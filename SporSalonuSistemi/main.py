from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import pyodbc
import random
import io
from datetime import date, timedelta, datetime

#veri tabanı bağlantısı
#kendi bilgisayar adımızı server kısmına yazmalıyız. (.\SQLEXPRESS çalışabiliyor.)
CONN_STR = (
    r"DRIVER={SQL Server};"
    r"SERVER=.\SQLEXPRESS;"
    r"DATABASE=SporSalonuDB;"
    r"Trusted_Connection=yes;"
)


def get_db_connection():
    return pyodbc.connect(CONN_STR)



PROGRAMLAR = {
    "Hacim (Bulking)": "1. GÜN: Göğüs-Biceps (Bench Press, Curl...)\n2. GÜN: Sırt-Triceps (Row, Pushdown...)\n3. GÜN: Bacak-Omuz (Squat, Press...)",
    "Definasyon (Yağ Yakımı)": "Yüksek tekrar sayıları (15-20), Süper setler ve her antrenman sonu 25dk HIIT Kardiyo.",
    "Full Body (Başlangıç)": "Haftada 3 Gün: Squat, Chest Press, Lat Pulldown, Shoulder Press, Plank (Tüm Vücut)"
}


class SporSistemiPro:
    def __init__(self, pencere):
        self.pencere = pencere
        self.pencere.title("Golds Gym")
        self.genislik = 1100
        self.yukseklik = 700
        self.pencere_ortala(self.genislik, self.yukseklik)


        self.pencere.grid_rowconfigure(0, weight=1)
        self.pencere.grid_columnconfigure(0, weight=1)

        self.aktif_kullanici = None


        self.font_baslik = ("Segoe UI", 24, "bold")
        self.font_normal = ("Segoe UI", 12)
        self.font_kucuk = ("Segoe UI", 10)
        self.font_buton = ("Segoe UI", 11, "bold")

        #tema için
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2d3436", foreground="white", fieldbackground="black", rowheight=25)
        style.map('Treeview', background=[('selected', 'orange')])

        self.giris_sayfasi()

    def pencere_ortala(self, w, h):
        self.pencere.geometry(f"{w}x{h}")
        ws = self.pencere.winfo_screenwidth()
        hs = self.pencere.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.pencere.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def temizle(self):
        self.pencere.config(menu="", bg="SystemButtonFace")
        for widget in self.pencere.winfo_children():
            widget.destroy()

    def sistem_hakkinda(self):
        mesaj = (
            "  GOLDS GYM OTOMASYON SİSTEMİ\n\n"
            "Bu sistem, spor salonu üyelerinin takibini, antrenman programlarını "
            "ve üyelik sürelerini yönetmek amacıyla geliştirilmiştir.\n\n"
            "--------------------------------------------------\n\n"
            "  NASIL KAYIT OLUNUR?\n"
            "1. Ana ekrandaki mavi renkli 'KAYIT OL' butonuna tıklayın.\n"
            "2. Ad, Soyad, Kullanıcı Adı ve Şifre alanlarını eksiksiz doldurun.\n"
            "3. Kaydı tamamladığınızda sistem size otomatik 30 gün deneme süresi tanımlar.\n"
            "4. Belirlediğiniz kullanıcı adı ve şifre ile giriş yapabilirsiniz."
        )
        messagebox.showinfo("Sistem Hakkında & Yardım", mesaj)


    def giris_sayfasi(self):
        self.temizle()

        # Menü
        ana_menu = Menu(self.pencere)
        self.pencere.config(menu=ana_menu)
        yardim_menusu = Menu(ana_menu, tearoff=0)
        ana_menu.add_cascade(label="Menü", menu=yardim_menusu)
        yardim_menusu.add_command(label="Sistem Hakkında & Nasıl Kayıt Olunur?", command=self.sistem_hakkinda)

        #arka plan canvas olacak
        canvas = Canvas(self.pencere, width=self.genislik, height=self.yukseklik, highlightthickness=0, bg="black")

        canvas.grid(row=0, column=0, sticky="nsew")

        try:
            image = Image.open("BackGround/zyzzbg1.png.png")
            image = image.resize((self.genislik, self.yukseklik), Image.LANCZOS)
            self.bg_img_ref = ImageTk.PhotoImage(image)
            canvas.image = self.bg_img_ref
            canvas.create_image(0, 0, image=self.bg_img_ref, anchor="nw")
        except:
            pass


        center_x = self.genislik / 2
        start_y = 200

        canvas.create_text(center_x, start_y - 80, text="SPOR SALONU GİRİŞİ", font=("Impact", 36), fill="#f1c40f")

        canvas.create_text(center_x, start_y, text="Kullanıcı Adı:", font=("Segoe UI", 14, "bold"), fill="#f1c40f")
        self.ent_u = Entry(self.pencere, font=("Segoe UI", 12), width=25, bg="#ecf0f1")
        canvas.create_window(center_x, start_y + 30, window=self.ent_u)

        canvas.create_text(center_x, start_y + 80, text="Şifre:", font=("Segoe UI", 14, "bold"), fill="#f1c40f")
        self.ent_p = Entry(self.pencere, show="*", font=("Segoe UI", 12), width=25, bg="#ecf0f1")
        canvas.create_window(center_x, start_y + 110, window=self.ent_p)

        btn_giris = Button(self.pencere, text="GİRİŞ YAP", bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"),
                           width=20, command=self.giris_kontrol)
        canvas.create_window(center_x, start_y + 170, window=btn_giris)

        btn_kayit = Button(self.pencere, text="KAYIT OL", bg="#2980b9", fg="white", font=("Segoe UI", 11, "bold"),
                           width=20, command=self.kayit_sayfasi)
        canvas.create_window(center_x, start_y + 220, window=btn_kayit)

    def giris_kontrol(self):
        try:
            conn = get_db_connection();
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE username=? AND password=?", (self.ent_u.get(), self.ent_p.get()))
            row = cursor.fetchone()
            conn.close()
            if row:
                self.aktif_kullanici = row
                self.admin_paneli() if row.role.strip() == 'admin' else self.uye_paneli()
            else:
                messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış!")
        except Exception as e:
            messagebox.showerror("Hata", str(e))


    def kayit_sayfasi(self):
        self.temizle()

        canvas = Canvas(self.pencere, width=self.genislik, height=self.yukseklik, highlightthickness=0, bg="black")
        canvas.grid(row=0, column=0, sticky="nsew")

        try:
            image = Image.open("BackGround/zyzzbg1.png.png")
            image = image.resize((self.genislik, self.yukseklik), Image.LANCZOS)
            self.bg_img_ref = ImageTk.PhotoImage(image)
            canvas.image = self.bg_img_ref
            canvas.create_image(0, 0, image=self.bg_img_ref, anchor="nw")
        except:
            pass

        center_x = self.genislik / 2
        y = 150
        canvas.create_text(center_x, y - 60, text="YENİ ÜYE KAYDI", font=("Impact", 32), fill="#f1c40f")

        lbls = ["Ad:", "Soyad:", "Kullanıcı Adı:", "Şifre:", "Telefon:"]
        self.k_ents = []
        for txt in lbls:
            canvas.create_text(center_x - 130, y, text=txt, font=("Segoe UI", 12, "bold"), fill="#f1c40f", anchor="e")
            e = Entry(self.pencere, font=("Segoe UI", 11), width=25, bg="#ecf0f1")
            canvas.create_window(center_x + 20, y, window=e, anchor="w")
            self.k_ents.append(e)
            y += 50

        btn_tamam = Button(self.pencere, text="KAYDI TAMAMLA", bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                           width=25, command=self.kayit_tamamla)
        canvas.create_window(center_x, y + 20, window=btn_tamam)

        btn_iptal = Button(self.pencere, text="GERİ DÖN", command=self.giris_sayfasi, width=20, bg="#bdc3c7")
        canvas.create_window(center_x, y + 70, window=btn_iptal)

    def kayit_tamamla(self):
        d = [x.get() for x in self.k_ents]
        if "" in d: messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurunuz!"); return

        bugun = date.today()
        bitis_tarihi_obj = bugun + timedelta(days=30)
        bitis_tarihi_str = bitis_tarihi_obj.strftime('%Y-%m-%d')

        try:
            conn = get_db_connection();
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Users (name, surname, username, password, phone, expiry_date) VALUES (?,?,?,?,?,?)",
                (d[0], d[1], d[2], d[3], d[4], bitis_tarihi_str))
            conn.commit();
            conn.close()
            messagebox.showinfo("Başarılı", "Kayıt işlemi tamamlandı! ")
            self.giris_sayfasi()
        except Exception as e:
            messagebox.showerror("Kayıt Hatası", f"Hata Detayı:\n{e}")

    #------------------------------------------------------------------------------
    def uye_paneli(self):
        self.temizle()
        self.pencere.config(bg="black")


        conn = get_db_connection();
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE id=?", (self.aktif_kullanici.id,))
        self.aktif_kullanici = cursor.fetchone();
        conn.close()

        #tarih hesaplaması
        bitis = self.aktif_kullanici.expiry_date
        if isinstance(bitis, str):
            try:
                bitis = datetime.strptime(bitis, "%Y-%m-%d").date()
            except:
                bitis = None
        kalan = (bitis - date.today()).days if bitis else 0
        if kalan < 0: kalan = 0


        m = Menu(self.pencere);
        self.pencere.config(menu=m)
        m.add_command(label="Antrenman Programım", command=self.program_hesapla_penceresi)
        m.add_command(label="Çıkış", command=self.giris_sayfasi)

        main_container = Frame(self.pencere, bg="black")
        main_container.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)

        main_container.grid_columnconfigure(0, weight=1)  # Sol taraf (Yazılar)
        main_container.grid_columnconfigure(1, weight=0)  # Sağ taraf (Resim)

        header_frame = Frame(main_container, bg="black")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)

        Label(header_frame, text=f"Hoş geldin, {self.aktif_kullanici.name}",
              font=("Segoe UI", 20, "bold"), fg="white", bg="black").grid(row=0, column=0, sticky="w")


        self.profil_cerceve = Frame(header_frame, bg="#333", width=130, height=130,
                                    highlightbackground="white", highlightthickness=1)
        self.profil_cerceve.grid(row=0, column=1, sticky="e")
        self.profil_cerceve.pack_propagate(False)  # Boyut sabit kalsın

        self.lbl_profil = Label(self.profil_cerceve, text="Fotoğraf\nYükle", bg="#333", fg="white", cursor="hand2")
        self.lbl_profil.pack(fill=BOTH, expand=True)
        self.lbl_profil.bind("<Button-1>", self.foto_yukle)
        if self.aktif_kullanici.profile_pic: self.resmi_goster(self.aktif_kullanici.profile_pic, self.lbl_profil)


        info_box = LabelFrame(main_container, text=" Durum Özeti ", font=self.font_buton,
                              padx=30, pady=30, bg="black", fg="white", bd=2)
        info_box.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

        info_box.grid_columnconfigure(1, weight=1)

        Label(info_box, text=f"Kalan Süre:", font=("Segoe UI", 14), bg="black", fg="white").grid(row=0, column=0,
                                                                                                 sticky="w", pady=10)
        Label(info_box, text=f"{kalan} Gün", font=("Segoe UI", 14, "bold"), fg="#2ecc71", bg="black").grid(row=0,
                                                                                                           column=1,
                                                                                                           sticky="w",
                                                                                                           padx=20)

        Label(info_box, text=f"Bitiş Tarihi:", font=("Segoe UI", 14), bg="black", fg="white").grid(row=1, column=0,
                                                                                                   sticky="w", pady=10)
        Label(info_box, text=f"{bitis}", font=("Segoe UI", 14, "bold"), fg="#3498db", bg="black").grid(row=1, column=1,
                                                                                                       sticky="w",
                                                                                                       padx=20)

        Label(info_box, text=f"Üyelik Ücreti:", font=("Segoe UI", 14), bg="black", fg="white").grid(row=2, column=0,
                                                                                                    sticky="w", pady=10)
        Label(info_box, text=f"{self.aktif_kullanici.fee} TL", font=("Segoe UI", 14, "bold"), fg="#e67e22",
              bg="black").grid(row=2, column=1, sticky="w", padx=20)

        # 3. SATIR: Simülasyon
        sim_box = Frame(main_container, bd=2, relief="groove", bg="#2c3e50")
        sim_box.grid(row=2, column=0, columnspan=2, sticky="ew", pady=20)

        Label(sim_box, text="SALON DOLULUK DURUMU", font=("Segoe UI", 11, "bold"), bg="#2c3e50", fg="white").pack(
            pady=5)
        self.pb = ttk.Progressbar(sim_box, length=800, mode='determinate')  # Length biraz kısaldı grid'e sığsın diye
        self.pb.pack(fill=X, padx=20)
        self.lbl_sim = Label(sim_box, text="...", bg="#2c3e50", fg="white", font=("Segoe UI", 10))
        self.lbl_sim.pack(pady=5)
        self.sim_baslat()

    def foto_yukle(self, event):
        dosya = filedialog.askopenfilename(filetypes=[("Resimler", "*.png;*.jpg;*.jpeg")])
        if dosya:
            with open(dosya, 'rb') as f:
                binary_data = f.read()
            try:
                conn = get_db_connection();
                cursor = conn.cursor()
                cursor.execute("UPDATE Users SET profile_pic=? WHERE id=?", (binary_data, self.aktif_kullanici.id))
                conn.commit();
                conn.close()
                messagebox.showinfo("Başarılı", "Profil fotoğrafı güncellendi!")
                self.resmi_goster(binary_data, self.lbl_profil)
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def resmi_goster(self, binary_data, label_widget):
        try:
            image = Image.open(io.BytesIO(binary_data))
            image = image.resize((125, 125))
            photo = ImageTk.PhotoImage(image)
            label_widget.config(image=photo, text="");
            label_widget.image = photo
        except:
            pass

    def sim_baslat(self):
        if not hasattr(self, 'pb') or not self.pb.winfo_exists(): return
        try:
            v = random.randint(10, 90)
            self.pb['value'] = v
            self.lbl_sim.config(text=f"Doluluk: %{v}")
            self.pencere.after(3000, self.sim_baslat)
        except:
            pass


    def program_hesapla_penceresi(self):
        if hasattr(self, 'top') and self.top.winfo_exists(): self.top.lift(); return
        self.top = Toplevel(self.pencere)
        self.top.title("Kişisel Antrenman Sihirbazı")
        self.top.geometry("500x600")
        self.top.config(bg="black")
        self.top.resizable(False, False)


        self.top.grid_columnconfigure(0, weight=1)

        Label(self.top, text="Vücut Analizi & Program", font=("Segoe UI", 16, "bold"), fg="#3498db", bg="black").grid(
            row=0, column=0, pady=15)

        f = Frame(self.top, bg="black")
        f.grid(row=1, column=0, pady=5)

        Label(f, text="Boyunuz (cm):", font=("Segoe UI", 11), bg="black", fg="white").grid(row=0, column=0, sticky="e",
                                                                                           pady=5)
        self.e_boy = Entry(f, width=15, bg="#333", fg="white", insertbackground="white")
        self.e_boy.grid(row=0, column=1, pady=5, padx=10)

        Label(f, text="Kilonuz (kg):", font=("Segoe UI", 11), bg="black", fg="white").grid(row=1, column=0, sticky="e",
                                                                                           pady=5)
        self.e_kilo = Entry(f, width=15, bg="#333", fg="white", insertbackground="white")
        self.e_kilo.grid(row=1, column=1, pady=5, padx=10)

        Label(f, text="Yaşınız:", font=("Segoe UI", 11), bg="black", fg="white").grid(row=2, column=0, sticky="e",
                                                                                      pady=5)
        self.e_yas = Entry(f, width=15, bg="#333", fg="white", insertbackground="white")
        self.e_yas.grid(row=2, column=1, pady=5, padx=10)

        Button(self.top, text="HESAPLA VE GÜNCELLE", bg="orange", fg="black", font=("Segoe UI", 10, "bold"),
               command=self.ozel_program_algoritmasi).grid(row=2, column=0, pady=15)

        Label(self.top, text="--- MEVCUT / YENİ PROGRAMINIZ ---", font=("Segoe UI", 10, "bold"), fg="#bdc3c7",
              bg="black").grid(row=3, column=0)

        text_frame = Frame(self.top, bg="black")
        text_frame.grid(row=4, column=0, pady=10, padx=20, sticky="nsew")

        self.txt_sonuc = Text(text_frame, height=15, width=50, font=("Segoe UI", 10), bg="#2d3436", fg="white")
        self.txt_sonuc.pack(side=LEFT, fill=BOTH, expand=True)
        scroll = Scrollbar(text_frame, command=self.txt_sonuc.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.txt_sonuc.config(yscrollcommand=scroll.set)

        if self.aktif_kullanici.training_program:
            self.txt_sonuc.insert(END, "Sistemde Kayıtlı Olan Programınız:\n")
            self.txt_sonuc.insert(END, "-" * 40 + "\n\n")
            self.txt_sonuc.insert(END, self.aktif_kullanici.training_program)
        else:
            self.txt_sonuc.insert(END, "Henüz bir program oluşturmadınız.")

    def ozel_program_algoritmasi(self):
        try:
            boy = float(self.e_boy.get()); kilo = float(self.e_kilo.get()); yas = int(self.e_yas.get())
        except:
            messagebox.showerror("Hata", "Lütfen değerleri sayı olarak giriniz!"); return

        vke = kilo / ((boy / 100) ** 2)
        if vke < 18.5:
            durum, p_adi, p_icerik = "Zayıf", "Hacim (Bulking)", PROGRAMLAR[
                "Hacim (Bulking)"]; tavsiye = "Kalori fazlası oluştur."
        elif 18.5 <= vke < 25:
            durum, p_adi, p_icerik = "Normal", "Full Body", PROGRAMLAR.get("Full Body (Başlangıç)",
                                                                           "Standart"); tavsiye = "Formunu koru."
        else:
            durum, p_adi, p_icerik = "Fazla Kilolu", "Definasyon", PROGRAMLAR[
                "Definasyon (Yağ Yakımı)"]; tavsiye = "Kalori açığı oluştur."
        if yas > 50: tavsiye += "\n(Eklemleri yormayan hareketler.)"

        try:
            conn = get_db_connection();
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET training_program=? WHERE id=?", (p_icerik, self.aktif_kullanici.id))
            conn.commit()
            cursor.execute("SELECT * FROM Users WHERE id=?", (self.aktif_kullanici.id,))
            self.aktif_kullanici = cursor.fetchone()
            conn.close()
            self.txt_sonuc.delete("1.0", END)
            self.txt_sonuc.insert(END,
                                  f"DURUM: {durum} (VKE: {vke:.1f})\n{tavsiye}\n" + "-" * 40 + f"\nPROGRAM: {p_adi}\n\n{p_icerik}")
            messagebox.showinfo("Başarılı", "Programın kaydedildi!")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    # ------------------------------------------------------------------------------
    def admin_paneli(self):
        self.temizle()
        self.pencere.config(bg="black")
        m = Menu(self.pencere);
        self.pencere.config(menu=m)
        m.add_command(label="Çıkış", command=self.giris_sayfasi)

        Label(self.pencere, text="YÖNETİCİ KONTROL PANELİ", font=("Segoe UI", 22, "bold"), fg="#e74c3c",
                bg="black").grid(row=0, column=0, pady=15)


        main_frame = Frame(self.pencere, bg="black")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)


        f_left = LabelFrame(main_frame, text=" Kayıtlı Üye Listesi ", font=self.font_buton, bg="black", fg="white")
        f_left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tree = ttk.Treeview(f_left, columns=("ID", "Ad", "Soyad"), show='headings')
        for col in ("ID", "Ad", "Soyad"): self.tree.heading(col, text=col); self.tree.column(col, width=50)
        self.tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.admin_secim)


        self.lbl_uye_sayisi = Label(f_left, text="Toplam Üye: 0", font=("Segoe UI", 11, "bold"), bg="black",
                                        fg="#f1c40f")
        self.lbl_uye_sayisi.pack(pady=5)


        f_mid = LabelFrame(main_frame, text=" Seçili Üye İşlemleri ", font=self.font_buton, bg="black", fg="white")
        f_mid.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.admin_profil_frame = Frame(f_mid, bg="#333", width=160, height=160, highlightbackground="white",
                                            highlightthickness=1)
        self.admin_profil_frame.pack(pady=20)
        self.admin_profil_frame.pack_propagate(False)
        self.lbl_admin_profil = Label(self.admin_profil_frame, text="Fotoğraf\nYok", bg="#333", fg="white")
        self.lbl_admin_profil.pack(fill=BOTH, expand=True)


        form_box = Frame(f_mid, bg="black")
        form_box.pack(pady=20)

        Label(form_box, text="Ad:", font=self.font_normal, bg="black", fg="white").grid(row=0, column=0, sticky="e",
                                                                                            pady=5)
        self.ed_ad = Entry(form_box, font=self.font_normal, width=20, bg="#333", fg="white",
                               insertbackground="white")
        self.ed_ad.grid(row=0, column=1, pady=5, padx=10)

        Label(form_box, text="Soyad:", font=self.font_normal, bg="black", fg="white").grid(row=1, column=0,sticky="e", pady=5)
        self.ed_soyad = Entry(form_box, font=self.font_normal, width=20, bg="#333", fg="white",
                                  insertbackground="white")
        self.ed_soyad.grid(row=1, column=1, pady=5, padx=10)

        Label(form_box, text="Süre Ekle (Gün):", font=self.font_normal, bg="black", fg="white").grid(row=2, column=0, sticky="e", pady=5)
        self.ed_gun = Entry(form_box, font=self.font_normal, width=20, bg="#333", fg="white",insertbackground="white")
        self.ed_gun.grid(row=2, column=1, pady=5, padx=10)

        Label(form_box, text="Ücret (TL):", font=self.font_normal, bg="black", fg="white").grid(row=3, column=0,
                                                                                                    sticky="e", pady=5)
        self.ed_fiyat = Entry(form_box, font=self.font_normal, width=20, bg="#333", fg="white",
                                  insertbackground="white")
        self.ed_fiyat.grid(row=3, column=1, pady=5, padx=10)


        Label(form_box, text="Telefon:", font=self.font_normal, bg="black", fg="white").grid(row=4, column=0,
                                                                                                 sticky="e", pady=5)
        self.ed_tel = Entry(form_box, font=self.font_normal, width=20, bg="#333", fg="white",
                                insertbackground="white")
        self.ed_tel.grid(row=4, column=1, pady=5, padx=10)

        btn_frame = Frame(f_mid, bg="black")
        btn_frame.pack(pady=20)
        Button(btn_frame, text="GÜNCELLE & SÜRE EKLE", bg="orange", font=self.font_buton, width=22,
                   command=self.admin_guncelle).pack(pady=5)
        Button(btn_frame, text="SİL", bg="red", fg="white", font=self.font_buton, width=22,
                command=self.admin_sil).pack(pady=5)

        self.admin_yukle()

    def admin_yukle(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = get_db_connection();
        cursor = conn.cursor()


        cursor.execute("SELECT id, name, surname FROM Users WHERE role='user'")
        rows = cursor.fetchall()
        for r in rows: self.tree.insert("", "end", values=tuple(r))


        cursor.execute("SELECT COUNT(*) FROM Users WHERE role='user'")
        sayi = cursor.fetchone()[0]
        self.lbl_uye_sayisi.config(text=f"Toplam Üye Sayısı: {sayi}")

        conn.close()

    def admin_secim(self, e):
        item = self.tree.selection()
        if not item: return
        uid = self.tree.item(item)['values'][0]

        conn = get_db_connection();
        cursor = conn.cursor()
        cursor.execute("SELECT name, surname, expiry_date, fee, profile_pic, phone FROM Users WHERE id=?", (uid,))
        r = cursor.fetchone();
        conn.close()

        bitis_tarihi = r[2]
        if isinstance(bitis_tarihi, str):
            try:
                bitis_tarihi = datetime.strptime(bitis_tarihi, "%Y-%m-%d").date()
            except:
                bitis_tarihi = None

        if bitis_tarihi:
            kalan = (bitis_tarihi - date.today()).days
        else:
            kalan = 0

        self.ed_ad.delete(0, END);
        self.ed_ad.insert(0, r[0])
        self.ed_soyad.delete(0, END);
        self.ed_soyad.insert(0, r[1])
        self.ed_gun.delete(0, END);
        self.ed_gun.insert(0, kalan)
        self.ed_fiyat.delete(0, END);
        self.ed_fiyat.insert(0, r[3])


        self.ed_tel.delete(0, END)
        self.ed_tel.insert(0, r[5] if r[5] else "")

        if r[4]:
            self.resmi_goster(r[4], self.lbl_admin_profil)
        else:
            self.lbl_admin_profil.config(image="", text="Fotoğraf\nYok")

    def admin_guncelle(self):
        item = self.tree.selection()
        if not item: messagebox.showwarning("Uyarı", "Lütfen listeden bir üye seçiniz."); return
        uid = self.tree.item(item)['values'][0]

        try:
            gun_girisi = self.ed_gun.get().strip()
            fiyat_girisi = self.ed_fiyat.get().strip().replace(',', '.')
            if not gun_girisi or not fiyat_girisi: messagebox.showwarning("Uyarı","Gün ve Fiyat alanları boş bırakılamaz."); return

            yeni_gun_sayisi = int(gun_girisi)
            ucret = float(fiyat_girisi)
            yeni_bitis_obj = date.today() + timedelta(days=yeni_gun_sayisi)
            yeni_bitis_str = yeni_bitis_obj.strftime('%Y-%m-%d')

            conn = get_db_connection();
            cursor = conn.cursor()


            cursor.execute("UPDATE Users SET name=?, surname=?, expiry_date=?, fee=?, phone=? WHERE id=?",
                               (self.ed_ad.get(), self.ed_soyad.get(), yeni_bitis_str, ucret, self.ed_tel.get(), uid))

            conn.commit();
            conn.close()
            messagebox.showinfo("Başarılı", "Üye bilgileri güncellendi.")
            self.admin_yukle()
        except ValueError:
            messagebox.showerror("Format Hatası", "Lütfen 'Gün' kısmına tam sayı,\n'Ücret' kısmına sayı giriniz.")
        except Exception as e:
            messagebox.showerror("Sistem Hatası", f"Hata Detayı:\n{e}")

    def admin_sil(self):
        item = self.tree.selection()
        if not item: return
        uid = self.tree.item(item)['values'][0]
        if messagebox.askyesno("Onay", "Silinsin mi?"):
            conn = get_db_connection();
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Users WHERE id=?", (uid,));
            conn.commit();
            conn.close()
            self.admin_yukle()
            self.ed_ad.delete(0, END);
            self.ed_soyad.delete(0, END);
            self.ed_gun.delete(0, END);
            self.ed_fiyat.delete(0, END)
            self.lbl_admin_profil.config(image="", text="Fotoğraf\nYok")


if __name__ == "__main__":
    root = Tk()
    SporSistemiPro(root)
    root.mainloop()