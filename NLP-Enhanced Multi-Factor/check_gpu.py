import torch

def check_gpu():
    print(f"PyTorch Version: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"CUDA Available: YES")
        print(f"Device Count: {torch.cuda.device_count()}")
        print(f"Current Device: {torch.cuda.current_device()}")
        print(f"Device Name: {torch.cuda.get_device_name(0)}")
        
        # Test tensor allocation
        x = torch.tensor([1.0, 2.0]).cuda()
        print(f"Test Tensor on GPU: {x}")
        print("GPU Acceleration is READY for FinBERT!")
    else:
        print("CUDA Available: NO")
        print("WARNING: Running on CPU. NLP tasks will be slow.")

if __name__ == "__main__":
    check_gpu()
