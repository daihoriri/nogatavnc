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
    
    def __init__(self, name: str, ip_address: str, port: int = 5900, password: str = ''):
        self.name = name
        self.ip_address = ip_address
        self.port = port
        self.password = password
    
    def to_dict(self):
        return {
            'name': self.name,
            'ip_address': self.ip_address,
            'port': self.port,
            'password': self.password
        }
    
    @staticmethod
    def from_dict(data: dict):
        return Room(
            data['name'],
            data['ip_address'],
            data.get('port', 5900),
            data.get('password', '')
        )


class ConfigManager:
    """設定管理クラス"""
    
    @staticmethod
    def get_config_dir():
        """設定ファイルのディレクトリを取得（exeファイルと同じ場所）"""
        if getattr(sys, 'frozen', False):
            # PyInstallerでパッケージ化されている場合
            return os.path.dirname(sys.executable)
        else:
            # 開発環境での実行時
            return os.path.dirname(os.path.abspath(__file__))
    
    @staticmethod
    def get_config_path():
        """設定ファイルのパスを取得"""
        return os.path.join(ConfigManager.get_config_dir(), 'config.json')
    
    @staticmethod
    def get_default_rooms():
        """デフォルトの診察室情報を返す"""
        return [
            Room('診察室1', '192.168.1.10', 5900),
            Room('診察室2', '192.168.1.11', 5900),
            Room('診察室3', '192.168.1.12', 5900),
            Room('診察室4', '192.168.1.13', 5900),
        ]
    
    @staticmethod
    def load_config():
        """設定ファイルを読み込む"""
        config_path = ConfigManager.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f'設定ファイルの読み込みに失敗: {e}')
                return {}
        return {}
    
    @staticmethod
    def save_config(config):
        """設定ファイルを保存"""
        config_path = ConfigManager.get_config_path()
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'設定ファイルの保存に失敗: {e}')
    
    @staticmethod
    def load_rooms():
        """診察室情報を読み込む"""
        config = ConfigManager.load_config()
        rooms_data = config.get('rooms', [])
        
        if not rooms_data:
            # デフォルトの診察室情報を返す
            return ConfigManager.get_default_rooms()
        
        rooms = []
        for room_data in rooms_data:
            rooms.append(Room(
                room_data.get('name', ''),
                room_data.get('ip_address', ''),
                room_data.get('port', 5900),
                room_data.get('password', '')
            ))
        return rooms
    
    @staticmethod
    def save_rooms(rooms):
        """診察室情報を保存"""
        config = ConfigManager.load_config()
        rooms_data = []
        for room in rooms:
            rooms_data.append({
                'name': room.name,
                'ip_address': room.ip_address,
                'port': room.port,
                'password': room.password
            })
        config['rooms'] = rooms_data
        ConfigManager.save_config(config)
    
    @staticmethod
    def load_ultravnc_path():
        """UltraVNCパスを読み込む"""
        config = ConfigManager.load_config()
        return config.get('ultravnc_path', '')
    
    @staticmethod
    def save_ultravnc_path(path):
        """UltraVNCパスを保存"""
        config = ConfigManager.load_config()
        config['ultravnc_path'] = path
        ConfigManager.save_config(config)


