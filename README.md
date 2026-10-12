# 🌌 NEBULAHEART 3D (Space Gesture Controller)

Aplikasi interaktif visualisasi 3D real-time yang mengontrol gerakan dan formasi 1.500 partikel kosmis menggunakan kecerdasan buatan (AI) pelacak tangan berbasis visi komputer.

---

## ⚙️ Teknologi Utama (Tech Stack)
* **Python 3.11** - Lingkungan eksekusi stabil
* **Pygame** - Mengatur jendela aplikasi, input keyboard, dan frame-rate (60 FPS)
* **PyOpenGL** - Akses kartu grafis (GPU) untuk render 3D partikel kosmis secara real-time
* **MediaPipe (0.10.14)** - AI pelacak 21 titik koordinat kerangka tangan
* **OpenCV (cv2)** - Akses webcam, pemrosesan frame video, dan tampilan monitor tracking
* **NumPy 1.26.4** - Komputasi matriks kilat untuk kalkulasi posisi rumus matematika 3D

---

## 🎛️ Panduan Kontrol Gestur Tangan (Mapped Gestures)

| Jari Tangan | Mode | Nama Mode | Efek Visual Partikel |
| :--- | :---: | :--- | :--- |
| 🖐️ **Terbuka Lebar** | **1** | **ROTASI ANGCOSMOS** | Partikel biru acak berputar lambat |
| ☝️ **1 Telunjuk Tegak** | **2** | **SATURNUS 3D** | Mengumpul jadi bola oranye & cincin emas |
| ✌️ **2 Jari (Peace Sign)** | **3** | **TEKS I LOVE YOU** | Berbaris membentuk tulisan biru neon |
| ✊ **Kepal / Genggam Tangan** | **4** | **BENTUK HATI (LOVE)** | Mengalir membentuk ikon hati pink tajam |

---

## 🚀 Panduan Instalasi & Eksekusi

### 1. Buat dan Aktifkan Lingkungan Conda
```bash
conda create -n space_gesture python=3.11 -y
conda activate space_gesture
```

### 2. Pasang Pustaka yang Diperlukan
```bash
pip install opencv-python "mediapipe==0.10.14" pygame PyOpenGL "numpy==1.26.4"
```

### 3. Jalankan Aplikasi
```bash
python index.py
# atau
python nebula.py
```

> **Catatan untuk macOS:** Jika aplikasi freeze karena aturan Main Thread GUI Mac, gunakan `pythonw index.py`.
