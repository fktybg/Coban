from typing import List, Dict
from functools import lru_cache
from .sozluk import CobanVeritabani, SesOlaylariMotoru

class CobanAnalizMotoru:
    def __init__(self, vt: CobanVeritabani):
        self.vt = vt
        self.ses = SesOlaylariMotoru()
        self.DEBUG = False

        self.ISIM_SIRA_ZINCIRI = {'YP': 1, 'Fİ': 1, 'ÇKçğl': 2, 'İY': 3, 'ÇKbul': 4, 'ÇKbel': 4, 'ÇKyön': 4, 'ÇKayr': 4, 'ÇKki': 5, 'ÇKzmn': 5, 'SR': 6, 'EF': 7, 'KŞ': 8}
        self.FIIL_SIRA_ZINCIRI = {'ÇATT': 1, 'YP': 1, 'Fİ': 1, 'YTR': 2, 'TZL': 2, 'ÖL': 3, 'ZM': 4, 'KP': 4, 'EF': 5, 'KŞ': 6}

        # OPTİMİZASYON: Sıralama işlemi her DFS adımında değil, başlangıçta 1 kere yapılır!
        self._isim_anahtarlari = sorted(self.ISIM_SIRA_ZINCIRI.keys(), key=len, reverse=True)
        self._fiil_anahtarlari = sorted(self.FIIL_SIRA_ZINCIRI.keys(), key=len, reverse=True)

    # OPTİMİZASYON: Aynı kelime tekrar sorulursa DFS yapılmaz, bellekten verilir.
    @lru_cache(maxsize=10000)
    def analiz_et(self, kelime: str) -> List[Dict]:
        kelime = kelime.lower().strip()
        tum_analizler = []

        for uz in range(len(kelime), 0, -1):
            aday = kelime[:uz]
            kalan = kelime[uz:]

            if aday in self.vt.yuzey_kok_haritasi:
                for orjinal_kok, tur in self.vt.yuzey_kok_haritasi[aday]:
                    yollar = self._tam_analiz_dene(orjinal_kok, aday, tur, kalan)
                    for yol in yollar:
                        tum_analizler.append({
                            'kelime': kelime, 'yuzey_kok': aday, 'derin_kok': orjinal_kok, 'tur': tur,
                            'ekler': yol['ekler'], 'ek_kodlari': yol['ek_kodlari'], 'tokenler': yol['tokenler']
                        })

        return tum_analizler

    def _grup_endeksi_bul(self, kod: str, tur: str) -> int:
        anahtarlar = self._isim_anahtarlari if tur == 'isim' else self._fiil_anahtarlari
        zincir = self.ISIM_SIRA_ZINCIRI if tur == 'isim' else self.FIIL_SIRA_ZINCIRI
        for anahtar in anahtarlar:
            if kod.startswith(anahtar): return zincir[anahtar]
        return 99

    def _tam_analiz_dene(self, orjinal_kok: str, yuzey_kok: str, kok_turu: str, kalan: str) -> List[Dict]:
        baslangic_tur = kok_turu.split('_')[0]

        def dfs(suanki_kalan, guncel_tur, suanki_seviye, son_parca):
            if not suanki_kalan:
                return [[]]

            eslesmeler = self.vt.trie.en_uzun_ek_bul(suanki_kalan, 0)
            if not eslesmeler: return []

            gecerli_yollar = []

            for ek, kodlar in eslesmeler:
                if ek not in ['ki', 'kü', 'ken', 'yor', 'iyor', 'ıyor', 'uyor', 'üyor', 'leyin']:
                    if not self.ses.buyuk_unlu_uyumu_kontrol(son_parca, ek):
                        continue

                for kod in kodlar:
                    if guncel_tur == 'isim':
                        if any(kod.startswith(x) for x in ('ZM', 'KP', 'ÖL', 'ÇATT', 'YTR', 'TZL')): continue
                        if kod.startswith('YPFl'): continue
                    elif guncel_tur == 'fiil':
                        if any(kod.startswith(x) for x in ('ÇK', 'İY', 'SR')): continue
                        if kod.startswith('YPIs'): continue

                    ek_seviyesi = self._grup_endeksi_bul(kod, guncel_tur)

                    if kod.startswith('ÇATT') or kod.startswith('YP'):
                        pass
                    elif ek_seviyesi <= suanki_seviye:
                        continue

                    yeni_seviye = ek_seviyesi
                    yeni_tur = guncel_tur

                    if kod.startswith('YP') or kod.startswith('Fİ') or kod.startswith('ÇATT') or kod.startswith('YTR') or kod.startswith('TZL'):
                        yeni_seviye = 0
                        if kod.startswith('YPIsFl'): yeni_tur = 'fiil'
                        elif kod.startswith('YPFlIs') or kod.startswith('Fİ'): yeni_tur = 'isim'

                    alt_yollar = dfs(suanki_kalan[len(ek):], yeni_tur, yeni_seviye, ek)
                    for alt_yol in alt_yollar:
                        gecerli_yollar.append([(ek, kod)] + alt_yol)

            return gecerli_yollar

        yollar = dfs(kalan, baslangic_tur, 0, yuzey_kok)
        sonuclar = []
        for yol in yollar:
            ekler = [y[0] for y in yol]
            ek_kodlari = [y[1] for y in yol]
            tokenler = [f"[{orjinal_kok.upper()}]"] + [f"[{k}]" for k in ek_kodlari]
            sonuclar.append({'ekler': ekler, 'ek_kodlari': ek_kodlari, 'tokenler': tokenler})

        return sonuclar
