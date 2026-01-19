# Auto-Transcriber with Speaker Diarization

自動化會議錄音轉錄系統，使用 WhisperX + Pyannote.audio 實現語音轉文字與講者區分。

## Features

- 🎙️ **WhisperX** - 高精度語音轉文字（支援 large-v3 模型）
- 🗣️ **講者區分** - 自動識別不同講者（使用 Pyannote.audio）
- 🌐 **自動語言偵測** - 支援中文/英文自動切換
- ⚡ **GPU 加速** - 自動檢測 CUDA，支援 CPU 降級
- 🎵 **多格式支援** - 支援 MP3, WAV, FLAC, AAC, OGG 等常見音訊格式，自動轉 M4A
- 🔤 **自動翻譯** - 英文內容自動翻譯成繁體中文並附在下方
- 📄 **PDF 輸出** - 自動生成精美排版的 PDF 文件（支援中文字體）
- 📝 **Markdown 輸出** - 格式化的會議記錄，含表格和 Emoji

## Prerequisites

- Python 3.10+
- FFmpeg (安裝於系統 PATH)
- Pandoc + XeLaTeX (PDF 生成，可選)
- NVIDIA GPU + CUDA (可選，但強烈建議)
- Hugging Face Token

### FFmpeg 安裝

```powershell
winget install FFmpeg
```

### Pandoc 安裝（PDF 生成功能需要）

```powershell
# 安裝 Pandoc
winget install JohnMacFarlane.Pandoc

# 安裝 MiKTeX (提供 XeLaTeX)
winget install MiKTeX.MiKTeX
```

安裝完 MiKTeX 後，第一次生成 PDF 時會自動下載所需的 LaTeX 套件。

### Hugging Face Token

1. 前往 [Hugging Face Settings](https://huggingface.co/settings/tokens) 取得 Token
2. 接受以下模型的使用條款：
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

## Installation

### 重要提示

本專案使用經過優化的穩定版本組合，詳細安裝步驟請參考 **[INSTALL.md](INSTALL.md)**。

### 快速安裝

```powershell
# 建立虛擬環境 (Python 3.10.x 推薦)
conda create -n whisper-env python=3.10
conda activate whisper-env

# 安裝 PyTorch (CUDA 11.8) - 必須先安裝！
pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

# 安裝專案依賴
pip install whisperx>=3.1.1 pyannote.audio==3.1.1 deep-translator>=1.11.4 python-dotenv>=1.0.0 faster-whisper>=1.0.0 ctranslate2 transformers>=4.30.0
```

**為何使用 PyTorch 2.1.2？**
- 這是音訊處理領域的「避風港」版本
- speechbrain 和 CTranslate2 對此版本支援最完善
- 避免 2.2.x/2.3.x/2.5.x 的潛在兼容性問題

## Configuration

複製 `.env.example` 為 `.env` 並設定：

```env
HF_TOKEN=your_huggingface_token
WATCH_DIR=C:\Users\tnfsh\Downloads\zhanlu
MODEL_SIZE=large-v3
```

## Usage

### 基本使用

```powershell
python main.py
```

自動掃描 `WATCH_DIR` 中的音訊檔案並轉錄。

**支援的音訊格式：**
- M4A, MP3, WAV, FLAC, AAC
- OGG, WMA, OPUS, AIFF, APE
- WebM, MP4, AVI, MKV（音軌）

系統會自動將非 M4A 格式轉換成 M4A 後再進行辨識。

### 處理單一檔案

```powershell
# 支援任何音訊格式
python main.py --file path/to/audio.mp3
python main.py --file path/to/meeting.wav
python main.py --file path/to/recording.m4a
```

### CLI 參數

| 參數 | 說明 |
|------|------|
| `--dir` | 覆蓋預設監控目錄 |
| `--model` | 指定模型大小 (tiny/base/small/medium/large-v2/large-v3) |
| `--file` | 處理單一檔案 |
| `--no-translation` | 停用英文翻譯功能 |
| `--no-pdf` | 停用 PDF 生成功能 |

### 進階範例

```powershell
# 僅生成 Markdown，不翻譯、不生成 PDF
python main.py --file audio.mp3 --no-translation --no-pdf

# 使用較小模型加快速度
python main.py --model base --file audio.wav
```

## Output Format

系統會自動生成兩個檔案：
- **Markdown 檔案** (`.md`) - 含表格、Emoji 的精美排版
- **PDF 檔案** (`.pdf`) - 中文字體支援，含目錄和頁碼

### Markdown 範例格式：

```markdown
# 📝 會議轉錄記錄

## 📊 基本資訊

| 項目 | 內容 |
|------|------|
| 📁 檔案名稱 | `meeting.m4a` |
| ⏱️ 總時長 | 15:30 |
| 🕐 轉錄時間 | 2026-01-18 20:51:08 |
| 🌐 偵測語言 | ZH |
| 👥 講者數量 | 2 |

---

## 💬 逐字稿內容

### 🎤 SPEAKER_00

**`00:00:10 - 00:00:45`**

這裡是講者 1 說話的內容...

### 🎤 SPEAKER_01

**`00:00:46 - 00:01:20`**

This is an English segment that will be translated.
  > *翻譯: 這是一段會被翻譯的英文內容。*

---

*本文件由 Auto-Transcriber 自動生成於 2026-01-18 20:51:08*
```
