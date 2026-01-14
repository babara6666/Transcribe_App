# Auto-Transcriber with Speaker Diarization

自動化會議錄音轉錄系統，使用 WhisperX + Pyannote.audio 實現語音轉文字與講者區分。

## Features

- 🎙️ **WhisperX** - 高精度語音轉文字（支援 large-v3 模型）
- 🗣️ **講者區分** - 自動識別不同講者（使用 Pyannote.audio）
- 🌐 **自動語言偵測** - 支援中文/英文自動切換
- ⚡ **GPU 加速** - 自動檢測 CUDA，支援 CPU 降級
- 📝 **Markdown 輸出** - 格式化的會議記錄

## Prerequisites

- Python 3.10+
- FFmpeg (安裝於系統 PATH)
- NVIDIA GPU + CUDA (可選，但強烈建議)
- Hugging Face Token

### FFmpeg 安裝

```powershell
winget install FFmpeg
```

### Hugging Face Token

1. 前往 [Hugging Face Settings](https://huggingface.co/settings/tokens) 取得 Token
2. 接受以下模型的使用條款：
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

## Installation

```powershell
# 建立虛擬環境 (建議使用 conda)
conda activate torch-gpu

# 安裝依賴
pip install -r requirements.txt

# 若需 GPU 加速，安裝 CUDA 版 PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

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

自動掃描 `WATCH_DIR` 中的 `.m4a` 檔案並轉錄。

### 處理單一檔案

```powershell
python main.py --file path/to/audio.m4a
```

### CLI 參數

| 參數 | 說明 |
|------|------|
| `--dir` | 覆蓋預設監控目錄 |
| `--model` | 指定模型大小 (tiny/base/small/medium/large-v2/large-v3) |
| `--file` | 處理單一檔案 |

## Output Format

輸出的 Markdown 格式：

```markdown
# 會議轉錄記錄

**檔案名稱:** meeting.m4a
**轉錄時間:** 2026-01-11 20:51:08
**偵測語言:** zh

---

**[SPEAKER_00]:** (00:00:10 - 00:00:45)
這裡是講者 1 說話的內容...

**[SPEAKER_01]:** (00:00:46 - 00:01:20)
這是講者 2 的回應...
```
