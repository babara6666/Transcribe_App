# 安裝指南 - 基於 Gemini 推薦配置

## 📋 環境需求

- **Python**: 3.10.x （強烈推薦，3.11 在某些音訊庫有兼容性問題）
- **CUDA**: 11.8（系統級安裝）
- **PyTorch**: 2.1.2+cu118（音訊處理的「避風港」版本）

## 🚀 安裝步驟

### 步驟 1️⃣: 檢查環境

```powershell
# 檢查 Python 版本（應該是 3.10.x）
python --version

# 檢查 CUDA 版本（應該是 11.8）
nvidia-smi
```

### 步驟 2️⃣: 建立虛擬環境

```powershell
# 使用 conda（推薦）
conda create -n whisper-env python=3.10
conda activate whisper-env

# 或使用 venv
python -m venv venv
.\venv\Scripts\activate
```

### 步驟 3️⃣: 安裝 PyTorch（重要！必須先安裝）

```powershell
# ⚠️ 必須指定 CUDA 11.8 版本
pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118
```

**為什麼使用 2.1.2 而不是最新版？**
- 2.1.2 是音訊處理專業的穩定版
- speechbrain 和 CTranslate2 對此版本支援最完善
- 避免 2.2.x/2.3.x/2.5.x 的潛在問題

### 步驟 4️⃣: 驗證 PyTorch 安裝

```powershell
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}')"
```

**預期輸出：**
```
PyTorch: 2.1.2+cu118
CUDA Available: True
CUDA Version: 11.8
```

### 步驟 5️⃣: 安裝其他依賴

```powershell
# 安裝專案依賴
pip install whisperx>=3.1.1
pip install pyannote.audio==3.1.1
pip install deep-translator>=1.11.4
pip install python-dotenv>=1.0.0
pip install faster-whisper>=1.0.0
pip install ctranslate2
pip install transformers>=4.30.0
```

**或一次安裝（不含 PyTorch）：**
```powershell
pip install whisperx>=3.1.1 pyannote.audio==3.1.1 deep-translator>=1.11.4 python-dotenv>=1.0.0 faster-whisper>=1.0.0 ctranslate2 transformers>=4.30.0
```

### 步驟 6️⃣: 驗證完整安裝

```powershell
python -c "import torch; import whisperx; import pyannote.audio; from deep_translator import GoogleTranslator; print('✓ All imports successful')"
```

## 🔧 故障排除

### 問題 1: CUDA 版本不匹配

**症狀：**
```
RuntimeError: CUDA error: no kernel image is available for execution on the device
```

**解決：**
確保安裝的 PyTorch 版本與系統 CUDA 匹配：
```powershell
# 重新安裝正確的版本
pip uninstall torch torchaudio
pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118
```

### 問題 2: pytorch-lightning 版本衝突

**症狀：**
```
ERROR: pip's dependency resolver does not currently take into account all the packages...
```

**解決：**
不要手動指定 pytorch-lightning 版本，讓 pip 根據 pyannote.audio 自動管理：
```powershell
# 如果已安裝，卸載後重裝
pip uninstall pytorch-lightning lightning
pip install pyannote.audio==3.1.1
```

### 問題 3: Python 3.11 兼容性問題

**症狀：**
某些音訊編碼庫報錯或警告

**解決：**
降級到 Python 3.10.x：
```powershell
conda create -n whisper-env python=3.10
conda activate whisper-env
# 重新執行所有安裝步驟
```

## 📊 版本對照表

| 套件 | 版本 | 原因 |
|------|------|------|
| Python | 3.10.x | 最穩定，避免 3.11 音訊庫問題 |
| CUDA | 11.8 | speechbrain 與 CTranslate2 最佳支援 |
| PyTorch | 2.1.2+cu118 | 音訊處理的「避風港」 |
| Torchaudio | 2.1.2+cu118 | 必須匹配 PyTorch |
| Pyannote.audio | 3.1.1 | 主流穩定版 |
| WhisperX | >=3.1.1 | 最新功能 |

## ✅ 完整安裝腳本

```powershell
# 一鍵安裝腳本（複製整段執行）

# 1. 建立環境
conda create -n whisper-env python=3.10 -y
conda activate whisper-env

# 2. 安裝 PyTorch (CUDA 11.8)
pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

# 3. 安裝專案依賴
pip install whisperx>=3.1.1 pyannote.audio==3.1.1 deep-translator>=1.11.4 python-dotenv>=1.0.0 faster-whisper>=1.0.0 ctranslate2 transformers>=4.30.0

# 4. 驗證
python -c "import torch; import whisperx; import pyannote.audio; print('✓ Installation successful')"
```

## 📝 升級現有環境

如果你已經有安裝但版本不對：

```powershell
# 1. 降級 PyTorch
pip uninstall torch torchaudio -y
pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

# 2. 更新 pyannote
pip install pyannote.audio==3.1.1 --force-reinstall

# 3. 驗證
python -c "import torch; print(torch.__version__)"
```
