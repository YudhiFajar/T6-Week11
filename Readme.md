# Tugas 5 - Threading & REST API

**Nama:** Yudhi Fajar Pratama  
**NIM:** F1D02310142  

## Deskripsi Tugas
Aplikasi Desktop "Post Manager" yang dibangun menggunakan Python dan PySide6. Aplikasi ini terhubung dengan layanan REST API untuk mengelola data postingan (CRUD).

## Fitur Utama
1. **CRUD Lengkap:**
   - **GET:** Menampilkan daftar postingan dalam tabel.
   - **POST:** Menambah postingan baru melalui dialog form.
   - **PUT:** Mengubah data postingan yang sudah ada.
   - **DELETE:** Menghapus postingan dengan konfirmasi.
2. **Multi-threading:** Semua permintaan jaringan (network requests) dijalankan di thread terpisah menggunakan `QThread` agar antarmuka pengguna (UI) tetap responsif dan tidak membeku (freeze).
3. **Detail Panel:** Menampilkan detail lengkap postingan dan komentar terkait saat sebuah baris di tabel dipilih.
4. **Error Handling:** Menangani kesalahan koneksi, timeout, dan validasi server (seperti slug unik).

## Cara Menjalankan
1. Pastikan Python sudah terinstal.
2. Instal dependensi yang diperlukan:
   ```bash
   pip install PySide6 requests
   ```
3. Jalankan aplikasi:
   ```bash
   python post_manager.py
   ```

## Hasil Screenshot
![Screenshot](screenshot(1).png)
![Screenshot](screenshot(2).png)
![Screenshot](screenshot(3).png)
