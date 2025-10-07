import os
import struct
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

MAGIC = b'ENCv1'
NONCE_SIZE = 12
TAG_SIZE = 16
BUF_SIZE = 64 * 1024

def gen_key(out_path: Path):
    key = os.urandom(32)
    out_path.write_bytes(key)
    return out_path

def load_key(path: Path):
    key = path.read_bytes()
    if len(key) != 32:
        raise ValueError("Chave inválida: deve ter 32 bytes (AES-256).")
    return key

def encrypt_file(key: bytes, in_path: Path, out_path: Path):
    nonce = os.urandom(NONCE_SIZE)
    name_bytes = in_path.name.encode('utf-8')
    name_len = len(name_bytes)
    header = MAGIC + nonce + struct.pack('>I', name_len) + name_bytes
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend()).encryptor()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with in_path.open('rb') as rf, out_path.open('wb') as wf:
        wf.write(header)
        while True:
            chunk = rf.read(BUF_SIZE)
            if not chunk:
                break
            wf.write(encryptor.update(chunk))
        encryptor.finalize()
        wf.write(encryptor.tag)
    return out_path

def decrypt_file(key: bytes, in_path: Path, out_dir: Path):
    filesize = in_path.stat().st_size
    with in_path.open('rb') as rf:
        magic = rf.read(len(MAGIC))
        if magic != MAGIC:
            raise ValueError("Formato inválido.")
        nonce = rf.read(NONCE_SIZE)
        name_len = struct.unpack('>I', rf.read(4))[0]
        name_bytes = rf.read(name_len)
        orig_name = name_bytes.decode('utf-8')

        tag_pos = filesize - TAG_SIZE
        rf.seek(tag_pos)
        tag = rf.read(TAG_SIZE)
        decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend()).decryptor()

        rf.seek(len(MAGIC) + NONCE_SIZE + 4 + name_len)
        out_file = out_dir / orig_name
        out_dir.mkdir(parents=True, exist_ok=True)
        with out_file.open('wb') as wf:
            while rf.tell() < tag_pos:
                chunk = rf.read(BUF_SIZE)
                wf.write(decryptor.update(chunk))
            decryptor.finalize()
    return out_file
