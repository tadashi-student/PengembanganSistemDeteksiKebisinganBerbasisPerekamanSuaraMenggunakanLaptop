penjelasan kurang detail

# Pengembangan Sistem Deteksi Kebisingan Berbasis Perekaman Suara Menggunakan Laptop
Aplikasi GUI untuk merekam audio, menganalisis sinyal dalam domain waktu dan frekuensi, serta mengklasifikasikan kebisingan. Mendukung penyimpanan audio ke format .wav, visualisasi sinyal real-time, dan pengunggahan ke Edge Impulse untuk analisis machine learning.

Proyek ini adalah sebuah aplikasi berbasis GUI yang dirancang untuk merekam audio, memproses sinyal dalam domain waktu dan frekuensi, serta mengklasifikasikan tingkat kebisingan berdasarkan analisis desibel rata-rata. Selain itu, aplikasi ini mendukung penyimpanan rekaman ke dalam format .wav dan pengunggahan ke platform Edge Impulse untuk kebutuhan analisis lebih lanjut.

Fitur Utama
- Rekaman Audio: Merekam audio melalui mikrofon dengan sampling rate default 44.1 kHz.
- Visualisasi Sinyal:
  a. Domain Waktu: Menampilkan amplitudo sinyal terhadap waktu.
  b. Domain Frekuensi: Menampilkan hasil transformasi Fourier untuk analisis frekuensi.
- Klasifikasi Kebisingan: Menghitung desibel rata-rata sinyal untuk menentukan apakah sinyal termasuk "Bising" atau "Tidak Bising".
- Simpan dan Putar Kembali Rekaman: Menyimpan rekaman sebagai file .wav dan memutar ulang hasil rekaman.
- Pengunggahan ke Edge Impulse: Mengunggah file audio dengan label klasifikasi ke platform Edge Impulse untuk keperluan machine learning atau analisis lanjutan.

Langkah Pembuatan GUI dengan Qt :
1. Desain Antarmuka
   - Gunakan Qt Designer untuk membuat file .ui dengan elemen seperti tombol, label, dan area plot.
2. Konversi ke Python
   - Konversi file .ui ke file Python menggunakan perintah: pyuic5 main.ui -o main.py
3. Integrasi dengan Matplotlib
   - Gunakan FigureCanvas dari Matplotlib untuk menampilkan grafik domain waktu dan frekuensi di dalam GUI.

Mengintegrasikan dengan Edge Impulse
1. Buat akun di Edge Impulse dan buat proyek baru.
2. Salin API Key dari proyek Edge Impulse kamu.
3. Masukkan API Key ke dalam variabel self.api_key di kode program.
4. Tekan tombol Save setelah merekam untuk mengunggah data ke Edge Impulse.

Cara Kerja
1. Rekaman Audio:
   a. Klik tombol Record untuk memulai rekaman.
   b. Klik tombol Stop untuk menghentikan rekaman.
2. Visualisasi : Domain waktu dan frekuensi diperbarui secara langsung selama proses rekaman.
3. Klasifikasi Kebisingan : Setelah merekam, hasil klasifikasi akan ditampilkan berdasarkan nilai desibel rata-rata.
4. Simpan dan Unggah:
   a. Klik tombol Save untuk menyimpan file audio ke dalam folder recordings/.
   b. File yang disimpan secara otomatis dapat diunggah ke Edge Impulse dengan klik Save.

Catatan Penting
- Aplikasi ini mengandalkan API Edge Impulse untuk klasifikasi. Pastikan koneksi internet tersedia saat mengunggah data.
- Format file audio yang disimpan adalah .wav dengan satu kanal (mono).
