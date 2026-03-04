"""
VNC Remote Desktop Application
医療施設内のUltraVNCサーバーに接続するデスクトップアプリケーション
"""

import json
import subprocess
import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


class Room:
    """診察室情報を管理するクラス"""
    
    def __init__(self, name: str, ip_address: str, port: int = 5900):
        self.name = name
        self.ip_address = ip_address
        self.port = port
    
    def to_dict(self):
        return {
            'name': self.name,
            'ip_address': self.ip_address,
            'port': self.port
        }
    
    @staticmethod
    def from_dict(data: dict):
        return Room(
            data['name'],
            data['ip_address'],
            data.get('port', 5900)
        )


class ConfigManager:
    """config.jsonファイルを管理するクラス"""
    
    CONFIG_FILE = 'config.json'
    
    @staticmethod
    def get_config_path():
        """設定ファイルのパスを取得"""
        return Path(ConfigManager.CONFIG_FILE)
    
    @staticmethod
    def load_rooms():
        """設定ファイルから診察室情報を読み込む"""
        config_path = ConfigManager.get_config_path()
        
        if not config_path.exists():
            # デフォルト設定を作成
            default_rooms = [
                Room('診察室1', '192.168.1.10'),
                Room('診察室2', '192.168.1.20'),
                Room('診察室3', '192.168.1.30'),
                Room('診察室4', '192.168.1.40'),
            ]
            ConfigManager.save_rooms(default_rooms)
            return default_rooms
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Room.from_dict(room) for room in data]
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            return []
    
    @staticmethod
    def save_rooms(rooms):
        """診察室情報を設定ファイルに保存"""
        config_path = ConfigManager.get_config_path()
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                data = [room.to_dict() for room in rooms]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"設定ファイル保存エラー: {e}")


class VNCConnector:
    """VNC接続を管理するクラス"""
    
    @staticmethod
    def connect(room):
        """UltraVNCビューアーでリモート接続"""
        try:
            # UltraVNCビューアーの実行ファイルパスを検索
            ultraVNC_paths = [
                r"C:\Program Files\UltraVNC\vncviewer.exe",
                r"C:\Program Files (x86)\UltraVNC\vncviewer.exe",
                os.path.expandvars(r"%ProgramFiles%\UltraVNC\vncviewer.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\UltraVNC\vncviewer.exe"),
            ]
            
            viewer_path = None
            for path in ultraVNC_paths:
                if os.path.exists(path):
                    viewer_path = path
                    break
            
            if not viewer_path:
                # macOSの場合（開発環境用）
                if sys.platform == 'darwin':
                    return True
                raise FileNotFoundError("UltraVNCビューアーが見つかりません")
            
            # VNC接続コマンド実行
            connection_str = f"{room.ip_address}:{room.port}"
            subprocess.Popen([viewer_path, connection_str])
            return True
            
        except Exception as e:
            raise Exception(f"VNC接続エラー: {e}")


class SettingsDialog(tk.Toplevel):
    """設定ダイアログクラス"""
    
    def __init__(self, parent, room=None):
        super().__init__(parent)
        self.room = room
        self.result = None
        self.init_ui()
    
    def init_ui(self):
        """UIの初期化"""
        self.title('診察室設定')
        self.geometry('400x220')
        self.resizable(False, False)
        
        # モーダルダイアログにする
        self.transient(self.master)
        self.grab_set()
        
        # メインフレーム
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 診察室名
        ttk.Label(main_frame, text='診察室名:').pack(anchor=tk.W, pady=(0, 5))
        self.name_input = ttk.Entry(main_frame, width=40)
        self.name_input.pack(fill=tk.X, pady=(0, 10))
        if self.room:
            self.name_input.insert(0, self.room.name)
        
        # IPアドレス
        ttk.Label(main_frame, text='IPアドレス:').pack(anchor=tk.W, pady=(0, 5))
        self.ip_input = ttk.Entry(main_frame, width=40)
        self.ip_input.pack(fill=tk.X, pady=(0, 10))
        if self.room:
            self.ip_input.insert(0, self.room.ip_address)
        
        # ポート番号
        ttk.Label(main_frame, text='ポート番号 (通常は5900):').pack(anchor=tk.W, pady=(0, 5))
        self.port_input = ttk.Entry(main_frame, width=40)
        self.port_input.pack(fill=tk.X, pady=(0, 15))
        if self.room:
            self.port_input.insert(0, str(self.room.port))
        else:
            self.port_input.insert(0, '5900')
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text='OK', command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='キャンセル', command=self.on_cancel).pack(side=tk.LEFT)
        
        # Enterキーで確定
        self.bind('<Return>', lambda e: self.on_ok())
        self.bind('<Escape>', lambda e: self.on_cancel())
    
    def on_ok(self):
        """OKボタンクリック時"""
        try:
            port = int(self.port_input.get())
        except ValueError:
            port = 5900
        
        self.result = Room(
            self.name_input.get(),
            self.ip_input.get(),
            port
        )
        self.destroy()
    
    def on_cancel(self):
        """キャンセルボタンクリック時"""
        self.result = None
        self.destroy()
    
    def get_room(self):
        """入力されたRoom情報を取得"""
        return self.result


