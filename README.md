# VNC リモートデスクトップ接続アプリケーション

医療施設内のUltraVNCサーバーに接続するWindowsデスクトップアプリケーション。

## 機能

- **診察室リスト表示** - config.json から読み込んだ診察室を一覧表示
- **ワンクリック接続** - 診察室を選択してボタンを押すと UltraVNC ビューアーで接続
- **診察室管理** - 新規追加、編集、削除が可能

## 動作環境

- Windows 10/11
- Python 3.8 以上
- UltraVNC がインストール済みであること

## インストール

### 方法1：exe ファイル（推奨・簡単）

1. [Releases](../../releases) ページから最新の `VNCリモートデスクトップ.exe` をダウンロード
2. Windows PC にコピー
3. ダブルクリックで実行

**前提条件：**
- UltraVNC がインストール済みであること

### 方法2：ソースコードから実行（開発者向け）

#### 1. Python のインストール

[Python 公式サイト](https://www.python.org/) から Python 3.10 以上をインストールしてください。

#### 2. 依存パッケージのインストール

プロジェクトディレクトリで以下を実行：

```bash
pip install -r requirements.txt
```

#### 3. UltraVNC のインストール

[UltraVNC 公式サイト](https://www.uvnc.com/) から UltraVNC をインストールしてください。

デフォルトインストール場所：
- `C:\Program Files\UltraVNC\vncviewer.exe`
- `C:\Program Files (x86)\UltraVNC\vncviewer.exe`

## 使用方法

### アプリケーションの起動

```bash
python main.py
```

### 設定ファイル (config.json)

初回起動時に自動生成されます。以下の形式：

```json
[
  {
    "name": "診察室1",
    "ip_address": "192.168.1.10",
    "port": 5900
  },
  {
    "name": "診察室2",
    "ip_address": "192.168.1.20",
    "port": 5900
  }
]
```

### 操作方法

1. **接続する**
   - リストから診察室を選択
   - 「接続」ボタンをクリック
   - UltraVNC ビューアーが起動して接続開始

2. **新規追加**
   - 「設定」ボタンをクリック
   - 「新規追加」を選択
   - 診察室名、IPアドレス、ポート番号を入力
   - OK をクリック

3. **編集**
   - リストから診察室を選択
   - 「設定」ボタンをクリック
   - 「編集」を選択
   - 情報を修正
   - OK をクリック

4. **削除**
   - リストから診察室を選択
   - 「設定」ボタンをクリック
   - 「削除」を選択
   - 確認ダイアログで「Yes」をクリック

## トラブルシューティング

### UltraVNC ビューアーが見つからないエラー

- UltraVNC がインストールされているか確認
- インストール場所を確認（C:\Program Files\ または C:\Program Files (x86)\）
- 別のインストール場所にある場合は、main.py の ultraVNC_paths を修正

### VNC 接続に失敗する

- 対象 PC の UltraVNC サーバーが起動しているか確認
- ファイアウォール設定を確認
- IP アドレスが正しいか確認
- ネットワーク接続を確認

## ファイル構成

```
nogatavnc/
├── main.py              # メインアプリケーション
├── config.json          # 設定ファイル（自動生成）
├── requirements.txt     # 依存パッケージ一覧
└── README.md           # このファイル
```

## exe ファイルの自動生成（GitHub Actions）

このプロジェクトは GitHub Actions で自動的に Windows 用 exe ファイルを生成します。

### セットアップ手順

1. **GitHub リポジトリを作成**
   ```bash
   cd ~/Documents/nogatavnc
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   ```

2. **GitHub にプッシュ**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/nogatavnc.git
   git push -u origin main
   ```

3. **リポジトリで GitHub Actions が自動実行**
   - Actions タブを確認
   - ビルド完了後、Artifacts から exe をダウンロード

### リリース版の作成

タグをプッシュするとリリース版として exe が生成されます：

```bash
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

その後、Releases ページから exe をダウンロード可能になります。

---

## ライセンス

MIT License

## 作成者

AI Assistant
