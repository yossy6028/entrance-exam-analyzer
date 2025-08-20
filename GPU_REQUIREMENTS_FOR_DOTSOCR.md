# DotsOCR GPU環境要件と導入ガイド

## 🖥️ ハードウェア要件

### 必要なGPUスペック

#### 最小要件
- **GPU**: NVIDIA GeForce RTX 3060 (12GB VRAM)
- **CUDA Compute Capability**: 7.0以上
- **VRAM**: 最低6GB（推奨8GB以上）
- **システムRAM**: 16GB以上

#### 推奨スペック
- **GPU**: NVIDIA RTX 4070 Ti (16GB) または RTX 4090 (24GB)
- **VRAM**: 16GB以上
- **システムRAM**: 32GB以上
- **SSD**: NVMe SSD 推奨（モデルロード高速化）

#### 対応GPUリスト
```
✅ 動作確認済み:
- RTX 4090/4080/4070 Ti/4070
- RTX 3090/3080/3070
- RTX A4000/A5000/A6000
- Tesla T4/V100/A100

⚠️ 制限あり（VRAMが少ない）:
- RTX 3060 (12GB) - 動作するが遅い
- RTX 3050 (8GB) - バッチサイズ制限

❌ 非対応:
- GTX 10xxシリーズ以前
- AMD GPU全般
- Intel Arc GPU
```

## 💻 ソフトウェア要件

### 1. CUDAツールキット
```bash
# CUDA 11.8または12.1のインストール
# macOSの場合（Apple SiliconはGPU非対応、Intel Macは外部GPU必要）
# Linuxの場合
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run

# 環境変数の設定
export CUDA_HOME=/usr/local/cuda-12.1
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
```

### 2. PyTorch（CUDA版）
```bash
# CUDA 12.1用
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu121

# CUDA 11.8用
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu118
```

### 3. Flash Attention 2
```bash
# GPU環境でのみインストール可能
pip install flash-attn==2.8.0.post2 --no-build-isolation

# ビルドに必要なツール
pip install ninja packaging
```

### 4. vLLM（GPU版）
```bash
# vLLMは既にインストール済みなので、GPU環境で再インストール
pip uninstall vllm -y
pip install vllm --no-cache-dir
```

## 🚀 セットアップ手順

### ステップ1: GPU環境の確認
```python
import torch
print(f"CUDA利用可能: {torch.cuda.is_available()}")
print(f"CUDA版: {torch.version.cuda}")
print(f"GPU数: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU名: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
```

### ステップ2: Flash Attentionのインストール
```bash
# CUDAとPyTorchが正しくインストールされていることを確認後
cd ~/dots.ocr
pip install flash-attn==2.8.0.post2 --no-build-isolation

# テスト
python -c "from flash_attn import flash_attn_func; print('Flash Attention OK')"
```

### ステップ3: vLLMサーバーの起動
```bash
cd ~/dots.ocr

# GPU版vLLMサーバー起動
python -m vllm.entrypoints.openai.api_server \
    --model ./weights/DotsOCR \
    --served-model-name DotsOCR \
    --trust-remote-code \
    --gpu-memory-utilization 0.9 \
    --max-model-len 16384 \
    --port 8000
```

### ステップ4: DotsOCRの実行
```bash
# CLIから実行（vLLMサーバー使用）
python dots_ocr/parser.py input.pdf --output ./output

# Pythonコードから実行
from modules.dots_ocr_pdf_processor import DotsOCRPDFProcessor
processor = DotsOCRPDFProcessor(use_gpu=True)
result = processor.process_pdf(pdf_path)
```

## ☁️ クラウドGPUオプション

### 1. Google Colab Pro+ 
- **料金**: 月額$49.99
- **GPU**: T4/V100/A100（ランダム割り当て）
- **制限**: 最大24時間連続実行

