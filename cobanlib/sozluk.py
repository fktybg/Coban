import json
import os
from typing import List, Tuple

# ============================================================
# TRİE YAPISI
# ============================================================
class Trie:
    def __init__(self):
        self.cocuklar = {}
        self.ek_kodlari = []

    def ekle(self, ek: str, kod: str):
        dugum = self
        for harf in ek:
            if harf not in dugum.cocuklar:
                dugum.cocuklar[harf] = Trie()
            dugum = dugum.cocuklar[harf]
        if kod not in dugum.ek_kodlari:
            dugum.ek_kodlari.append(kod)

    def en_uzun_ek_bul(self, metin: str, baslangic: int = 0) -> List[Tuple[str, List[str]]]:
        dugum = self
        eslesmeler = []
        i = baslangic
        while i < len(metin):
            harf = metin[i]
            if harf not in dugum.cocuklar: break
            dugum = dugum.cocuklar[harf]
            if dugum.ek_kodlari:
                eslesmeler.append((metin[baslangic:i+1], dugum.ek_kodlari))
            i += 1
        return list(reversed(eslesmeler))

# ============================================================
# SES OLAYLARI MOTORU
# ============================================================
class SesOlaylariMotoru:
    UNLULER = set('aeıioöuü')
    ISTISNA_KOKLER = {
        'saat':'e', 'kalp':'i', 'kalb':'i', 'harf':'i', 'hakikat':'i',
        'hürriyet':'i', 'adalet':'i', 'merhamet':'i', 'hayal':'i', 'mi':'i'
    }

    def buyuk_unlu_uyumu_kontrol(self, kok: str, ek: str) -> bool:
        son_unlu = self.ISTISNA_KOKLER.get(kok)
        if not son_unlu:
            kok_unluleri = [h for h in kok if h in self.UNLULER]
            if not kok_unluleri: return True
            son_unlu = kok_unluleri[-1]

        kalin = set('aıou'); ince = set('eiöü')
        ek_unluleri = [h for h in ek if h in self.UNLULER]
        if not ek_unluleri: return True

        return (ek_unluleri[0] in kalin) if (son_unlu in kalin) else (ek_unluleri[0] in ince)

    def yuzey_formlari_uret(self, kok: str) -> List[str]:
        yuzeyler = [kok]
        if len(kok) < 2: return yuzeyler
        son = kok[-1]

        YUMUSAT = {'p':'b', 'ç':'c', 't':'d', 'k':'ğ'}
        if son in YUMUSAT: yuzeyler.append(kok[:-1] + YUMUSAT[son])
        if kok.endswith('nk'): yuzeyler.append(kok[:-1] + 'g')

        if len(kok) >= 3 and kok[-2] in 'ıiuü' and son in 'bcçdfgğhjklmnprsştvyz':
            yuzeyler.append(kok[:-2] + son)

        if son in 'ae':
            for unlu in 'ıiuü':
                yuzeyler.append(kok[:-1] + unlu)

        return yuzeyler

