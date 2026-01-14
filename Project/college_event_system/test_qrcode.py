try:
    import qrcode
    print("✓ qrcode is installed")
except ImportError as e:
    print("✗ qrcode is NOT installed:", e)

try:
    from PIL import Image
    print("✓ PIL/Pillow is installed")
except ImportError as e:
    print("✗ PIL/Pillow is NOT installed:", e)