class VNCConnector:
    """VNC接続を管理するクラス"""
    
    @staticmethod
    def get_viewer_path():
        """UltraVNC Viewerのパスを取得"""
        # 設定ファイルからパスを取得
        custom_path = ConfigManager.load_ultravnc_path()
        if custom_path and os.path.exists(custom_path):
            return custom_path
        
        # デフォルトパス
        default_path = r"C:\Program Files\uvnc bvba\UltraVNC\vncviewer.exe"
        if os.path.exists(default_path):
            return default_path
        
        # 別の一般的なパスも確認
        alt_path = r"C:\Program Files (x86)\uvnc bvba\UltraVNC\vncviewer.exe"
        if os.path.exists(alt_path):
            return alt_path
        
        return None
    
    @staticmethod
    def connect(room):
        """UltraVNCビューアーでリモート接続"""
        try:
            viewer_path = VNCConnector.get_viewer_path()
            
            if not viewer_path:
                # macOSの場合（開発環境用）
                if sys.platform == 'darwin':
                    return True
                raise FileNotFoundError(f"UltraVNCビューアーが見つかりません: {viewer_path}")
            
            # VNC接続コマンド実行（パスワード付き）
            connection_str = f"{room.ip_address}:{room.port}"
            if room.password:
                subprocess.Popen([viewer_path, connection_str, '-password', room.password])
            else:
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
        self.geometry('400x270')
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
        self.port_input.pack(fill=tk.X, pady=(0, 10))
        if self.room:
            self.port_input.insert(0, str(self.room.port))
        else:
            self.port_input.insert(0, '5900')
        
        # パスワード
        ttk.Label(main_frame, text='VNCパスワード (省略可):').pack(anchor=tk.W, pady=(0, 5))
        self.password_input = ttk.Entry(main_frame, width=40, show='*')
        self.password_input.pack(fill=tk.X, pady=(0, 15))
        if self.room:
            self.password_input.insert(0, self.room.password)
        
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
            port,
            self.password_input.get()
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
        # 診察室情報を読み込む（config.jsonから、なければデフォルト）
        self.rooms = ConfigManager.load_rooms()
        
        # 初回起動時にデフォルト設定を保存
        if not os.path.exists(ConfigManager.get_config_path()):
            ConfigManager.save_rooms(self.rooms)
        
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
        """診察室情報をリストに表示"""
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
            # 接続処理を別スレッドで実行し、メッセージボックスを自動閉じ
            self.show_connection_message(room)
        except Exception as e:
            messagebox.showerror(
                'エラー',
                f'接続に失敗しました:\n{str(e)}'
            )
    
    def show_connection_message(self, room):
        """接続中メッセージを表示して自動閉じ"""
        import threading
        import time
        
        # メッセージウィンドウを作成
        msg_window = tk.Toplevel(self)
        msg_window.title('接続中')
        msg_window.geometry('300x100')
        msg_window.resizable(False, False)
        msg_window.transient(self)
        msg_window.grab_set()
        
        # メッセージラベル
        label = ttk.Label(
            msg_window,
            text=f'{room.name}\n({room.ip_address})\nに接続しています...',
            font=('', 11)
        )
        label.pack(expand=True)
        
        # 2秒後に自動閉じ
        def auto_close():
            time.sleep(2)
            try:
                msg_window.destroy()
            except:
                pass
        
        thread = threading.Thread(target=auto_close, daemon=True)
        thread.start()
    
    def on_settings(self):
        """設定ボタンクリック時"""
        # 操作選択ダイアログ
        dialog = tk.Toplevel(self)
        dialog.title('設定')
        dialog.geometry('300x220')
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
            elif action == 'ultravnc':
                self.set_ultravnc_path()
        
        ttk.Button(dialog, text='新規追加', command=lambda: on_choice('add')).pack(fill=tk.X, padx=20, pady=5)
        ttk.Button(dialog, text='編集', command=lambda: on_choice('edit')).pack(fill=tk.X, padx=20, pady=5)
        ttk.Button(dialog, text='削除', command=lambda: on_choice('delete')).pack(fill=tk.X, padx=20, pady=5)
        ttk.Separator(dialog, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=5)
        ttk.Button(dialog, text='UltraVNCパス設定', command=lambda: on_choice('ultravnc')).pack(fill=tk.X, padx=20, pady=5)
    
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
    
    def set_ultravnc_path(self):
        """UltraVNCビューアーのパスを設定"""
        # 現在の設定パスを取得
        current_path = ConfigManager.load_ultravnc_path()
        
        # パス入力ダイアログ
        dialog = tk.Toplevel(self)
        dialog.title('UltraVNCパス設定')
        dialog.geometry('500x200')
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text='UltraVNCビューアーのパスを入力してください', font=('', 10)).pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(main_frame, text='例: C:\\Program Files\\uvnc bvba\\UltraVNC\\vncviewer.exe', font=('', 9), foreground='gray').pack(anchor=tk.W, pady=(0, 5))
        
        # パス入力フィールド
        ttk.Label(main_frame, text='パス:').pack(anchor=tk.W, pady=(0, 5))
        path_input = ttk.Entry(main_frame, width=60)
        path_input.pack(fill=tk.X, pady=(0, 15))
        if current_path:
            path_input.insert(0, current_path)
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def on_ok():
            path = path_input.get().strip()
            if path:
                ConfigManager.save_ultravnc_path(path)
                messagebox.showinfo('成功', 'UltraVNCパスを設定しました')
                dialog.destroy()
            else:
                ConfigManager.save_ultravnc_path('')
                messagebox.showinfo('成功', 'UltraVNCパスをリセットしました（デフォルトパスを使用）')
                dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        def on_reset():
            path_input.delete(0, tk.END)
        
        ttk.Button(button_frame, text='OK', command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='キャンセル', command=on_cancel).pack(side=tk.LEFT)
        ttk.Button(button_frame, text='リセット', command=on_reset).pack(side=tk.LEFT, padx=50)


def main():
    """メイン関数"""
    app = MainWindow()
    app.mainloop()


if __name__ == '__main__':
    main()
