import random
import tkinter as tk


# ================= FUNGSI MATEMATIKA =================

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def is_akar_primitif(g, p):
    # g akar primitif jika g^i mod p tidak pernah = 1 sebelum i = p-1
    for i in range(1, p - 1):
        if pow(g, i, p) == 1:
            return False
    return True


def cari_akar_primitif(p):
    for g in range(2, p):
        if is_akar_primitif(g, p):
            return g


# ================= DIFFIE-HELLMAN =================

def dh_kunci_publik(g, rahasia, p):
    return pow(g, rahasia, p)          # X = g^x mod p


def dh_kunci_sesi(publik_lawan, rahasia, p):
    return pow(publik_lawan, rahasia, p)   # K = Y^x mod p


# ================= ELGAMAL =================

def elgamal_buat_kunci(p, g, x):
    return pow(g, x, p)                # y = g^x mod p


def elgamal_enkripsi(m, p, g, y, k):
    a = pow(g, k, p)                   # a = g^k mod p
    b = (pow(y, k, p) * m) % p         # b = y^k * m mod p
    return a, b


def elgamal_dekripsi(a, b, p, x):
    return (b * pow(a, p - 1 - x, p)) % p   # m = b * a^(p-1-x) mod p


# ================= BACA INPUT =================

def baca(entry):
    teks = entry.get().strip()
    return int(teks) if teks else None


def ambil_p_g():
    p = baca(e_p) or 2357
    if not is_prime(p):
        raise ValueError("p harus bilangan prima")
    g = baca(e_g) or cari_akar_primitif(p)
    if not (1 < g < p and is_akar_primitif(g, p)):
        raise ValueError(f"g = {g} bukan akar primitif mod {p}")
    return p, g


def ambil_rahasia(entry, p):
    n = baca(entry) or random.randint(2, p - 2)
    if not 1 <= n <= p - 2:
        raise ValueError(f"Nilai rahasia harus 1 .. {p - 2}")
    return n


# ================= JALANKAN + TAMPILKAN =================

def jalankan_dh():
    p, g = ambil_p_g()
    x = ambil_rahasia(e_x, p)
    y = ambil_rahasia(e_y, p)

    X = dh_kunci_publik(g, x, p)
    Y = dh_kunci_publik(g, y, p)
    K1 = dh_kunci_sesi(Y, x, p)
    K2 = dh_kunci_sesi(X, y, p)

    return (
        "=== DIFFIE-HELLMAN ===\n"
        f"1. Parameter publik: p = {p}, g = {g}\n\n"
        f"2. Alice pilih rahasia x = {x}\n"
        f"   X = g^x mod p = {g}^{x} mod {p} = {X}\n\n"
        f"3. Bob pilih rahasia y = {y}\n"
        f"   Y = g^y mod p = {g}^{y} mod {p} = {Y}\n\n"
        f"4. Alice kirim X = {X} ke Bob, Bob kirim Y = {Y} ke Alice\n\n"
        f"5. Alice: K  = Y^x mod p = {Y}^{x} mod {p} = {K1}\n"
        f"   Bob  : K' = X^y mod p = {X}^{y} mod {p} = {K2}\n\n"
        f"6. K = K' ? {K1 == K2}  -> kunci sesi = {K1}"
    )


def jalankan_elgamal():
    p, g = ambil_p_g()
    x = ambil_rahasia(e_x, p)
    pesan = e_pesan.get()
    if not pesan:
        raise ValueError("Pesan tidak boleh kosong")
    if any(ord(c) >= p for c in pesan):
        raise ValueError("p terlalu kecil, harus lebih besar dari kode ASCII huruf")

    # 1. Pembangkitan kunci
    y = elgamal_buat_kunci(p, g, x)
    hasil = [
        "=== ELGAMAL ===",
        "1. PEMBANGKITAN KUNCI",
        f"   p = {p}, g = {g}, x (privat) = {x}",
        f"   y = g^x mod p = {g}^{x} mod {p} = {y}",
        f"   Kunci publik = (y={y}, g={g}, p={p}), kunci privat = (x={x}, p={p})",
        "",
        "2. ENKRIPSI (tiap huruf = 1 blok m)",
    ]

    # 2. Enkripsi
    cipher = []
    for c in pesan:
        m = ord(c)
        k = baca(e_k) or random.randint(1, p - 2)
        a, b = elgamal_enkripsi(m, p, g, y, k)
        cipher.append((a, b))
        hasil.append(f"   '{c}' m={m}, k={k} -> a={g}^{k} mod {p}={a}, "
                     f"b={y}^{k}*{m} mod {p}={b}")

    # 3. Dekripsi
    hasil += ["", "3. DEKRIPSI"]
    plain = ""
    for a, b in cipher:
        m = elgamal_dekripsi(a, b, p, x)
        plain += chr(m)
        hasil.append(f"   (a={a}, b={b}) -> m = {b}*{a}^{p - 1 - x} mod {p}"
                     f" = {m} -> '{chr(m)}'")

    hasil += ["", f"Plaintext awal : {pesan}", f"Hasil dekripsi : {plain}"]
    return "\n".join(hasil)


def aman(fungsi):
    out.delete("1.0", tk.END)
    try:
        out.insert(tk.END, fungsi())
    except ValueError as err:
        out.insert(tk.END, f"ERROR: {err}")


# ================= TAMPILAN (UI) =================

root = tk.Tk()
root.title("Diffie-Hellman & ElGamal")


def input_baris(baris, label):
    tk.Label(root, text=label).grid(row=baris, column=0, sticky="w")
    e = tk.Entry(root, width=40)
    e.grid(row=baris, column=1, padx=5, pady=2)
    return e


e_p = input_baris(0, "p (prima)")
e_g = input_baris(1, "g (akar primitif)")
e_x = input_baris(2, "x (rahasia Alice / privat)")
e_y = input_baris(3, "y (rahasia Bob, DH)")
e_k = input_baris(4, "k (ElGamal)")
e_pesan = input_baris(5, "Pesan (ElGamal)")
tk.Label(root, text="Kosongkan = otomatis (p=2357, sisanya acak)",
         fg="gray").grid(row=6, column=0, columnspan=2)

tk.Button(root, text="Diffie-Hellman",
          command=lambda: aman(jalankan_dh)).grid(row=7, column=0, pady=5)
tk.Button(root, text="ElGamal",
          command=lambda: aman(jalankan_elgamal)).grid(row=7, column=1, pady=5)

out = tk.Text(root, width=95, height=25, font=("Consolas", 10))
out.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()