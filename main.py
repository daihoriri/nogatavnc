"""
VNC Remote Desktop Application
医療施設内のUltraVNCサーバーに接続するデスクトップアプリケーション
"""

import sys
import json
import subprocess
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QDialog, QLabel,
    QLineEdit, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


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
    def load_rooms() -> list[Room]:
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
    def save_rooms(rooms: list[Room]):
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
    def connect(room: Room):
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
                    # スタブ実装
                    return True
                raise FileNotFoundError("UltraVNCビューアーが見つかりません")
            
            # VNC接続コマンド実行
            connection_str = f"{room.ip_address}:{room.port}"
            subprocess.Popen([viewer_path, connection_str])
            return True
            
        except Exception as e:
            raise Exception(f"VNC接続エラー: {e}")


class SettingsDialog(QDialog):
    """設定ダイアログクラス"""
    
    def __init__(self, parent=None, room: Room = None):
        super().__init__(parent)
        self.room = room
        self.init_ui()
    
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle('診察室設定')
        self.setGeometry(200, 200, 400, 200)
        
        layout = QVBoxLayout()
        
        # 診察室名
        layout.addWidget(QLabel('診察室名:'))
        self.name_input = QLineEdit()
        if self.room:
            self.name_input.setText(self.room.name)
        layout.addWidget(self.name_input)
        
        # IPアドレス
        layout.addWidget(QLabel('IPアドレス:'))
        self.ip_input = QLineEdit()
        if self.room:
            self.ip_input.setText(self.room.ip_address)
        layout.addWidget(self.ip_input)
        
        # ポート番号
        layout.addWidget(QLabel('ポート番号 (通常は5900):'))
        self.port_input = QLineEdit()
        if self.room:
            self.port_input.setText(str(self.room.port))
        else:
            self.port_input.setText('5900')
        layout.addWidget(self.port_input)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton('OK')
        cancel_button = QPushButton('キャンセル')
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_room(self) -> Room:
        """入力されたRoom情報を取得"""
        try:
            port = int(self.port_input.text())
        except ValueError:
            port = 5900
        
        return Room(
            self.name_input.text(),
            self.ip_input.text(),
            port
        )


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""
    
    def __init__(self):
        super().__init__()
        self.rooms: list[Room] = []
        self.init_ui()
        self.load_rooms()
    
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle('VNC リモートデスクトップ接続')
        self.setGeometry(100, 100, 500, 400)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # タイトル
        title = QLabel('接続する診察室を選択してください')
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # 診察室リスト
        self.room_list = QListWidget()
        self.room_list.itemSelectionChanged.connect(self.on_selection_changed)
        main_layout.addWidget(self.room_list)
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        
        self.connect_button = QPushButton('接続')
        self.connect_button.clicked.connect(self.on_connect)
        self.connect_button.setEnabled(False)
        button_layout.addWidget(self.connect_button)
        
        settings_button = QPushButton('設定')
        settings_button.clicked.connect(self.on_settings)
        button_layout.addWidget(settings_button)
        
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        central_widget.setLayout(main_layout)
    
    def load_rooms(self):
        """診察室情報を読み込んでリストに表示"""
        self.rooms = ConfigManager.load_rooms()
        self.room_list.clear()
        
        for room in self.rooms:
            item = QListWidgetItem(room.name)
            item.setData(Qt.ItemDataRole.UserRole, room)
            self.room_list.addItem(item)
    
    def on_selection_changed(self):
        """リスト選択変更時"""
        self.connect_button.setEnabled(self.room_list.currentItem() is not None)
    
    def on_connect(self):
        """接続ボタンクリック時"""
        current_item = self.room_list.currentItem()
        if not current_item:
            return
        
        room = current_item.data(Qt.ItemDataRole.UserRole)
        
        try:
            VNCConnector.connect(room)
            QMessageBox.information(
                self,
                '接続中',
                f'{room.name} ({room.ip_address}) に接続しています...'
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                'エラー',
                f'接続に失敗しました:\n{str(e)}'
            )
    
    def on_settings(self):
        """設定ボタンクリック時"""
        dialog = SettingsDialog(self)
        
        # 設定ダイアログのアクション選択
        choice, ok = QInputDialog.getItem(
            self,
            '設定',
            '操作を選択してください:',
            ['新規追加', '編集', '削除'],
            0,
            False
        )
        
        if not ok:
            return
        
        if choice == '新規追加':
            self.add_room()
        elif choice == '編集':
            self.edit_room()
        elif choice == '削除':
            self.delete_room()
    
    def add_room(self):
        """新規診察室を追加"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_room = dialog.get_room()
            
            if not new_room.name or not new_room.ip_address:
                QMessageBox.warning(self, '警告', '診察室名とIPアドレスを入力してください')
                return
            
            self.rooms.append(new_room)
            ConfigManager.save_rooms(self.rooms)
            self.load_rooms()
            QMessageBox.information(self, '成功', f'{new_room.name} を追加しました')
    
    def edit_room(self):
        """診察室情報を編集"""
        if not self.room_list.currentItem():
            QMessageBox.warning(self, '警告', '編集する診察室を選択してください')
            return
        
        current_item = self.room_list.currentItem()
        room = current_item.data(Qt.ItemDataRole.UserRole)
        
        dialog = SettingsDialog(self, room)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_room = dialog.get_room()
            
            if not updated_room.name or not updated_room.ip_address:
                QMessageBox.warning(self, '警告', '診察室名とIPアドレスを入力してください')
                return
            
            # 既存の情報を更新
            index = self.rooms.index(room)
            self.rooms[index] = updated_room
            ConfigManager.save_rooms(self.rooms)
            self.load_rooms()
            QMessageBox.information(self, '成功', f'{updated_room.name} を更新しました')
    
    def delete_room(self):
        """診察室を削除"""
        if not self.room_list.currentItem():
            QMessageBox.warning(self, '警告', '削除する診察室を選択してください')
            return
        
        current_item = self.room_list.currentItem()
        room = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            '確認',
            f'{room.name} を削除してもよろしいですか？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.rooms.remove(room)
            ConfigManager.save_rooms(self.rooms)
            self.load_rooms()
            QMessageBox.information(self, '成功', f'{room.name} を削除しました')


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
