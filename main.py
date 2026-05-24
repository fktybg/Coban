from cobanlib import CobanVeritabani, CobanAnalizMotoru, CobanTokenizer

def full_test():
    vt = CobanVeritabani("coban_veri.json")
    motor = CobanAnalizMotoru(vt)
    tokenizer = CobanTokenizer(motor)

    # 1. Fallback (Bilinmeyen Kelime) Testi
    metin = "çocuklar evde chatgpt kullanıyor"
    print(f"\n1. FALLBACK TESTİ: '{metin}'")
    ids = tokenizer.encode(metin)
    print(f"Encode: {ids}")
    print(f"Decode: {tokenizer.decode(ids)}")

    # 2. Batch (Matris) Eğitim Verisi Testi
    cumleler = ["gözlükçülük", "çocuklar evde"]
    print(f"\n2. BATCH & PADDING TESTİ")
    batch_ids, masks = tokenizer.encode_batch(cumleler)

    for i in range(len(cumleler)):
        print(f"\nCümle: {cumleler[i]}")
        print(f"   ID Matrisi: {batch_ids[i]}")
        print(f"   Att. Mask : {masks[i]}")

if __name__ == '__main__':
    full_test()
