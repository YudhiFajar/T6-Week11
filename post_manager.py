"""
Nama: Yudhi Fajar Pratama
NIM: F1D02310142
Tugas 5 - Threading & REST API
"""

import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QTextEdit, QFormLayout, QDialog, QMessageBox, QHeaderView,
    QStatusBar, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, Slot

API_BASE_URL = "https://api.pahrul.my.id/api/posts"

class WorkerThread(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except requests.exceptions.RequestException as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(str(e))

class PostFormDialog(QDialog):
    def __init__(self, parent=None, post_data=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Post" if post_data is None else "Edit Post")
        self.setMinimumWidth(400)
        
        self.layout = QFormLayout(self)
        
        self.title_input = QLineEdit()
        self.body_input = QTextEdit()
        self.author_input = QLineEdit()
        self.slug_input = QLineEdit()
        self.status_input = QLineEdit()
        self.status_input.setPlaceholderText("published / draft")
        
        if post_data:
            self.title_input.setText(post_data.get('title', ''))
            self.body_input.setPlainText(post_data.get('body', ''))
            self.author_input.setText(post_data.get('author', ''))
            self.slug_input.setText(post_data.get('slug', ''))
            self.status_input.setText(post_data.get('status', ''))
            
        self.layout.addRow("Title:", self.title_input)
        self.layout.addRow("Body:", self.body_input)
        self.layout.addRow("Author:", self.author_input)
        self.layout.addRow("Slug:", self.slug_input)
        self.layout.addRow("Status:", self.status_input)
        
        self.submit_btn = QPushButton("Simpan")
        self.submit_btn.clicked.connect(self.accept)
        self.layout.addRow(self.submit_btn)

    def get_data(self):
        return {
            "title": self.title_input.text(),
            "body": self.body_input.toPlainText(),
            "author": self.author_input.text(),
            "slug": self.slug_input.text(),
            "status": self.status_input.text()
        }

class PostManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Post Manager - Tugas 5 Threading & REST API")
        self.resize(1000, 600)
        
        self.setup_ui()
        self.load_posts()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left Side: Table and Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Author", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.load_posts)
        self.btn_add = QPushButton("Tambah Post")
        self.btn_add.clicked.connect(self.add_post)
        self.btn_edit = QPushButton("Edit Post")
        self.btn_edit.setEnabled(False)
        self.btn_edit.clicked.connect(self.edit_post)
        self.btn_delete = QPushButton("Hapus Post")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self.delete_post)
        
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        left_layout.addLayout(btn_layout)
        
        main_layout.addWidget(left_panel, 2)
        
        # Right Side: Detail Panel
        self.detail_panel = QFrame()
        self.detail_panel.setFrameShape(QFrame.StyledPanel)
        detail_layout = QVBoxLayout(self.detail_panel)
        
        detail_layout.addWidget(QLabel("<b>Detail Post</b>"))
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text)
        
        detail_layout.addWidget(QLabel("<b>Comments</b>"))
        self.comments_text = QTextEdit()
        self.comments_text.setReadOnly(True)
        detail_layout.addWidget(self.comments_text)
        
        main_layout.addWidget(self.detail_panel, 1)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def show_loading(self, message="Loading..."):
        self.status_bar.showMessage(message)
        self.setCursor(Qt.WaitCursor)
        self.setEnabled_all(False)

    def hide_loading(self):
        self.status_bar.clearMessage()
        self.setCursor(Qt.ArrowCursor)
        self.setEnabled_all(True)
        self.on_selection_changed() # Update button states

    def setEnabled_all(self, enabled):
        self.btn_refresh.setEnabled(enabled)
        self.btn_add.setEnabled(enabled)
        self.table.setEnabled(enabled)

    def on_selection_changed(self):
        selected = self.table.selectedItems()
        if selected:
            self.btn_edit.setEnabled(True)
            self.btn_delete.setEnabled(True)
            row = selected[0].row()
            post_id = self.table.item(row, 0).text()
            self.load_detail(post_id)
        else:
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.detail_text.clear()
            self.comments_text.clear()

    def load_posts(self):
        self.show_loading("Mengambil data posts...")
        self.worker = WorkerThread(requests.get, API_BASE_URL, timeout=10)
        self.worker.finished.connect(self.on_posts_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_posts_loaded(self, response):
        self.hide_loading()
        if response.status_code == 200:
            posts = response.json().get('data', [])
            self.table.setRowCount(0)
            for post in posts:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(post['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(post['title']))
                self.table.setItem(row, 2, QTableWidgetItem(post['author']))
                self.table.setItem(row, 3, QTableWidgetItem(post['status']))
        else:
            QMessageBox.critical(self, "Error", f"Gagal mengambil data: {response.status_code}")

    def load_detail(self, post_id):
        self.status_bar.showMessage(f"Mengambil detail post {post_id}...")
        self.worker_detail = WorkerThread(requests.get, f"{API_BASE_URL}/{post_id}", timeout=10)
        self.worker_detail.finished.connect(self.on_detail_loaded)
        self.worker_detail.error.connect(self.on_error)
        self.worker_detail.start()

    def on_detail_loaded(self, response):
        self.status_bar.clearMessage()
        if response.status_code == 200:
            post = response.json().get('data', {})
            comments = post.get('comments', [])
            
            detail = f"ID: {post.get('id')}\n"
            detail += f"Title: {post.get('title')}\n"
            detail += f"Slug: {post.get('slug')}\n"
            detail += f"Author: {post.get('author')}\n"
            detail += f"Status: {post.get('status')}\n\n"
            detail += f"Body:\n{post.get('body')}"
            self.detail_text.setText(detail)
            
            comm_text = ""
            for c in comments:
                comm_text += f"- {c.get('body')} (by {c.get('name')})\n"
            self.comments_text.setText(comm_text if comm_text else "No comments.")
        else:
            self.detail_text.setText("Gagal mengambil detail.")

    def add_post(self):
        dialog = PostFormDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.show_loading("Menambah post...")
            self.worker = WorkerThread(requests.post, API_BASE_URL, json=data, timeout=10)
            self.worker.finished.connect(self.on_post_added)
            self.worker.error.connect(self.on_error)
            self.worker.start()

    def on_post_added(self, response):
        self.hide_loading()
        if response.status_code == 201:
            new_id = response.json().get('data', {}).get('id')
            QMessageBox.information(self, "Sukses", f"Post berhasil ditambah dengan ID: {new_id}")
            self.load_posts()
        elif response.status_code == 422:
            errors = response.json().get('errors', {})
            msg = "Validasi Gagal:\n"
            for field, m in errors.items():
                msg += f"- {field}: {', '.join(m)}\n"
            QMessageBox.warning(self, "Validasi", msg)
        else:
            QMessageBox.critical(self, "Error", f"Gagal menambah post: {response.status_code}\n{response.text}")

    def edit_post(self):
        selected = self.table.selectedItems()
        if not selected: return
        row = selected[0].row()
        post_id = self.table.item(row, 0).text()
        
        # We need the current data, let's fetch it first or use what's in detail
        # For simplicity, I'll use a worker to get detail first then show dialog, 
        # but to keep it responsive, I'll just parse the detail_text or fetch again.
        # Let's fetch again to be sure.
        self.show_loading("Mengambil data untuk diedit...")
        self.worker = WorkerThread(requests.get, f"{API_BASE_URL}/{post_id}", timeout=10)
        self.worker.finished.connect(lambda r: self.show_edit_dialog(r, post_id))
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def show_edit_dialog(self, response, post_id):
        self.hide_loading()
        if response.status_code == 200:
            post_data = response.json().get('data', {})
            dialog = PostFormDialog(self, post_data)
            if dialog.exec():
                data = dialog.get_data()
                self.show_loading("Mengupdate post...")
                self.worker = WorkerThread(requests.put, f"{API_BASE_URL}/{post_id}", json=data, timeout=10)
                self.worker.finished.connect(self.on_post_updated)
                self.worker.error.connect(self.on_error)
                self.worker.start()
        else:
            QMessageBox.critical(self, "Error", "Gagal mengambil data post.")

    def on_post_updated(self, response):
        self.hide_loading()
        if response.status_code == 200:
            QMessageBox.information(self, "Sukses", "Post berhasil diupdate.")
            self.load_posts()
        elif response.status_code == 422:
            errors = response.json().get('errors', {})
            msg = "Validasi Gagal:\n"
            for field, m in errors.items():
                msg += f"- {field}: {', '.join(m)}\n"
            QMessageBox.warning(self, "Validasi", msg)
        else:
            QMessageBox.critical(self, "Error", f"Gagal update post: {response.status_code}")

    def delete_post(self):
        selected = self.table.selectedItems()
        if not selected: return
        row = selected[0].row()
        post_id = self.table.item(row, 0).text()
        
        reply = QMessageBox.question(self, "Konfirmasi", f"Hapus post ID {post_id}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.show_loading("Menghapus post...")
            self.worker = WorkerThread(requests.delete, f"{API_BASE_URL}/{post_id}", timeout=10)
            self.worker.finished.connect(self.on_post_deleted)
            self.worker.error.connect(self.on_error)
            self.worker.start()

    def on_post_deleted(self, response):
        self.hide_loading()
        if response.status_code in [200, 204]:
            QMessageBox.information(self, "Sukses", "Post berhasil dihapus.")
            self.load_posts()
        else:
            QMessageBox.critical(self, "Error", f"Gagal menghapus post: {response.status_code}")

    def on_error(self, message):
        self.hide_loading()
        QMessageBox.critical(self, "Network Error", f"Terjadi kesalahan: {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PostManagerApp()
    window.show()
    sys.exit(app.exec())
