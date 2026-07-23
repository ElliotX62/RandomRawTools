import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name='scrapybot.db'):
        """Inisialisasi koneksi database"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()
    
    def connect(self):
        """Membuat koneksi ke database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def create_table(self):
        """Membuat tabel targets jika belum ada"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            return False
    
    def insert_target(self, url):
        """Menyimpan URL target ke database"""
        try:
            self.cursor.execute('''
                INSERT INTO targets (url, created_at, status)
                VALUES (?, ?, ?)
            ''', (url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'pending'))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting target: {e}")
            return None
    
    def get_all_targets(self):
        """Mengambil semua data targets"""
        try:
            self.cursor.execute('''
                SELECT id, url, created_at, status 
                FROM targets 
                ORDER BY created_at DESC
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching targets: {e}")
            return []
    
    def get_target_by_id(self, target_id):
        """Mengambil target berdasarkan ID"""
        try:
            self.cursor.execute('''
                SELECT id, url, created_at, status 
                FROM targets 
                WHERE id = ?
            ''', (target_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching target: {e}")
            return None
    
    def update_status(self, target_id, status):
        """Mengupdate status target"""
        try:
            self.cursor.execute('''
                UPDATE targets 
                SET status = ? 
                WHERE id = ?
            ''', (status, target_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating status: {e}")
            return False
    
    def delete_target(self, target_id):
        """Menghapus target berdasarkan ID"""
        try:
            self.cursor.execute('DELETE FROM targets WHERE id = ?', (target_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting target: {e}")
            return False
    
    def get_total_count(self):
        """Mendapatkan total jumlah target"""
        try:
            self.cursor.execute('SELECT COUNT(*) FROM targets')
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error getting count: {e}")
            return 0
    
    def delete_all_targets(self):
        """Menghapus semua target"""
        try:
            self.cursor.execute('DELETE FROM targets')
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting all targets: {e}")
            return False
    
    def close(self):
        """Menutup koneksi database"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Destructor untuk menutup koneksi"""
        self.close()
