# detect_xss — XSS detection helper

Dokumentasi ini menjelaskan file `xss.py` yang berisi fungsi `detect_xss(input_string)` — sebuah detektor pola XSS sederhana berbasis regular expression.

---

## Source Code

```py
import re

def detect_xss(input_string):
    """
    Detects potential XSS vulnerabilities in the input string.
    Returns True if potential XSS is detected, False otherwise.
    
    This is a basic regex-based detector for common XSS patterns.
    It does not sanitize or escape the input; it only checks for suspicious patterns.
    Note: This is not foolproof; advanced obfuscated attacks may evade it.
    """
    # Common XSS patterns to detect
    xss_patterns = [
        r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',  # <script> tags
        r'on\w+\s*=',  # Event handlers like onload=, onclick=, etc.
        r'javascript\s*:',  # javascript: protocol
        r'vbscript\s*:',  # vbscript: protocol
        r'data\s*:',  # data: protocol (can be used for XSS)
        r'<img\s+[^>]*src\s*=\s*["\']?[^"\']*javascript:',  # img src with javascript
        r'<iframe\s+[^>]*src\s*=\s*["\']?[^"\']*javascript:',  # iframe src with javascript
        r'expression\s*\(',  # CSS expression()
        r'<svg\s+[^>]*onload\s*=',  # SVG onload
        r'alert\s*\(',  # Common test payload like alert(
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    return False
```

## Deskripsi singkat

`detect_xss(input_string)` memindai `input_string` untuk pola-pola umum yang sering dipakai dalam serangan Cross-Site Scripting (XSS). Fungsi ini **mengembalikan `True`** jika ditemukan pola mencurigakan, dan **`False`** bila tidak.

> **Penting:** fungsi ini hanya *mendeteksi* pola berbahaya. Ia **tidak** melakukan sanitasi atau escaping. Jangan mengandalkannya sebagai satu-satunya proteksi terhadap XSS.

---

## Fungsi (signature)

```python
def detect_xss(input_string) -> bool
```

* **Parameter**: `input_string` (str) — string yang akan dipindai.
* **Return**: `True` jika potensi XSS terdeteksi; `False` jika tidak.

---

## Pola yang dicek

Detektor ini menggunakan daftar regular expression untuk menangkap pola-pola XSS umum, antara lain:

* Tag `<script>...</script>`
* Atribut event HTML: `onload=`, `onclick=`, dll. (`on\w+\s*=`)
* Protocol handler: `javascript:`, `vbscript:`, `data:`
* Tag `<img>` atau `<iframe>` dengan `src` yang mengandung `javascript:`
* CSS expression: `expression(`
* SVG with `onload`
* Payload test umum seperti `alert(`

Daftar pola lengkap ada di `xss.py` (lihat kode untuk regex lengkap).

---

## Contoh penggunaan

```python
from xss import detect_xss

user_input = "<script>alert('xss')</script>"
if detect_xss(user_input):
    # tolak atau log, jangan simpan / render langsung ke HTML
    raise ValueError('Input terdeteksi mengandung script berbahaya')

# jika False, lanjutkan proses (tetap lakukan sanitasi/escaping saat render)
```

---

## Integrasi yang disarankan

Fungsi ini cocok dipakai sebagai langkah deteksi awal (pre-save / pre-render) di aplikasi Flask/Django/others. Rekomendasi integrasi:

* Periksa semua input teks (judul, nama, deskripsi, komentar) sebelum menyimpan.
* Jika `detect_xss(...)` mengembalikan `True`, tolak input, log kejadian, dan tampilkan pesan generik ke user.
* Selalu **escape/encode** data saat menampilkan di HTML (mis. `escape()` di Jinja2).
* Gunakan Content Security Policy (CSP) pada level aplikasi untuk mitigasi tambahan.

---

## Batasan & Peringatan

* **Bukan sanitizer.** Regex-based detection mudah dilewati oleh payload yang terobfuskasi atau teknik encoding. Fungsi ini memberikan *indikasi*, bukan jaminan.
* **False positives/negatives** bisa terjadi. Uji dengan sample payload yang relevan.
* Untuk proteksi produksi, kombinasikan:

  * Output encoding/escaping (server-side templating atau frontend frameworks),
  * CSP header,
  * Library sanitasi terbukti (mis. DOMPurify di frontend),
  * Validasi tipe input dan panjang.

---

## Testing (contoh sederhana)

Contoh test minimal menggunakan `pytest`:

```python
def test_detect_script_tag():
    assert detect_xss("<script>alert(1)</script>") is True

def test_detect_onclick():
    assert detect_xss('<div onclick="do()">') is True

def test_benign_text():
    assert detect_xss('Hello world') is False
```

---

## Contribution & improving

* Perbaikan regex dan coverage pattern sangat welcome.
* Jika menambahkan sanitasi, pertimbangkan menaruh fungsi baru (mis. `sanitize_input()`) dan dokumentasikan trade-offs.

---

## License

Sertakan lisensi repo-mu (mis. MIT) di root repo. Jika ingin, tambahkan contoh `LICENSE` dan tambahkan catatan di README ini.

---

Jika kamu mau, aku bisa juga membuatkan:

* file `README.md` lengkap yang siap commit,
* atau `tests/test_xss.py` lengkap dengan beberapa payload (benign + malicious) untuk CI.

Mau aku generate salah satunya sekarang?
