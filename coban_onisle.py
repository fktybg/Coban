
import re

_TR_BUYUK = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
_TR_KUCUK = "abcçdefgğhıijklmnoöprsştuüvyz"
_TR_MAP = str.maketrans(_TR_BUYUK, _TR_KUCUK)

def tr_kucult(s):
    return s.translate(_TR_MAP)

_DESENLER = [
    ("[TARIH]", re.compile(r'\\b\\d{1,2}[./\\-]\\d{1,2}[./\\-]\\d{2,4}\\b')),
    ("[SAYI]",  re.compile(r'\\b\\d+(?:[.,]\\d+)?\\b')),
    ("[SAAT]",  re.compile(r'\\b\\d{1,2}:\\d{2}(?::\\d{2})?\\b')),
    ("[YUZDE]", re.compile(r'%\\d+(?:[.,]\\d+)?|\\d+(?:[.,]\\d+)?%')),
]

_APOSTROF = re.compile(r"([A-Za-zÇĞİÖŞÜçğıöşü]+)['\\u2019]([A-Za-zÇĞİÖŞÜçğıöşü]+)")

def metin_temizle(metin):
    # 1. Apostrofları ayır
    metin = _APOSTROF.sub(lambda m: tr_kucult(m.group(1)) + " " + tr_kucult(m.group(2)), metin)
    # 2. Noktalama işaretlerini kelimelerden ayır (virgül, nokta, ünlem, soru, parantez)
    metin = re.sub(r"([.,!?()\":;])", r" \\1 ", metin)
    # 3. Özel token'ları değiştir
    for token_adi, desen in _DESENLER:
        metin = desen.sub(token_adi, metin)
    # 4. Büyük harfleri küçült
    metin = tr_kucult(metin)
    # 5. Fazla boşlukları temizle
    metin = re.sub(r"\\s+", " ", metin).strip()
    return metin