class MainWindow(tk.Tk):
    """メインウィンドウクラス"""
    
    def __init__(self):
        super().__init__()
        self.rooms = []
        self.init_ui()
        self.load_rooms()
    
    def init_ui(self):
        """UIの初期化"""
        self.title('VNC リモートデスクトップ接続')
        self.geometry('500x450')
        
        # メインフレーム
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title = ttk.Label(
            main_frame, 
            text='接続する診察室を選択してください',
            font=('', 12, 'bold')
        )
        title.pack(pady=(0, 10))
        
        # 診察室リストフレーム
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 診察室リスト
        self.room_list = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('', 11),
            height=12
        )
        self.room_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.room_list.yview)
        
        self.room_list.bind('<<ListboxSelect>>', self.on_selection_changed)
        self.room_list.bind('<Double-Button-1>', lambda e: self.on_connect())
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.connect_button = ttk.Button(
            button_frame,
            text='接続',
            command=self.on_connect,
            state=tk.DISABLED
        )
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text='設定',
            command=self.on_settings
        ).pack(side=tk.LEFT)
    
    def load_rooms(self):
        """診察室情報を読み込んでリストに表示"""
        self.rooms = ConfigManager.load_rooms()
        self.room_list.delete(0, tk.END)
        
        for room in self.rooms:
            self.room_list.insert(tk.END, room.name)
    
    def on_selection_changed(self, event=None):
        """リスト選択変更時"""
        if self.room_list.curselection():
            self.connect_button.config(state=tk.NORMAL)
        else:
            self.connect_button.config(state=tk.DISABLED)
    
    def on_connect(self):
        """接続ボタンクリック時"""
        selection = self.room_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        room = self.rooms[index]
        
        try:
            VNCConnector.connect(room)
            messagebox.showinfo(
                '接続中',
                f'{room.name} ({room.ip_address}) に接続しています...'
            )
        except Exception as e:
            messagebox.showerror(
                'エラー',
                f'接続に失敗しました:\n{str(e)}'
            )
    
    def on_settings(self):
        """設定ボタンクリック時"""
        # 操作選択ダイアログ
        dialog = tk.Toplevel(self)
        dialog.title('設定')
        dialog.geometry('300x180')
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text='操作を選択してください:', font=('', 10)).pack(pady=10)
        
        def on_choice(action):
            dialog.destroy()
            if action == 'add':
                self.add_room()
            elif action == 'edit':
                self.edit_room()
            elif action == 'delete':
                self.delete_room()
        
        ttk.Button(dialog, text='新規追加', command=lambda: on_choice('add')).pack(fill=tk.X, padx=20, pady=5)
        ttk.Button(dialog, text='編集', command=lambda: on_choice('edit')).pack(fill=tk.X, padx=20, pady=5)
        ttk.Button(dialog, text='削除', command=lambda: on_choice('delete')).pack(fill=tk.X, padx=20, pady=5)
    
    def add_room(self):
        """新規診察室を追加"""
        dialog = SettingsDialog(self)
        self.wait_window(dialog)
        
        new_room = dialog.get_room()
        if new_room:
            if not new_room.name or not new_room.ip_address:
                messagebox.showwarning('警告', '診察室名とIPアドレスを入力してください')
                return
            
            self.rooms.append(new_room)
            ConfigManager.save_rooms(self.rooms)
            self.load_rooms()
            messagebox.showinfo('成功', f'{new_room.name} を追加しました')
    
    def edit_room(self):
        """診察室情報を編集"""
        selection = self.room_list.curselection()
        if not selection:
            messagebox.showwarning('警告', '編集する診察室を選択してください')
            return
        
        index = selection[0]
        room = self.rooms[index]
        
        dialog = SettingsDialog(self, room)
        self.wait_window(dialog)
        
        updated_room = dialog.get_room()
        if updated_room:
            if not updated_room.name or not updated_room.ip_address:
                messagebox.showwarning('警告', '診察室名とIPアドレスを入力してください')
                return
            
            # 既存の情報を更新
            self.rooms[index] = updated_room
            ConfigManager.save_rooms(self.rooms)
            self.load_rooms()
            messagebox.showinfo('成功', f'{updated_room.name} を更新しました')
    
    def delete_room(self):
        """診察室を削除"""
        selection = self.room_list.curselection()
        if not selection:
            messagebox.showwarning('警告', '削除する診察室を選択してください')
            return
        
        index = selection[0]
        room = self.rooms[index]
        
        result = messagebox.askyesno(
            '確認',
            f'{room.name} を削除してもよろしいですか？'
        )
        
        if result:
            self.rooms.remove(room)
            ConfigManager.save_rooms(self.rooms)
            self.load_rooms()
            messagebox.showinfo('成功', f'{room.name} を削除しました')


def main():
    """メイン関数"""
    app = MainWindow()
    app.mainloop()


if __name__ == '__main__':
    main()
