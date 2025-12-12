import zipfile
import os

# ZIPファイルを作成
with zipfile.ZipFile('handler.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('handler.py', 'handler.py')

print(f"Created handler.zip (size: {os.path.getsize('handler.zip')} bytes)")
