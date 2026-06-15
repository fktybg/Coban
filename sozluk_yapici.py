import json

print("🚀 TDK Pres Makinesi Çalışıyor... 65.000 kelime eziliyor!")

# İndirdiğin veya temizlediğin 65k kelimelik TDK dosyan
try:
    with open("tdk_kokler.txt", "r", encoding="utf-8") as f:
        ham_kelimeler = set([w.strip().lower() for w in f.readlines() if w.strip()])
except FileNotFoundError:
    print("❌ tdk_kokler.txt dosyası bulunamadı! Lütfen TDK kök listesini bu klasöre koyun.")
    exit()

print(f"📦 Başlangıç: {len(ham_kelimeler)} madde başı bulundu.")

# 1. AŞAMA: İğrenç Derecede Türetilmiş Fiilleri ve Kötü Formları Sil
yasakli_parcalar = [
    "abilme", "ebilme", "ıverme", "iverme", "uverme", "üverme",
    "mamazlık", "memezlik", "mazlık", "mezlik"
]

temiz_kelimeler = set()
for w in ham_kelimeler:
    if any(p in w for p in yasakli_parcalar):
        continue
    temiz_kelimeler.add(w)

fiiller = {}
isimler = {}

# 2. AŞAMA: Fiilleri ve İsimleri Ayır
for w in temiz_kelimeler:
    if w.endswith("mak") or w.endswith("mek"):
        # Fiillerin mak/mek mastarını atıp saf kökü/gövdeyi alıyoruz
        kok = w[:-3]
        if len(kok) > 0:
            fiiller[kok] = kok
    else:
        isimler[w] = w

# 3. AŞAMA: İsimleri Presle (Fiilimsi ve Yan Ürünleri Yok Et)
saf_isimler = {}
for isim in isimler:
    # A. İsim Fiiller (-ma / -me)
    if isim + "k" in temiz_kelimeler:
        continue

    # B. İş/Oluş İsimleri (-ış, -iş, -yış, -yiş)
    if isim.endswith(('ış', 'iş', 'uş', 'üş')):
        if isim[:-2] + "mak" in temiz_kelimeler or isim[:-2] + "mek" in temiz_kelimeler:
            continue
    if isim.endswith(('yış', 'yiş', 'yuş', 'yüş')):
        if isim[:-3] + "mak" in temiz_kelimeler or isim[:-3] + "mek" in temiz_kelimeler:
            continue

    # Temiz kalan isimleri listeye ekle
    saf_isimler[isim] = isim

# Çoban Motoru JSON formatı
yeni_coban_vt = {
    "isim_kokleri": saf_isimler,
    "fiil_kokleri": fiiller,
    "ek_kodlari_listesi": [
        ["ÇKçğl", "lAr"], ["ÇKbel", "I"], ["ÇKyön", "A"], ["ÇKbul", "DA"], ["ÇKayr", "DAn"],
        ["ÇKtam", "In"], ["YPIsIs_cı", "CI"], ["YPIsIs_lık", "lIk"], ["YPIsIs_lı", "lI"],
        ["YPIsIs_sız", "sIz"], ["Fİinf", "mAk"], ["Fİzrf", "ArAk"], ["Fİeyl", "Ip"],
        ["YPIsFl_la", "lA"], ["ZMKşh_1t", "Im"], ["Fİkip_gçmş", "DI"],
        ["Fİkip_şmd", "Iyor"], ["Fİkip_gck", "AcAk"]
    ]
}

# JSON dosyasını alfabetik olarak sırala (Profesyonel görünüm için)
yeni_coban_vt["isim_kokleri"] = {k: yeni_coban_vt["isim_kokleri"][k] for k in sorted(yeni_coban_vt["isim_kokleri"].keys())}
yeni_coban_vt["fiil_kokleri"] = {k: yeni_coban_vt["fiil_kokleri"][k] for k in sorted(yeni_coban_vt["fiil_kokleri"].keys())}

with open("coban_veri.json", "w", encoding="utf-8") as f:
    json.dump(yeni_coban_vt, f, ensure_ascii=False, indent=2)

print("\n🎯 İŞLEM TAMAMLANDI!")
print(f"✅ Çıkarılan Saf Fiil Kökü: {len(fiiller)}")
print(f"✅ Çıkarılan Saf İsim Kökü: {len(saf_isimler)}")
