import mmap
import pickle
import os
import glob

import numpy as np

class ObjectStream:
    def __init__(self, path):
        self.path = path
        self.using_flag = b'0'
        self.not_using_flag = b'1'

        try:
            # ファイルがなければ作成、あれば初期化
            with open(path, 'w') as f:
                f.write(' '*128)
        except OSError:
            # すでに他のObjectStreamがこのファイルのmmapを作成していたら
            # 初期化はしない
            pass

        with open(path, 'r+b') as f:
            self.mm = mmap.mmap(f.fileno(), 0)

    def set_using(self):
        self.mm[:1] = self.using_flag

    def set_not_using(self):
        self.mm[:1] = self.not_using_flag

    def wait_until_mm_released(self):
        """他のプロセスの読み込み/書き込みが終わるまで待つ"""
        while self.mm[:1] == self.using_flag:
            pass

    def resize_if_needed(self, use_size):
        """(必要であれば)ファイルの容量を変更する"""
        mm_size = len(self.mm)
        if use_size > mm_size:
            # ファイルの容量が足りなければ新たに確保
            new_size = 1 << len(bin(use_size)[2:]) # sの長さより大きい2の累乗の値
            self.mm.resize(new_size)
        elif use_size < (mm_size >> 2):
            # ファイルの容量が必要な分の4倍以上なら、容量を半分にする
            new_size = mm_size >> 1
            self.mm.resize(new_size)

    def write_bytes(self, b):
        self.wait_until_mm_released()
        self.resize_if_needed(1 + len(b)) # using_flagの分で+1
        self.mm.seek(0)
        self.mm.write(self.using_flag + b)
        self.mm[:1] = self.not_using_flag
        self.mm.flush()

    def read_bytes(self):
        self.wait_until_mm_released()
        return self.mm[1:]

    def write(self, obj):
        self.write_bytes(pickle.dumps(obj))

    def read(self):
        return pickle.loads(self.read_bytes())
    
class MMapDict:
    def __init__(self, savedir):
        self.savedir = savedir if savedir.endswith('/') else savedir + '/'
        os.makedirs(self.savedir, exist_ok=True)
        self.mmaps = {}
        
    def _key2path(self, key):
        return f"{self.savedir}{key}.txt"
    
    def _path2key(self, path):
        filename = path.replace('\\', '/').removeprefix(self.savedir)
        key = '.'.join(filename.split('.')[:-1])
        return key
    
    def __getitem__(self, key):
        if key not in self.mmaps:
            self.mmaps[key] = ObjectStream(self._key2path(key))
        
        try:
            value = self.mmaps[key].read()
        except pickle.UnpicklingError as e:
            raise KeyError(key) from e
            
        return value
        
    def __setitem__(self, key, value):
        if key not in self.mmaps:
            self.mmaps[key] = ObjectStream(self._key2path(key))
            
        self.mmaps[key].write(value)
        
    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False
        
    def _get_dict(self):
        d = {}
        for path in glob.glob(f"{self.savedir}*"):
            key = self._path2key(path)
            try:
                value = self.__getitem__(key)
            except KeyError:
                continue
            d[key] = value
        return d
    
    def items(self):
        return self._get_dict().items()
    
    def keys(self):
        return self._get_dict().keys()
    
    def values(self):
        return self._get_dict().values()
    
    def __iter__(self):
        yield from self.keys()