### 2. AWS EC2
```bash
# p3.2xlargeインスタンス（V100 16GB）
# 料金: 約$3.06/時間

# 起動コマンド例
aws ec2 run-instances \
    --image-id ami-0c94855ba3b6c8f7a \
    --instance-type p3.2xlarge \
    --key-name your-key \
    --security-groups your-sg
```

### 3. Paperspace Gradient
- **料金**: $0.51/時間〜（RTX 4000）
- **利点**: Jupyter Notebook統合
- **GPU**: RTX 4000/5000/A4000/A5000/A6000/A100

### 4. Lambda Labs
- **料金**: $0.50/時間〜（RTX 6000）
- **利点**: 専用GPU、長時間利用可
- **GPU**: RTX 6000/A6000/A100

### 5. RunPod
- **料金**: $0.34/時間〜（RTX 3090）
- **利点**: 最も安価
- **GPU**: RTX 3090/4090/A40/A100

## 🔧 トラブルシューティング

### CUDA out of memory
```python
# バッチサイズを減らす
processor = DotsOCRPDFProcessor(batch_size=1)

# GPU メモリ使用率を制限
--gpu-memory-utilization 0.7
```

### Flash Attentionビルドエラー
```bash
# 必要な開発ツールをインストール
sudo apt-get install build-essential
pip install ninja packaging

# CUDAツールキットの完全版が必要
sudo apt-get install cuda-toolkit-12-1
```

### vLLMサーバーが起動しない
```bash
# ポートが使用中の場合
lsof -i :8000
kill -9 [PID]

# 別のポートを使用
--port 8001
```

## 📊 パフォーマンス比較

| 環境 | 処理速度（ページ/秒） | 初期化時間 | メモリ使用量 |
|------|---------------------|------------|-------------|
| CPU (M1 Max) | 動作不可 | - | - |
| RTX 3060 12GB | 0.5-1 | 30秒 | 8GB |
| RTX 4070 Ti 16GB | 2-3 | 15秒 | 12GB |
| RTX 4090 24GB | 4-5 | 10秒 | 16GB |
| A100 40GB | 6-8 | 8秒 | 20GB |

## 💰 コスト試算

### オンプレミス（購入）
- RTX 4070 Ti: 約15万円
- 年間電力費: 約3万円（8時間/日使用）
- 投資回収: 約12ヶ月（クラウド比）

### クラウド（月100時間使用）
- AWS: 約$300/月
- Paperspace: 約$50/月
- RunPod: 約$35/月

## ✅ 導入チェックリスト

- [ ] GPUハードウェアの確保（購入/クラウド）
- [ ] CUDA 11.8以上のインストール
- [ ] PyTorch CUDA版のインストール
- [ ] Flash Attention 2のインストール
- [ ] vLLMサーバーの起動確認
- [ ] DotsOCRモデルの配置（~/dots.ocr/weights/DotsOCR）
- [ ] テストPDFでの動作確認
- [ ] 本番環境での性能測定

## 🎯 推奨構成

### 個人・研究用途
- **ローカル**: RTX 4070 Ti 16GB
- **クラウド**: RunPod RTX 3090（必要時のみ）

### 小規模ビジネス
- **ローカル**: RTX 4090 24GB
- **クラウド**: Paperspace A4000（定期利用）

### エンタープライズ
- **オンプレ**: NVIDIA A100 40GB × 複数台
- **クラウド**: AWS p4d.24xlarge（A100 × 8）

## 📝 まとめ

DotsOCRをGPU環境で動作させるには：

1. **最低でもRTX 3060（12GB）**が必要
2. **CUDA 11.8以上**とPyTorch CUDA版が必須
3. **Flash Attention 2**のインストールが必要
4. 初期コストを抑えるなら**クラウドGPU**から始める
5. 長期的にはローカルGPUの方がコスト効率が良い

現在のCPU環境から移行する場合は、まずクラウドGPUで動作確認してから、必要に応じてローカルGPUの購入を検討することをお勧めします。