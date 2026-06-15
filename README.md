# Çoban: Türkçe Morfolojik Tokenizer ve Analiz Motoru


Çoban, Türkçe Doğal Dil İşleme (NLP) projeleri ve Büyük Dil Modelleri (LLM) için özel olarak geliştirilmiş, TDK (Türk Dil Kurumu) tabanlı, kural tabanlı ve morfolojik bir metin parçalama (tokenization) kütüphanesidir.

Büyük dil modellerini (LLM) Türkçe eğitirken karşılaşılan en büyük iki sorun olan **Sözlük Şişmesi (Vocabulary Bloat)** ve **Morfolojik Körlük (Morphological Blindness)** problemlerini çözmek amacıyla tasarlanmıştır.

## Neden Çoban?

Geleneksel tokenizer'lar (BPE, WordPiece vb.) Türkçe gibi sondan eklemeli dillerde kelimeleri anlamsız alt parçalara (subwords) böler veya her ek almış kelimeyi ("evde", "evden", "evler") ayrı bir kelime sanarak sözlüğü devasa boyutlara ulaştırır. 

Çoban ise metni **gerçek Türkçe dil bilgisi kurallarına göre** işler:
* `[EV]` kökünü ve `[DE]` bulunma ekini tanır.
* Modelin kelimelerin kök anlamlarını ve eklerin işlevlerini (morfoloji) kavramasını sağlar.
* TDK 12. Baskı'dan süzülmüş on binlerce **saf kök** içeren devasa bir veri tabanına sahiptir.
* Python'ın İngilizce tabanlı `.lower()` fonksiyonunun yarattığı meşhur `I/i` dönüşüm hatasını kendi içindeki bypass algoritmasıyla çözer.

## Dosya Yapısı

Çoban, bağımsız çalışabilen ve her projeye kolayca entegre edilebilen modüler bir yapıya sahiptir:

* `coban_veri.json`: Çoban'ın kalbi. Deyimlerden, fiilimsilerden ve sahte eklerden arındırılmış, sadece TDK onaylı saf isim/fiil köklerini ve ek kodlarını içeren veri tabanı.
* `Tokenizer.py`: Metinleri modelin anlayacağı token ID'lerine ve tip vektörlerine (kök, ek, boşluk, özel karakter) çeviren ana sınıf.
* `Motor.py`: `coban_veri.json`'daki kökleri kullanarak kelimeleri morfolojik olarak analiz eden zekâ.
* `Sozluk.py`: JSON formatındaki veri tabanını sisteme yükleyen ve yöneten altyapı.
* `coban_onisle.py`: Metinleri analiz motoruna girmeden önce temizleyen, gereksiz boşlukları ve uyumsuz karakterleri normalize eden ön işleme aracı.
* `sozluk_yapici.py`: TDK listelerini veya ham kelime yığınlarını analiz edip, sahte ek almış kelimeleri (örneğin "aşağılanabilmek") temizleyerek saf kökleri çıkaran mühendislik betiği.

## Kurulum ve Kullanım

Kütüphaneyi projenize dâhil etmek çok basittir. Dışarıdan hiçbir ağır kütüphaneye (PyTorch, TensorFlow vb.) ihtiyaç duymaz. Tamamen saf Python ile yazılmıştır.

### Örnek Kullanım (main.py)

```python
from Tokenizer import CobanTokenizer
from Motor import CobanAnalizMotoru
from Sozluk import CobanVeritabani

# 1. Veritabanını ve Motoru Başlat
vt = CobanVeritabani("coban_veri.json")
motor = CobanAnalizMotoru(vt)
tokenizer = CobanTokenizer(motor)

# 2. Test Metni
metin = "Kütüphanedeki bilgisayarlarımızdan verileri hızlıca indirebildik."

# 3. Metni Encode Et (Parçala ve ID'lere çevir)
ids, tipler = tokenizer.encode_with_types(metin)

print(f"Orijinal Metin: {metin}")
print(f"Token ID'leri: {ids}")
print(f"Token Tipleri: {tipler}")

# 4. Modelin Gözünden Metne Bak (Decode)
parcalanmis = [tokenizer.i2w.get(i) for i in ids]
print("Parçalanmış Hali:", parcalanmis)

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için LICENSE dosyasına göz atabilirsiniz.
