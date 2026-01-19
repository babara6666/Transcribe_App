# Requirements 依賴分析報告

## 📊 核心衝突分析

### Torch 版本需求總結

| 套件 | Torch 版本需求 | 說明 |
|------|---------------|------|
| **whisperx** | `torch>=2.0` | 官方要求 PyTorch 2.0+ |
| **pyannote.audio** | `torch` (無硬性限制) | 推薦 2.0+，配合 pytorch-lightning |
| **pytorch-lightning** | `torch>=2.1.0` | pyannote 的間接依賴 |
| **torchaudio** | 應與 torch 版本匹配 | 建議同版本 |
| **deep-translator** | 無需 torch | 不相關 |

### ⚠️ 已知問題

1. **PyTorch 2.6+ 兼容性問題**
   - pyannote 使用的 `omegaconf` 在 PyTorch 2.6+ 會觸發 `weights_only=True` 錯誤
   - 已在 `transcribe.py` 中加入 monkey-patch 修正

2. **依賴鏈衝突**
   ```
   whisperx -> pyannote.audio -> pytorch-lightning -> torch>=2.1.0
   ```
   但 PyTorch 2.6+ 會出問題，所以限制在 `torch>=2.0.0,<2.6.0`

## ✅ 推薦配置

### 選項 1: 穩定版本（推薦給生產環境）

```txt
torch==2.5.1
torchaudio==2.5.1
whisperx>=3.1.1
pyannote.audio>=3.1.0
deep-translator>=1.11.4
python-dotenv>=1.0.0
```

**優點:** 
- 經過測試的穩定組合
- 避免 2.6+ 的問題
- 與當前 CUDA 兼容

### 選項 2: 靈活範圍（當前使用）

```txt
torch>=2.0.0,<2.6.0
torchaudio>=2.0.0,<2.6.0
whisperx>=3.1.1
pyannote.audio>=3.1.0
deep-translator>=1.11.4
python-dotenv>=1.0.0
```

**優點:**
- 允許自動更新到 2.5.x
- 避開已知問題版本
- 更靈活

## 🔧 安裝建議

### 方案 A: 從頭安裝（乾淨環境）

```powershell
# 1. 先安裝 torch (指定 CUDA 版本)
pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121

# 2. 安裝其他依賴
pip install whisperx>=3.1.1 pyannote.audio>=3.1.0 deep-translator>=1.11.4 python-dotenv>=1.0.0
```

### 方案 B: 更新現有環境

```powershell
# 如果已安裝 torch 2.6+，降級:
pip install torch==2.5.1 torchaudio==2.5.1 --force-reinstall

# 然後安裝/更新其他套件
pip install -r requirements.txt
```

## 📝 依賴樹

```
decord_app/
├── torch (2.0.0-2.5.x) ← 核心依賴
│   └── torchaudio (同版本)
├── whisperx (>=3.1.1)
│   ├── torch ✓
│   ├── torchaudio ✓
│   ├── faster-whisper
│   ├── ctranslate2
│   └── transformers
├── pyannote.audio (>=3.1.0)
│   ├── torch ✓
│   ├── pytorch-lightning (需要 torch>=2.1)
│   │   └── torch ✓ (2.1-2.5 符合)
│   └── transformers ✓
└── deep-translator (>=1.11.4)
    ├── beautifulsoup4
    └── requests
    (不依賴 torch) ✓
```

## 🎯 驗證方法

執行以下命令檢查是否有衝突:

```powershell
# 檢查安裝的版本
pip list | Select-String "torch|whisper|pyannote|translator"

# 檢查依賴樹
pip show whisperx pyannote.audio

# 測試導入
python -c "import torch; import whisperx; import pyannote.audio; print('All imports OK')"
```

## 🚨 故障排除

### 問題 1: `weights_only` 錯誤

**症狀:** PyTorch 2.6+ 加載 pyannote 模型時報錯

**解決:** 
- 已在 `transcriber/transcribe.py` 中實作 monkey-patch
- 或降級到 torch 2.5.x

### 問題 2: CUDA 版本不匹配

**症狀:** `RuntimeError: CUDA error: no kernel image available`

**解決:**
```powershell
# 檢查 CUDA 版本
nvidia-smi

# 安裝對應的 torch
# CUDA 11.8: cu118
# CUDA 12.1: cu121
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 問題 3: transformers 版本衝突

**症狀:** `ImportError` 或 deprecated warnings

**解決:**
```powershell
pip install transformers>=4.30.0 --upgrade
```

## 📌 結論

**當前 requirements.txt 配置安全且無衝突**，主要保護措施：

1. ✅ Torch 版本限制在 `2.0-2.5.x` 避開 2.6+ 問題
2. ✅ 所有套件要求的最低版本都滿足
3. ✅ 已對 PyTorch 2.6+ 的問題加入 workaround
4. ✅ Deep-translator 不依賴 torch，無衝突風險

**建議:** 使用當前配置即可，無需修改。
