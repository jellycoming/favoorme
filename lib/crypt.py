# coding=utf-8
import hashlib
import base64
from Crypto.Cipher import AES


class Pycrypt(object):
    def __init__(self, key):
        # 密钥key长度必须为16(AES-128),24(AES-192),或32(AES-256)Bytes长度,所以直接将用户提供的key md5一下变成32位的。
        self.key = hashlib.md5(key).hexdigest()
        # 加密分组模式
        self.mode = AES.MODE_CBC
        # b'0000000000000000'是初始化向量IV(必须是bytes类型),16位要求,可以看做另一个密钥。在部分分组模式需要。
        self.iv = b'0000000000000000'
        # AES要求需要加密的内容长度为16的倍数,当密文长度不够的时候需要填充,解密后把填充内容去掉即可
        self.pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
        self.unpad = lambda s: s[0:-ord(s[-1])]

    def encrypt(self, plaintext):
        # 加解密过程都要新建cipher对象,否则会出错
        cipher = AES.new(self.key, self.mode, self.iv)
        # 默认加密后的字符串有很多特殊字符,加解密时用base64处理下
        ciphertext = cipher.encrypt(self.pad(plaintext))
        return base64.b64encode(ciphertext)

    def decrypt(self, ciphertext):
        cipher = AES.new(self.key, self.mode, self.iv)
        plaintext = cipher.decrypt(base64.b64decode(ciphertext))
        return self.unpad(plaintext)


if __name__ == '__main__':
    rawtext = 'hello world!'
    cipher = Pycrypt('12345')
    ciphertext = cipher.encrypt(rawtext)
    print ciphertext
    plaintext = cipher.decrypt(ciphertext)
    print plaintext
    if rawtext == plaintext:
        print 'same text'