# ============================================================
# VERİTABANI & JSON ENTEGRASYONU
# ============================================================
class CobanVeritabani:
    def __init__(self, veri_dosyasi: str = "coban_veri.json"):
        self.ses = SesOlaylariMotoru()
        self.yuzey_kok_haritasi = {}
        self.veri_dosyasi = veri_dosyasi
        self.isim_kokleri = set()
        self.fiil_kokleri = set()

        self.ek_kodlari_listesi = [
            ('lık','YPIsIs_lık'),('lik','YPIsIs_lık'),('luk','YPIsIs_lık'),('lük','YPIsIs_lık'),
            ('lığ','YPIsIs_lık'),('liğ','YPIsIs_lık'),('luğ','YPIsIs_lık'),('lüğ','YPIsIs_lık'),
            ('cı','YPIsIs_cı'),('ci','YPIsIs_cı'),('cu','YPIsIs_cı'),('cü','YPIsIs_cı'),
            ('çı','YPIsIs_cı'),('çi','YPIsIs_cı'),('çu','YPIsIs_cı'),('çü','YPIsIs_cı'),
            ('lı','YPIsIs_lı'),('li','YPIsIs_lı'),('lu','YPIsIs_lı'),('lü','YPIsIs_lı'),
            ('sız','YPIsIs_siz'),('siz','YPIsIs_siz'),('suz','YPIsIs_siz'),('süz','YPIsIs_siz'),
            ('cik','YPIsIs_kçlt'),('cuk','YPIsIs_kçlt'),('cağız','YPIsIs_kçlt'),('ceğiz','YPIsIs_kçlt'),
            ('cık','YPIsIs_kçlt'),('cük','YPIsIs_kçlt'),('çık','YPIsIs_kçlt'),('çik','YPIsIs_kçlt'),('çuk','YPIsIs_kçlt'),('çük','YPIsIs_kçlt'),
            ('la','YPIsFl_la'),('le','YPIsFl_la'),('lan','YPIsFl_lan'),('len','YPIsFl_lan'),('laş','YPIsFl_laş'),('leş','YPIsFl_laş'),
            ('im','YPFlIs_im'),('ım','YPFlIs_im'),('um','YPFlIs_im'),('üm','YPFlIs_im'),
            ('gi','YPFlIs_gi'),('gı','YPFlIs_gi'),('gu','YPFlIs_gi'),('gü','YPFlIs_gi'),
            ('gın','YPFlIs_gın'),('gin','YPFlIs_gın'),('gun','YPFlIs_gın'),('gün','YPFlIs_gın'),

            ('ıl','ÇATT_edlg'),('il','ÇATT_edlg'),('ul','ÇATT_edlg'),('ül','ÇATT_edlg'),
            ('ın','ÇATT_edlg'),('in','ÇATT_edlg'),('un','ÇATT_edlg'),('ün','ÇATT_edlg'),
            ('dır','ÇATT_etrg'),('dir','ÇATT_etrg'),('dur','ÇATT_etrg'),('dür','ÇATT_etrg'),
            ('tır','ÇATT_etrg'),('tir','ÇATT_etrg'),('tur','ÇATT_etrg'),('tür','ÇATT_etrg'),
            ('t','ÇATT_etrg'), ('ış','ÇATT_iştş'),('iş','ÇATT_iştş'),('uş','ÇATT_iştş'),('üş','ÇATT_iştş'),

            ('ebil','YTR'),('abil','YTR'),('yabil','YTR'),('yebil','YTR'),
            ('ama','YTR_olmsz'),('eme','YTR_olmsz'),
            ('ıver','TZL'),('iver','TZL'),('uver','TZL'),('üver','TZL'),
            ('yiver','TZL'),('yıver','TZL'),('yuver','TZL'),('yüver','TZL'),

            ('lar','ÇKçğl'),('ler','ÇKçğl'),
            ('dan','ÇKayr'),('den','ÇKayr'),('tan','ÇKayr'),('ten','ÇKayr'),
            ('da','ÇKbul'),('de','ÇKbul'),('ta','ÇKbul'),('te','ÇKbul'),
            ('a','ÇKyön'),('e','ÇKyön'),('ya','ÇKyön'),('ye','ÇKyön'),
            ('ı','ÇKbel'),('i','ÇKbel'),('u','ÇKbel'),('ü','ÇKbel'),('yı','ÇKbel'),('yi','ÇKbel'),('yu','ÇKbel'),('yü','ÇKbel'),
            ('ki','ÇKki'),('kü','ÇKki'),
            ('im','İYt1'),('ım','İYt1'),('um','İYt1'),('üm','İYt1'),
            ('in','İYt2'),('ın','İYt2'),('un','İYt2'),('ün','İYt2'),
            ('sı','İYt3'),('si','İYt3'),('su','İYt3'),('sü','İYt3'),
            ('imiz','İYç1'),('ımız','İYç1'),('umuz','İYç1'),('ümüz','İYç1'),
            ('nin','ÇKilg'),('nın','ÇKilg'),('nun','ÇKilg'),('nün','ÇKilg'),
            ('mi','SRsoru'),('mı','SRsoru'),('mu','SRsoru'),('mü','SRsoru'),
            ('miydi','SRsoru'),('mıydı','SRsoru'),('muydu','SRsoru'),('müydü','SRsoru'),
            ('miymiş','SRsoru'),('mıymış','SRsoru'),('muymuş','SRsoru'),('müymüş','SRsoru'),
            ('leyin','ÇKzmn'),

            ('mış','ZMdgy'),('miş','ZMdgy'),('muş','ZMdgy'),('müş','ZMdgy'),
            ('dı','ZMgçm'),('di','ZMgçm'),('du','ZMgçm'),('dü','ZMgçm'),('tı','ZMgçm'),('ti','ZMgçm'),('tu','ZMgçm'),('tü','ZMgçm'),
            ('iyor','ZMşmd'),('ıyor','ZMşmd'),('uyor','ZMşmd'),('üyor','ZMşmd'),('yor','ZMşmd'),
            ('ecek','ZMglk'),('acak','ZMglk'),('yecek','ZMglk'),('yacak','ZMglk'),('eceğ','ZMglk'),('acağ','ZMglk'),('yeceğ','ZMglk'),('yacağ','ZMglk'),
            ('ar','ZMgnş'),('er','ZMgnş'),('ir','ZMgnş'),('ur','ZMgnş'),('ür','ZMgnş'),
            ('meli','KPgrk'),('malı','KPgrk'),('se','KPşrt'),('sa','KPşrt'),
            ('ydi','EFgçm'),('ydı','EFgçm'),('ydu','EFgçm'),('ydü','EFgçm'),
            ('di','EFgçm'),('dı','EFgçm'),('du','EFgçm'),('dü','EFgçm'),('ti','EFgçm'),('tı','EFgçm'),('tu','EFgçm'),('tü','EFgçm'),
            ('ymış','EFdgy'),('ymiş','EFdgy'),('ymuş','EFdgy'),('ymüş','EFdgy'),
            ('mış','EFdgy'),('miş','EFdgy'),('muş','EFdgy'),('müş','EFdgy'),
            ('yse','EFşrt'),('ysa','EFşrt'),('se','EFşrt'),('sa','EFşrt'),
            ('dir','EFblg'),('dır','EFblg'),('dur','EFblg'),('dür','EFblg'),('tir','EFblg'),('tır','EFblg'),('tur','EFblg'),('tür','EFblg'),
            ('me','ÖLms'),('ma','ÖLms'),
            ('yim','KŞt1'),('yım','KŞt1'),('m','KŞt1'),('sin','KŞt2'),('sın','KŞt2'),('n','KŞt2'),
            ('ler','KŞç3'),('lar','KŞç3'),

            ('mak','Fİinf'),('mek','Fİinf'),('ış','Fİeyl'),('iş','Fİeyl'),('uş','Fİeyl'),('üş','Fİeyl'),
            ('an','Fİsft'),('en','Fİsft'),('yan','Fİsft'),('yen','Fİsft'),
            ('dık','Fİsft'),('dik','Fİsft'),('duk','Fİsft'),('dük','Fİsft'),
            ('tık','Fİsft'),('tik','Fİsft'),('tuk','Fİsft'),('tük','Fİsft'),
            ('ecek','Fİsft'),('acak','Fİsft'),('yecek','Fİsft'),('yacak','Fİsft'),
            ('mış','Fİsft'),('miş','Fİsft'),('muş','Fİsft'),('müş','Fİsft'),
            ('ince','Fİzrf'),('ınca','Fİzrf'),('yince','Fİzrf'),('yınca','Fİzrf'),
            ('ken','Fİzrf'),('yken','Fİzrf'),
            ('ip','Fİzrf'),('ıp','Fİzrf'),('up','Fİzrf'),('üp','Fİzrf'),('yip','Fİzrf'),('yıp','Fİzrf'),('yup','Fİzrf'),('yüp','Fİzrf'),
            ('erek','Fİzrf'),('arak','Fİzrf'),('yerek','Fİzrf'),('yarak','Fİzrf'),('meden','Fİzrf'),('madan','Fİzrf')
        ]

        self.trie = Trie()
        for ek, kod in self.ek_kodlari_listesi:
            self.trie.ekle(ek, kod)

        self._veriyi_yukle()
        self._on_hesaplama_yap()

    def _veriyi_yukle(self):
        if not os.path.exists(self.veri_dosyasi):
            print(f"⚠️ '{self.veri_dosyasi}' bulunamadı! Hatalar olabilir.")
            return

        with open(self.veri_dosyasi, 'r', encoding='utf-8') as f:
            veri = json.load(f)
            isimler = veri.get('isim_kokleri', {})
            fiiller = veri.get('fiil_kokleri', {})
            for k in isimler.keys(): self.isim_kokleri.add(k)
            for k in fiiller.keys(): self.fiil_kokleri.add(k)
            self.isim_kokleri.add('mi')

    def _on_hesaplama_yap(self):
        for kok in self.isim_kokleri:
            yuzeyler = self.ses.yuzey_formlari_uret(kok)
            for y in yuzeyler:
                if y not in self.yuzey_kok_haritasi: self.yuzey_kok_haritasi[y] = []
                self.yuzey_kok_haritasi[y].append((kok, 'isim'))

        for kok in self.fiil_kokleri:
            yuzeyler = self.ses.yuzey_formlari_uret(kok)
            for y in yuzeyler:
                if y not in self.yuzey_kok_haritasi: self.yuzey_kok_haritasi[y] = []
                self.yuzey_kok_haritasi[y].append((kok, 'fiil'))
