# GitHub Actions で Windows EXE を生成するガイド

このドキュメントでは、GitHub Actions を使用して Windows 用 exe ファイルを自動生成する方法を説明します。

## 📋 前提条件

- GitHub アカウント（既にお持ちです）
- git がインストール済み（macOS には標準搭載）

## 🚀 ステップバイステップ手順

### ステップ1：GitHub にリポジトリを作成

1. [GitHub](https://github.com) にアクセス
2. 右上の「+」→「New repository」をクリック
3. リポジトリ名：**nogatavnc**
4. 説明：VNC Remote Desktop Application
5. Public / Private は自由に選択
6. 「Create repository」をクリック

**表示されたページの URL をコピーしておいてください**（例：https://github.com/YOUR_USERNAME/nogatavnc.git）

---

### ステップ2：ローカルで git を初期化

ターミナルで以下を実行：

```bash
cd ~/Documents/nogatavnc

# git の初期化
git init

# 全ファイルをステージ
git add .

# 初回コミット
git commit -m "Initial commit"

# main ブランチに名前変更
git branch -M main

# GitHub リポジトリを追加（上でコピーした URL を使用）
git remote add origin https://github.com/YOUR_USERNAME/nogatavnc.git

# GitHub にプッシュ
git push -u origin main
```

---

### ステップ3：GitHub Actions の実行を確認

1. GitHub のリポジトリページに移動
2. **Actions** タブをクリック
3. **Build Windows EXE** ワークフローが実行中 or 完了

ビルドが完了すると：
- ✅ exe ファイルが自動生成されます
- ✅ Artifacts から直接ダウンロード可能

---

## 📥 exe ファイルをダウンロード

### 方法A：Artifacts から（毎回のビルド）

1. **Actions** タブ → **Build Windows EXE** ワークフローをクリック
2. 最新のビルドを選択
3. **Artifacts** セクションから **VNC-RemoteDesktop-Windows** をダウンロード
4. zip を解凍 → `VNCリモートデスクトップ.exe` が取得できます

### 方法B：Releases から（公式リリース版）

タグをプッシュするとリリース版が自動生成されます：

```bash
# ローカルでタグを作成
git tag -a v1.0.0 -m "Version 1.0.0"

# GitHub にプッシュ
git push origin v1.0.0
```

すると：
1. **Releases** ページに自動作成される
2. exe ファイルが自動アップロード
3. ダウンロード可能になります

---

## 🔄 更新のたびに exe も自動更新

以下のいずれかの操作で自動的に exe が再生成されます：

```bash
# 通常の更新
git add .
git commit -m "Update: 何か変更した説明"
git push

# 新しいバージョンをリリース
git tag -a v1.0.1 -m "Version 1.0.1"
git push origin v1.0.1
```

---

## ⚙️ ワークフローファイルについて

`.github/workflows/build-windows.yml` ファイルに以下が設定されています：

1. **Windows 環境で実行**
   - Windows Server 最新版を使用

2. **Python 3.11 をインストール**
   - 最新の安定版

3. **依存パッケージをインストール**
   - `requirements.txt` から自動インストール
   - PyInstaller も自動インストール

4. **exe ファイルを生成**
   - PyInstaller で exe 化
   - アイコンを含める

5. **Artifacts に保存**
   - 30日間保持

---

## 🐛 トラブルシューティング

### ビルドが失敗する場合

1. **Actions** タブで失敗したワークフローをクリック
2. ログを確認
3. エラーメッセージから原因を特定

**よくあるエラー：**

- `ModuleNotFoundError`
  → `requirements.txt` に依存パッケージが不足している
  → 修正して push すると再実行される

- `icon.ico not found`
  → アイコンファイルが必要な場合は、別途作成が必要

---

## 💡 次のステップ

exe ファイルが完成したら：

1. Windows PC にコピー
2. UltraVNC がインストール済みか確認
3. exe をダブルクリック
4. アプリケーションが起動

---

## 📚 参考リンク

- [GitHub Actions ドキュメント](https://docs.github.com/en/actions)
- [PyInstaller ドキュメント](https://pyinstaller.org/)
- [UltraVNC 公式サイト](https://www.uvnc.com/)

