#!/usr/bin/env python3
"""
完整的依賴檢查腳本
檢查 Python、PyTorch、CUDA 及所有套件的兼容性
"""

import sys
import subprocess
from pathlib import Path

def print_section(title):
    """打印分隔線和標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_python_version():
    """檢查 Python 版本"""
    print_section("1️⃣  Python 版本檢查")
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 10:
        print("✅ Python 3.10.x - 推薦版本")
    elif version.major == 3 and version.minor == 11:
        print("⚠️  Python 3.11 - 可能有音訊庫兼容性問題")
    elif version.major == 3 and version.minor < 10:
        print("❌ Python 版本過舊，建議升級到 3.10.x")
    else:
        print("⚠️  未測試的 Python 版本")

def check_pytorch():
    """檢查 PyTorch 安裝和 CUDA"""
    print_section("2️⃣  PyTorch 和 CUDA 檢查")
    
    try:
        import torch
        print(f"PyTorch 版本: {torch.__version__}")
        
        # 檢查 CUDA
        cuda_available = torch.cuda.is_available()
        print(f"CUDA 可用: {cuda_available}")
        
        if cuda_available:
            print(f"CUDA 版本: {torch.version.cuda}")
            print(f"GPU 名稱: {torch.cuda.get_device_name(0)}")
            print(f"GPU 數量: {torch.cuda.device_count()}")
            
            # 檢查推薦版本
            if torch.__version__.startswith("2.1.2"):
                print("✅ PyTorch 2.1.2 - 音訊處理推薦版本")
            elif torch.__version__.startswith("2.5"):
                print("⚠️  PyTorch 2.5.x - 可用但 2.1.2 更穩定")
            elif torch.__version__.startswith("2.6") or torch.__version__.startswith("2.7"):
                print("⚠️  PyTorch 2.6+ - 可能有 omegaconf 兼容性問題")
            else:
                print(f"ℹ️  PyTorch {torch.__version__}")
        else:
            print("⚠️  未檢測到 CUDA，將使用 CPU（速度較慢）")
            
    except ImportError:
        print("❌ PyTorch 未安裝")

def check_torchaudio():
    """檢查 Torchaudio"""
    print_section("3️⃣  Torchaudio 檢查")
    
    try:
        import torchaudio
        import torch
        
        print(f"Torchaudio 版本: {torchaudio.__version__}")
        
        # 檢查版本是否匹配
        torch_version = torch.__version__.split('+')[0]
        torchaudio_version = torchaudio.__version__.split('+')[0]
        
        if torch_version == torchaudio_version:
            print(f"✅ 版本匹配 (都是 {torch_version})")
        else:
            print(f"⚠️  版本不匹配! PyTorch: {torch_version}, Torchaudio: {torchaudio_version}")
            
    except ImportError:
        print("❌ Torchaudio 未安裝")

def check_core_packages():
    """檢查核心套件"""
    print_section("4️⃣  核心套件檢查")
    
    packages = {
        "whisperx": "3.1.1",
        "pyannote.audio": "3.1.1",
        "faster_whisper": "1.0.0+",
        "ctranslate2": None,
        "transformers": "4.30.0+",
        "deep_translator": "1.11.4+",
        "python-dotenv": "1.0.0+",
    }
    
    for package_name, expected in packages.items():
        try:
            if package_name == "python-dotenv":
                import dotenv
                module = dotenv
                display_name = "python-dotenv"
            elif package_name == "pyannote.audio":
                import pyannote.audio
                module = pyannote.audio
                display_name = "pyannote.audio"
            elif package_name == "faster_whisper":
                import faster_whisper
                module = faster_whisper
                display_name = "faster_whisper"
            elif package_name == "deep_translator":
                import deep_translator
                module = deep_translator
                display_name = "deep_translator"
            else:
                module = __import__(package_name)
                display_name = package_name
            
            version = getattr(module, "__version__", "未知")
            
            if expected:
                print(f"✅ {display_name}: {version} (期望: {expected})")
            else:
                print(f"✅ {display_name}: {version}")
                
        except ImportError as e:
            print(f"❌ {package_name}: 未安裝 ({e})")

def check_pip_dependencies():
    """使用 pip check 檢查依賴衝突"""
    print_section("5️⃣  Pip 依賴衝突檢查")
    
    try:
        result = subprocess.run(
            ["pip", "check"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            print("✅ 沒有檢測到依賴衝突")
        else:
            print("⚠️  檢測到以下依賴問題:")
            print(result.stdout)
            
    except Exception as e:
        print(f"❌ 無法執行 pip check: {e}")

def test_imports():
    """測試關鍵導入"""
    print_section("6️⃣  實際導入測試")
    
    test_cases = [
        ("torch", "import torch"),
        ("torchaudio", "import torchaudio"),
        ("whisperx", "import whisperx"),
        ("pyannote.audio", "import pyannote.audio"),
        ("faster_whisper", "import faster_whisper"),
        ("deep_translator", "from deep_translator import GoogleTranslator"),
        ("dotenv", "from dotenv import load_dotenv"),
    ]
    
    for name, import_stmt in test_cases:
        try:
            exec(import_stmt)
            print(f"✅ {name} - 導入成功")
        except Exception as e:
            print(f"❌ {name} - 導入失敗: {e}")

def test_cuda_functionality():
    """測試 CUDA 功能"""
    print_section("7️⃣  CUDA 功能測試")
    
    try:
        import torch
        
        if not torch.cuda.is_available():
            print("⚠️  CUDA 不可用，跳過測試")
            return
        
        # 測試張量運算
        x = torch.randn(3, 3).cuda()
        y = torch.randn(3, 3).cuda()
        z = x @ y
        
        print("✅ CUDA 張量運算正常")
        print(f"   測試張量形狀: {z.shape}")
        print(f"   GPU 記憶體使用: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
        
    except Exception as e:
        print(f"❌ CUDA 功能測試失敗: {e}")

def show_installed_versions():
    """顯示已安裝套件版本"""
    print_section("8️⃣  已安裝套件版本列表")
    
    try:
        result = subprocess.run(
            ["pip", "list"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 篩選關鍵套件
        keywords = [
            "torch", "whisper", "pyannote", "faster-whisper",
            "ctranslate2", "transformers", "deep-translator",
            "dotenv", "lightning", "numpy", "pandas"
        ]
        
        lines = result.stdout.split('\n')
        print("套件名稱                    版本")
        print("-" * 50)
        
        for line in lines:
            if any(kw in line.lower() for kw in keywords):
                print(line)
                
    except Exception as e:
        print(f"❌ 無法獲取套件列表: {e}")

def main():
    """主函數"""
    print("\n" + "🔍" * 30)
    print("依賴完整檢查工具 - Decord App")
    print("🔍" * 30)
    
    check_python_version()
    check_pytorch()
    check_torchaudio()
    check_core_packages()
    check_pip_dependencies()
    test_imports()
    test_cuda_functionality()
    show_installed_versions()
    
    print("\n" + "=" * 60)
    print("  ✅ 檢查完成")
    print("=" * 60)
    print("\n提示: 如果發現問題，請參考 INSTALL.md 和 DEPENDENCIES.md")
    print()

if __name__ == "__main__":
    main()
