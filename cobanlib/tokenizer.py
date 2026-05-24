import json
import os
from typing import List, Tuple
from .motor import CobanAnalizMotoru

class CobanTokenizer:
    def __init__(self, motor: CobanAnalizMotoru, vocab_dosyasi: str = "coban_vocab.json"):
        self.motor = motor
        self.vocab_dosyasi = vocab_dosyasi

        self.w2i = {"[PAD]": 0, "[UNK]": 1, "[BOS]": 2, "[EOS]": 3, "[SPACE]": 4}
        self.i2w = {0: "[PAD]", 1: "[UNK]", 2: "[BOS]", 3: "[EOS]", 4: "[SPACE]"}
        self._cache = {}

        # Karakter Tokenizer entegrasyonu için vocab yenilemesi
        if os.path.exists(self.vocab_dosyasi):
            os.remove(self.vocab_dosyasi)

        self._vocab_olustur()

    def _vocab_olustur(self):
        if os.path.exists(self.vocab_dosyasi):
            with open(self.vocab_dosyasi, 'r', encoding='utf-8') as f:
                self.w2i = json.load(f)
                self.i2w = {int(k): v for k, v in self.w2i.items()}
            return

        idx = 5

        # Karakter Tokenlerini Ekle (Bilinmeyen OOV kelimeler için)
        for harf in 'abcçdefgğhıijklmnoöprsştuüvyz0123456789.,!?\'"':
            token = f"[CHAR_{harf}]"
            if token not in self.w2i:
                self.w2i[token] = idx
                self.i2w[idx] = token
                idx += 1

        # Kök ve Ekleri Ekle
        tum_kokler = self.motor.vt.isim_kokleri.union(self.motor.vt.fiil_kokleri)
        for kok in sorted(tum_kokler):
            token = f"[{kok.upper()}]"
            if token not in self.w2i:
                self.w2i[token] = idx
                self.i2w[idx] = token
                idx += 1

        for _, kod in self.motor.vt.ek_kodlari_listesi:
            token = f"[{kod}]"
            if token not in self.w2i:
                self.w2i[token] = idx
                self.i2w[idx] = token
                idx += 1

        with open(self.vocab_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(self.w2i, f, ensure_ascii=False, indent=2)

    def _kelimeyi_karakterlere_ayir(self, kelime: str) -> List[str]:
        """Sistemin bilmediği kelimeleri harf harf parçalar (Fallback)."""
        tokenler = []
        for harf in kelime.lower():
            if harf in 'abcçdefgğhıijklmnoöprsştuüvyz0123456789.,!?\'"':
                tokenler.append(f"[CHAR_{harf}]")
            else:
                tokenler.append("[UNK]")
        return tokenler

    def encode(self, metin: str) -> List[int]:
        ids = []
        kelimeler = metin.split()

        for i, kelime in enumerate(kelimeler):
            if i > 0:
                ids.append(self.w2i["[SPACE]"])

            if kelime not in self._cache:
                analizler = self.motor.analiz_et(kelime)
                if analizler:
                    en_kisa = min(analizler, key=lambda x: len(x['ekler']))
                    tokenler = en_kisa['tokenler']
                else:
                    # Kök bulunamazsa LLM kör olmasın diye harf harf ID'lendir.
                    tokenler = self._kelimeyi_karakterlere_ayir(kelime)
                self._cache[kelime] = tokenler

            for t in self._cache[kelime]:
                ids.append(self.w2i.get(t, self.w2i["[UNK]"]))

        return ids

    def decode(self, ids: List[int]) -> str:
        tokenler = [self.i2w.get(i, "[UNK]") for i in ids]
        return " ".join(tokenler)

    def encode_batch(self, metinler: List[str], max_len: int = None) -> Tuple[List[List[int]], List[List[int]]]:
        """LLM Eğitimi için Batch (Matris) oluşturur ve Padding uygular."""
        batch_ids = [self.encode(m) for m in metinler]

        if max_len is None:
            max_len = max(len(ids) for ids in batch_ids)

        attention_masks = []

        for ids in batch_ids:
            # Maske: Gerçek tokenler için 1, boşluklar (PAD) için 0
            mask = [1] * len(ids) + [0] * (max_len - len(ids))
            attention_masks.append(mask)
            # PAD ekleme (ID'leri eşit uzunluğa getirme)
            ids += [self.w2i["[PAD]"]] * (max_len - len(ids))

        return batch_ids, attention_masks
