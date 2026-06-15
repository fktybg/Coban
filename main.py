from Tokenizer import CobanTokenizer
from motor import CobanAnalizMotoru
from sozluk import CobanVeritabani

def full_test():
    vt = CobanVeritabani("coban_veri.json")
    motor = CobanAnalizMotoru(vt)
    tokenizer = CobanTokenizer(motor)

    metin = "çocuklar evde chatgpt kullanıyor"
    print(f"\nFALLBACK TESTİ: '{metin}'")
    ids = tokenizer.encode(metin)
    print(f"Encode: {ids}")
    print(f"Decode: {tokenizer.decode(ids)}")

    cumleler = ["gözlükçülük", "çocuklar evde"]
    print("\nBATCH & PADDING TESTİ")
    batch_ids, masks = tokenizer.encode_batch(cumleler)
    for i, cumle in enumerate(cumleler):
        print(f"\nCümle: {cumle}")
        print(f"   ID Matrisi: {batch_ids[i]}")
        print(f"   Att. Mask : {masks[i]}")

    print("\nTip bilgili encode:")
    ids2, tipler = tokenizer.encode_with_types("kediler uyuyor")
    print(f"IDs: {ids2}")
    print(f"Tipler: {tipler}")

if __name__ == '__main__':
    full_test()
