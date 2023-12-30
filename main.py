#import kebutuhan
import re
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

# class parser berisi keperluan parsing
class CFGParser:
    # inisiasi dictionary rules
    def __init__(self):
        self.rules = {}

    # hilangkan unit of production yang menghasilkan satu non terminal
    def simplify_rules(self, key_list):
        for key, value in self.rules.items():
            if key in key_list:
                temp_list = []
                for prod in value:
                    if len(prod.split(" ")) == 2:
                        temp_list.append(prod)
                    else:
                        temp_list.extend(self.rules[prod])
                self.rules[key] = list(set(temp_list))

    # ubah rules cfg ke bentuk cnf
    def convert_rules_cnf(self):
        # baca dari file txt dan ubah rules ke bentuk dictionary python
        # dengan lhs adalah key dan rhs adalah value dari dictionary
        self.rules.clear()
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                lhs, rhs = map(str.strip, line.lower().split(" -> "))
                self.rules[lhs] = rhs.split(" | ")

        # gunakan fungsi simplify_rules ke unit of production
        # yang dapat menghasilkan satu non terminal
        self.simplify_rules(["nump", "adjp", "pp", "np", "vp"])
        self.simplify_rules(["s", "p", "o", "pel", "ket"])

        # sederhanakan rule of production k
        # agar menghasilkan tepat dua non terminal
        temp_dict = {}
        counter = 1
        temp_list = []
        for val in self.rules["k"]:
            if len(val.split(" ")) > 2:
                temp = val.split(" ")
                while len(temp) > 2:
                    check_str = " ".join(temp[:2])
                    is_found = False
                    for k, v in temp_dict.items():
                        if check_str == v:
                            is_found = True
                            temp.pop(0)
                            temp.pop(0)
                            temp.insert(0, k)
                            break
                    # buat rule of production baru jika diperlukan
                    if not is_found:
                        temp_dict["k" + str(counter)] = check_str
                        temp.pop(0)
                        temp.pop(0)
                        temp.insert(0, "k" + str(counter))
                        counter += 1
                temp_list.append(" ".join(temp))
            else:
                temp_list.append(val)

        self.rules["k"] = temp_list
                

        # tambahkan rules hasil penyederhanaan rule of production k
        for key, value in temp_dict.items():
            self.rules[key] = [value]

        # dapatkan hasil rules cnf
        return self.rules

    # parsing kalimat menggunakan algoritma cyk
    def cyk_algorithm(self, input_string):
        triangular_table = {} # inisiasi triangular table kosong
        prod_rules = self.convert_rules_cnf() # dapatkan rules cnf
        input_string = input_string.lower().split(" ") # ubah kalimat ke bentuk list kata

        # bentuk triangular table kosong
        for i in range(1, len(input_string) + 1):
            for j in range(i, len(input_string) + 1):
                triangular_table[(i, j)] = []

        # konstruksi triangular table
        for i in range(len(input_string), 0, -1):
            for j in range(1, i + 1):
                if j == j + len(input_string) - i: # isi untuk baris paling bawah
                    temp_list = [key for key, value in prod_rules.items() if input_string[j - 1] in value]
                    triangular_table[(j, j + len(input_string) - i)] = temp_list
                else: # isi untuk baris seterusnya
                    temp_list = []
                    result_list = []
                    # dapatkan gabungan non terminal
                    for k in range(len(input_string) - i):
                        first = triangular_table[(j, j + k)]
                        second = triangular_table[(j + k + 1, j + len(input_string) - i)]
                        temp_list.extend([fi + " " + se for fi in first for se in second])

                    # cari rule of production yang menghasilkan gabungan non terminal
                    for key, value in prod_rules.items():
                        result_list.extend([key for val in value if val in temp_list])

                    # masukkan rule of production ke dalam triangular table sesuai baris dan kolomnya
                    triangular_table[(j, j + len(input_string) - i)] = list(set(result_list))

        # cetak hasil triangular table untuk melihat hasil
        for key, (value, inside) in enumerate(triangular_table.items()):
            print(value, inside)

        # jika state awal (k) ada di baris paling atas kolom satu, maka kalimat memnuhi rules
        return 1 if "k" in triangular_table[(1, len(input_string))] else 0

# driver code
def main():
    # memanggil class untuk parsing
    parser = CFGParser()

    # mengambil semua terminal yang diterima rules
    not_accepted = ['k', 's', 'p', 'o', 'pel', 'ket', 'np', 'vp', 'adjp', 'pp']
    all_alphabet = parser.convert_rules_cnf()
    all_kata = [val for key, value in all_alphabet.items() if key not in not_accepted for val in value]

    # build GUI program
    window = tk.Tk()
    window.configure(bg="white")
    window.geometry("520x520")
    window.resizable(False, False)
    window.title("Parsing Kalimat B. Indo")

    frame = ttk.Frame(window)
    frame.pack(padx=20, pady=20, fill="x", expand=True)

    label_entry = ttk.Label(frame, text="Masukkan Kalimat Yang Ingin Diuji")
    label_entry.pack(padx=10, fill="x", expand=True)

    # input kalimat
    kalimat = tk.StringVar()
    entry = ttk.Entry(frame, textvariable=kalimat)
    entry.pack(padx=10, fill="x", expand=True)

    # fungsi untuk button mengeksekusi parsing
    def event():
        # mengecek apakah ada kata yang tidak ada dalam rules
        cek_kalimat = kalimat.get().lower()
        cek_kata = cek_kalimat.split()
        tidak_ketemu = 0
        kata_tidak_ketemu = []

        for kata in cek_kata:
            if kata not in all_kata:
                tidak_ketemu = 1
                kata_tidak_ketemu.append(kata)

        if tidak_ketemu == 1:
            kata = ', '.join(kata_tidak_ketemu)
            showinfo(title="Error!", message=f"{kata} tidak ditemukan!")
            return

        # parse kalimat input
        if parser.cyk_algorithm(cek_kalimat):
            showinfo(title="Diterima!", message="Kalimat Baku")
        else:
            showinfo(title="Ditolak.", message="Kalimat Tidak Baku")

    # build button dan fungsionalitasnya
    button = ttk.Button(frame, text="Cek", command=event)
    button.pack(padx=10, pady=10, fill="x", expand=True)

    # mainloop agar dapat mengecek kalimat berulang kali
    window.mainloop()

# eksekusi driver code
if __name__ == "__main__":
    main()
