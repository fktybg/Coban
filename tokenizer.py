import json
from typing import List, Tuple
from functools import lru_cache

# 🔥 BÜYÜK FİKS 1: Python'un İngilizce bazlı .lower() fonksiyonunun
# Türkçe kelimeleri (Örn: Işık -> isik, İstanbul -> i̇stanbul) bozmasını engeller.
def turkce_kucult(metin: str) -> str:
    return metin.replace("I", "ı").replace("İ", "i").lower()

class CobanTokenizer:
    def __init__(self, motor):
        self.motor = motor
        self._analiz_et_cached = lru_cache(maxsize=16384)(motor.analiz_et)
        self.w2i = {}
        self.i2w = {}
        self.gecerli_ek_kodlari = {kod for _, kod in motor.vt.ek_kodlari_listesi}
        self._vocab_olustur()

    def _vocab_olustur(self):
        ozel_tokenlar = ["[PAD]", "[UNK]", "[BOS]", "[EOS]", "[SPACE]"]
        idx = 0
        for t in ozel_tokenlar:
            self.w2i[t] = idx
            self.i2w[idx] = t
            idx += 1

        # 🔥 BÜYÜK FİKS 2: Sık Kullanılan Bağlaç ve Kelimeleri Doğrudan Sözlüğe Ekleme
        # Bu kelimeler tek bir token olarak işlenecek ve CHAR oranını devasa düşürecek.
        sik_kullanilanlar = [
            "ve", "bir", "ile", "için", "bu", "da", "de", "çok", "gibi", "kadar", "en",
            "daha", "olan", "olarak", "sonra", "önce", "kendi", "büyük", "yeni", "ilk",
            "göre", "ancak", "başka", "çünkü", "tüm", "her", "hangi", "şekilde", "aynı",
            "iki", "sadece", "zaman", "yer", "yıl", "neden", "nasıl", "ne", "kim",
            "nerede", "yok", "var", "iyi", "değil", "o", "biz", "siz", "onlar"
        ]

        for kelime in sik_kullanilanlar:
            t = f"[{turkce_kucult(kelime).upper()}]"
            if t not in self.w2i:
                self.w2i[t] = idx
                self.i2w[idx] = t
                idx += 1

        for kok in self.motor.vt.isim_kokleri:
            t = f"[{turkce_kucult(kok).upper()}]"
            if t not in self.w2i:
                self.w2i[t] = idx
                self.i2w[idx] = t
                idx += 1

        for kok in self.motor.vt.fiil_kokleri:
            t = f"[{turkce_kucult(kok).upper()}]"
            if t not in self.w2i:
                self.w2i[t] = idx
                self.i2w[idx] = t
                idx += 1

        for ek, kod in self.motor.vt.ek_kodlari_listesi:
            t = f"[{kod}]"
            if t not in self.w2i:
                self.w2i[t] = idx
                self.i2w[idx] = t
                idx += 1

        # 🔥 BÜYÜK FİKS 3: Genişletilmiş Alfabe (Akıllı tırnaklar, noktalama ve semboller)
        alfabe = "abcçdefgğhıijklmnoöprsştuüvyzABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ0123456789.,!?:;\"'()[]{}-_/\\%&+*=#@|~$€£₺“”‘’"
        for harf in alfabe:
            t = f"[CHAR_{harf}]"
            if t not in self.w2i:
                self.w2i[t] = idx
                self.i2w[idx] = t
                idx += 1

    
        # 🔥 Türkçe karakterleri manuel ekle (CHAR oranını düşürür)
        turkce_karakterler = ["ç", "ş", "ğ", "ü", "ö", "ı", "İ", "Ç", "Ş", "Ğ", "Ü", "Ö"]
        for char in turkce_karakterler:
            t = f"[CHAR_{char}]"
            if t not in self.w2i:
                self.w2i[t] = idx
                self.i2w[idx] = t
                idx += 1

    def encode_with_types(self, metin: str, add_bos_eos: bool = True) -> Tuple[List[int], List[int]]:
        ids = []
        tipler = []
        if add_bos_eos:
            ids.append(self.w2i["[BOS]"])
            tipler.append(1)

        kelimeler = metin.strip().split()
        for i, kelime in enumerate(kelimeler):
            # 🔥 Türkçe küçük harf fonksiyonu devrede
            temiz_kelime = turkce_kucult(kelime)
            dogrudan_token = f"[{temiz_kelime.upper()}]"

            if dogrudan_token in self.w2i:
                ids.append(self.w2i[dogrudan_token])
                tipler.append(2)
                if i < len(kelimeler) - 1:
                    ids.append(self.w2i["[SPACE]"])
                    tipler.append(4)
                continue

            analiz_listesi = self._analiz_et_cached(temiz_kelime)

            # 🔥 BÜYÜK FİKS 4: Noktalama Ayrıştırıcı
            # (Eğer analiz başarısızsa ve kelime sonu noktalama ile bitiyorsa parçala)
            if not analiz_listesi and len(kelime) > 1 and kelime[-1] in ".,!?:;\"'()[]{}“”‘’":
                govde = turkce_kucult(kelime[:-1])
                noktalama = kelime[-1]
                govde_token = f"[{govde.upper()}]"

                if govde_token in self.w2i:
                    ids.append(self.w2i[govde_token])
                    tipler.append(2)

                    nokt_token = f"[CHAR_{noktalama}]"
                    ids.append(self.w2i.get(nokt_token, self.w2i["[UNK]"]))
                    tipler.append(0)

                    if i < len(kelimeler) - 1:
                        ids.append(self.w2i["[SPACE]"])
                        tipler.append(4)
                    continue

            if analiz_listesi:
                analiz = analiz_listesi[0]
                tokenler = analiz.get('tokenler', [])
                for token in tokenler:
                    token_id = self.w2i.get(token, self.w2i["[UNK]"])
                    ids.append(token_id)
                    if token.startswith("[CHAR_") or token in ("[PAD]", "[UNK]"):
                        tipler.append(0)
                    elif token in ("[BOS]", "[EOS]"):
                        tipler.append(1)
                    elif token == "[SPACE]":
                        tipler.append(4)
                    elif token[1:-1].isupper() and not token.startswith("[CHAR_"):
                        tipler.append(2)
                    else:
                        tipler.append(3)
            else:
                for harf in kelime:
                    token = f"[CHAR_{harf}]"
                    token_id = self.w2i.get(token, self.w2i["[UNK]"])
                    ids.append(token_id)
                    tipler.append(0)

            if i < len(kelimeler) - 1:
                ids.append(self.w2i["[SPACE]"])
                tipler.append(4)

        if add_bos_eos:
            ids.append(self.w2i["[EOS]"])
            tipler.append(1)
        return ids, tipler

    def encode(self, metin: str, add_bos_eos: bool = True) -> List[int]:
        ids, _ = self.encode_with_types(metin, add_bos_eos)
        return ids

    def decode(self, ids: List[int]) -> str:
        return " ".join(self.i2w.get(i, "[UNK]") for i in ids)

    def _ses_uyumlu_ek(self, onceki_kisim: str, ek_kodu: str) -> str:
        sablonlar = {
            "ÇKçğl": "lAr", "ÇKbel": "I", "ÇKyön": "A", "ÇKbul": "DA", "ÇKayr": "DAn",
            "ÇKtam": "In", "YPIsIs_cı": "CI", "YPIsIs_lık": "lIk", "YPIsIs_lı": "lI",
            "YPIsIs_sız": "sIz", "Fİinf": "mAk", "Fİzrf": "ArAk", "Fİeyl": "Ip",
            "YPIsFl_la": "lA", "ZMKşh_1t": "Im", "Fİkip_gçmş": "DI",
            "Fİkip_şmd": "Iyor", "Fİkip_gck": "AcAk"
        }
        sablon = sablonlar.get(ek_kodu, ek_kodu.lower())
        if "A" not in sablon and "I" not in sablon and "D" not in sablon and "C" not in sablon:
            return sablon

        son_unlu = 'a'
        for harf in reversed(onceki_kisim):
            if harf in "aeıioöuüAEIİOÖUÜ":
                son_unlu = harf.lower()
                break

        kalin = son_unlu in "aıou"
        a_tipi = "a" if kalin else "e"
        if son_unlu in "aı": i_tipi = "ı"
        elif son_unlu in "ei": i_tipi = "i"
        elif son_unlu in "ou": i_tipi = "u"
        else: i_tipi = "ü"

        if onceki_kisim and onceki_kisim[-1].lower() in "fstkçşhp":
            sablon = sablon.replace("D", "t").replace("C", "ç")
        else:
            sablon = sablon.replace("D", "d").replace("C", "c")

        if onceki_kisim and onceki_kisim[-1].lower() in "aeıioöuü":
            if sablon.startswith(("A", "I", "D", "C")):
                sablon = "y" + sablon

        return sablon.replace("A", a_tipi).replace("I", i_tipi)

    def detokenize(self, token_listesi: List[str]) -> str:
        parcalar = []
        for i, tok in enumerate(token_listesi):
            if not tok or tok in ("[BOS]", "[EOS]", "[PAD]", "[UNK]"):
                continue
            if tok == "[SPACE]":
                parcalar.append(" ")
                continue
            if tok.startswith("[CHAR_") and tok.endswith("]"):
                parcalar.append(tok[6:-1])
                continue
            if tok.startswith("[") and tok.endswith("]"):
                ic = tok[1:-1]
                if ic in self.gecerli_ek_kodlari:
                    biriken_metin = "".join(parcalar).replace("  ", " ").strip()
                    dogru_ek = self._ses_uyumlu_ek(biriken_metin, ic)
                    parcalar.append(dogru_ek)
                elif ic.isupper() or (len(ic) > 0 and ic[0].isupper()):
                    if i > 0 and parcalar and parcalar[-1] != " ":
                        parcalar.append(" ")
                    parcalar.append(ic.lower())
                else:
                    parcalar.append(ic.lower())
            else:
                parcalar.append(tok.lower())
        return "".join(parcalar).replace("  ", " ").strip()

    def encode_batch(self, metinler: List[str], add_bos_eos: bool = True, max_len: int = None) -> Tuple[List[List[int]], List[List[int]]]:
        batch_ids = []
        batch_tipler = []
        for metin in metinler:
            ids, tipler = self.encode_with_types(metin, add_bos_eos)
            batch_ids.append(ids)
            batch_tipler.append(tipler)

        if max_len is None:
            max_len = max(len(ids) for ids in batch_ids) if batch_ids else 0

        pad_id = self.w2i["[PAD]"]
        pad_tip = 0
        for i in range(len(batch_ids)):
            fark = max_len - len(batch_ids[i])
            if fark > 0:
                batch_ids[i].extend([pad_id] * fark)
                batch_tipler[i].extend([pad_tip] * fark)
            elif fark < 0:
                batch_ids[i] = batch_ids[i][:max_len]
                batch_tipler[i] = batch_tipler[i][:max_len]

        return batch_ids, batch_tipler
