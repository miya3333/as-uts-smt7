#!/usr/bin/env python3
"""
========================================================================================
PROJECT UJIAN TENGAH SEMESTER (UTS) - AUTOMATION SYSTEMS
PROGRAM STUDI TEKNIK INFORMATIKA - UNIVERSITAS PELITA BANGSA (TA 2025/2026)
========================================================================================
Mata Kuliah    : Automation Systems
Dosen Pengampu : Anggi Muhammad Rifa'i, M.Kom
Tema Proyek    : Online Book Catalog Organizer
Website Target : Gramedia (https://www.gramedia.com)

Integrasi Materi "Automate the Boring Stuff with Python":
- Chapter 9  : Regular Expressions (Ekstraksi nominal harga, sanitasi judul/penulis,
               ekstraksi pola ISBN-13, validasi URL)
- Chapter 10 : Reading and Writing Files (Penyimpanan respons mentah ke TXT, dataset
               terstruktur ke CSV dengan modul csv, dan laporan analitik ke TXT)
- Chapter 11 : Organizing Files (Modul pathlib.Path untuk direktori otomatis &
               zipfile untuk arsip backup otomatis)
- Chapter 12 : Command Line Programs (Argparse CLI dengan parameter --url, --keyword,
               --limit, --output, --backup)
- Chapter 13 : Web Scraping (Pengambilan data API internal/katalog Gramedia SPA Next.js
               dengan requests, penanganan pagination, dan BeautifulSoup)
========================================================================================
"""

import os
import sys
import re
import csv
import json
import zipfile
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

import requests
from bs4 import BeautifulSoup


# ======================================================================================
# KONFIGURASI GLOBAL & HEADERS (Chapter 13 - Web Scraping)
# ======================================================================================
BASE_DIR = Path(__file__).resolve().parent
GRAMEDIA_BASE_URL = "https://www.gramedia.com"
GRAMEDIA_API_ENDPOINT = "https://api-service.gramedia.com/api/v2/public/search-result-product"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://www.gramedia.com",
    "Referer": "https://www.gramedia.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}


# ======================================================================================
# CHAPTER 11: ORGANIZING FILES (Pathlib & Directory Management)
# ======================================================================================
def setup_directories(base_path: Path) -> Dict[str, Path]:
    """
    Membuat struktur folder kerja yang dibutuhkan secara otomatis menggunakan modul pathlib.Path.
    Folder yang dibuat:
    - data/   : Lokasi penyimpanan data mentah (raw data)
    - output/ : Lokasi file CSV terstruktur dan laporan ringkasan eksekusi
    - backup/ : Lokasi arsip ZIP hasil scraping

    Args:
        base_path (Path): Direktori dasar proyek.

    Returns:
        Dict[str, Path]: Dictionary berisi objek Path dari direktori yang dipastikan ada.
    """
    directories = {
        "data": base_path / "data",
        "output": base_path / "output",
        "backup": base_path / "backup",
    }

    for name, dir_path in directories.items():
        # Chapter 11: Membuat direktori aman (mkdir dengan parents=True & exist_ok=True)
        dir_path.mkdir(parents=True, exist_ok=True)

    return directories


def create_backup_archive(source_dir: Path, zip_dest_path: Path) -> bool:
    """
    Mengompresi seluruh isi direktori sumber (output/) ke dalam file ZIP arsip.
    Menggunakan modul standar zipfile sesuai materi Chapter 11 (Organizing Files).

    Args:
        source_dir (Path): Direktori yang akan diarsipkan.
        zip_dest_path (Path): Lokasi path file ZIP tujuan.

    Returns:
        bool: True jika backup berhasil dibuat, False jika gagal.
    """
    try:
        # Chapter 11: Kompresi direktori menggunakan ZipFile
        with zipfile.ZipFile(zip_dest_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    # Simpan arcname relatif agar isi ZIP terstruktur rapi
                    arcname = file_path.relative_to(source_dir)
                    zip_file.write(file_path, arcname=arcname)
        return True
    except Exception as exc:
        print(f"[!] Gagal membuat file arsip backup: {exc}", file=sys.stderr)
        return False


# ======================================================================================
# CHAPTER 9: REGULAR EXPRESSIONS (Pola Regex Pembersihan & Validasi Data)
# ======================================================================================
def clean_price_regex(raw_price: Any) -> int:
    """
    Regex Pola 1: Pembersihan dan ekstraksi nominal angka harga Rupiah.
    Menghapus semua karakter non-digit (seperti 'Rp', spasi, titik pemisah ribuan, atau ',00')
    sehingga menghasilkan nilai integer numerik murni.

    Contoh transformasi:
    - 'Rp 95.000'     -> 95000
    - 'Rp. 120.000,00' -> 120000
    - 78000            -> 78000

    Args:
        raw_price (Any): String harga mentah atau nilai numerik.

    Returns:
        int: Nominal harga numerik murni (0 jika tidak valid).
    """
    if raw_price is None:
        return 0

    price_str = str(raw_price).strip()

    # Potong bagian desimal sen seperti ',00' jika ada di akhir string
    price_str = re.sub(r",\d{2}$", "", price_str)

    # Pola Regex: Hanya ambil karakter digit numerik (\d)
    digits_only = re.sub(r"[^\d]", "", price_str)

    try:
        return int(digits_only) if digits_only else 0
    except ValueError:
        return 0


def sanitize_text_regex(raw_text: Optional[str]) -> str:
    """
    Regex Pola 2: Sanitasi teks string (Judul Buku, Penulis, Kategori/Format).
    Membersihkan tag HTML/entitas sisa dengan BeautifulSoup, karakter kontrol baris/tab,
    menghilangkan karakter aneh non-alfanumerik berbahaya, serta menormalkan spasi ganda.

    Args:
        raw_text (Optional[str]): String mentah teks.

    Returns:
        str: String teks yang bersih dan rapi.
    """
    if not raw_text:
        return "-"

    # Chapter 13 & 9: Bersihkan sisa entitas HTML menggunakan BeautifulSoup
    soup = BeautifulSoup(str(raw_text), "html.parser")
    clean_text = soup.get_text(separator=" ").strip()

    # Pola Regex 2a: Ubah karakter newline/tab menjadi spasi
    clean_text = re.sub(r"[\r\n\t]+", " ", clean_text)

    # Pola Regex 2b: Hapus karakter aneh yang tidak diinginkan untuk CSV
    clean_text = re.sub(r"[^\w\s\-\.\,\:\;\(\)\'\"\/]", "", clean_text)

    # Pola Regex 2c: Rapatkan spasi ganda berlebih menjadi spasi tunggal
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    return clean_text if clean_text else "-"


def extract_isbn_regex(text_source: str) -> Optional[str]:
    """
    Regex Pola 3: Ekstraksi nomor ISBN-13 standar buku dari string atau URL gambar.
    Mendeteksi pola ISBN 13 digit yang diawali '978' atau '979'.

    Contoh:
    'https://cdn.gramedia.com/uploads/items/9786026948007.jpg' -> '9786026948007'

    Args:
        text_source (str): Teks atau nama file gambar buku.

    Returns:
        Optional[str]: Nomor ISBN 13 digit jika ditemukan, atau None jika tidak ada.
    """
    if not text_source:
        return None
    match = re.search(r"(97[89]\d{10})", text_source)
    if match:
        return match.group(1)
    return None


def validate_url_regex(url: Optional[str]) -> bool:
    """
    Regex Pola 4: Validasi format tautan URL (Web Link / CDN Image Link).
    Memastikan URL diawali scheme http:// atau https:// dengan struktur domain yang valid.

    Args:
        url (Optional[str]): URL yang diuji.

    Returns:
        bool: True jika URL valid secara sintaksis, False sebaliknya.
    """
    if not url:
        return False
    url_pattern = re.compile(
        r"^https?://"  # Scheme http atau https
        r"(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}"  # Domain host
        r"(?::\d{1,5})?"  # Port opsional
        r"(?:/[^\s]*)?$",  # Path opsional
        re.IGNORECASE,
    )
    return bool(url_pattern.match(url.strip()))


# ======================================================================================
# CHAPTER 13: WEB SCRAPING (Requests & BeautifulSoup)
# ======================================================================================
def scrape_gramedia_catalog(
    base_url: str,
    keyword: str,
    limit: int = 30,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Mengambil data katalog buku dari website Gramedia berdasarkan kata kunci.
    Menggunakan reverse-engineering pada endpoint API internal katalog Gramedia
    (`/api/v2/public/search-result-product`) yang menyuplai data aplikasi Next.js/React.
    Mendukung pagination multi-halaman untuk memenuhi target limit record.

    Args:
        base_url (str): Base URL target (default: 'https://www.gramedia.com').
        keyword (str): Kata kunci pencarian (misal: 'python', 'komputer').
        limit (int): Target minimal jumlah record yang diambil.

    Returns:
        Tuple[List[Dict[str, Any]], str]:
            - List of dict kumpulan data buku terstruktur dan telah dibersihkan.
            - Raw payload JSON string gabungan untuk disimpan ke data/raw_data.txt.
    """
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    # Tentukan endpoint API
    api_endpoint = GRAMEDIA_API_ENDPOINT
    if base_url.rstrip("/") != GRAMEDIA_BASE_URL:
        api_endpoint = f"{base_url.rstrip('/')}/api/v2/public/search-result-product"

    scraped_books: List[Dict[str, Any]] = []
    raw_responses: List[Dict[str, Any]] = []

    page = 1
    per_page = 20  # Ukuran per halaman
    total_pages_available = 1

    print(f"\n[*] Memulai scraping katalog Gramedia untuk kata kunci: '{keyword}' (Target: {limit} buku)")
    print(f"[*] Endpoint Target: {api_endpoint}")

    while len(scraped_books) < limit and page <= total_pages_available:
        params = {
            "keyword": keyword,
            "per_page": per_page,
            "page": page,
        }

        print(f" -> Mengambil halaman {page}... (Terkumpul: {len(scraped_books)}/{limit})", end="\r")

        try:
            # Chapter 13: Mengirim HTTP GET request dengan requests
            response = session.get(api_endpoint, params=params, timeout=15)
            response.raise_for_status()
            payload = response.json()
        except requests.exceptions.Timeout:
            print(f"\n[!] Timeout saat menghubungi endpoint pada halaman {page}.")
            break
        except requests.exceptions.ConnectionError:
            print(f"\n[!] Kesalahan koneksi jaringan saat scraping halaman {page}.")
            break
        except requests.exceptions.RequestException as req_err:
            print(f"\n[!] HTTP Request Error: {req_err}")
            break
        except json.JSONDecodeError:
            print(f"\n[!] Gagal mem-parsing format respons JSON pada halaman {page}.")
            break

        # Simpan raw response mentah untuk kebutuhan Chapter 10
        raw_responses.append(payload)

        # Parsing metadata respon katalog
        meta = payload.get("meta", {})
        total_pages_available = meta.get("total_page", 1)

        items = payload.get("data", [])
        if not items:
            print(f"\n[*] Tidak ada produk lagi yang ditemukan pada halaman {page}.")
            break

        for item in items:
            if len(scraped_books) >= limit:
                break

            # Ekstraksi field mentah dari item
            raw_title = item.get("title") or item.get("name") or "-"
            raw_author = item.get("author") or "-"
            raw_format = item.get("format") or item.get("category_slugs") or "Buku Fisik"
            raw_final_price = item.get("final_price", 0)
            raw_slice_price = item.get("slice_price", 0)
            raw_discount = item.get("discount", 0)
            slug = item.get("slug", "")
            raw_image = item.get("image", "")
            raw_isbn = item.get("isbn") or ""

            # ==================================================================
            # Chapter 9: Pembersihan data menggunakan Regular Expressions
            # ==================================================================
            # Pola Regex 2: Sanitasi judul buku, nama penulis, dan format
            clean_title = sanitize_text_regex(raw_title)
            clean_author = sanitize_text_regex(raw_author)
            clean_format = sanitize_text_regex(raw_format)

            # Pola Regex 1: Ekstraksi dan pembersihan angka harga Rupiah
            harga_diskon = clean_price_regex(raw_final_price)
            harga_asli = clean_price_regex(raw_slice_price)
            if harga_asli == 0:
                harga_asli = harga_diskon

            # Pola Regex 3: Ekstraksi nomor ISBN-13 jika field isbn kosong
            detected_isbn = raw_isbn if raw_isbn else (extract_isbn_regex(raw_image) or "-")

            # Pola Regex 4: Validasi format URL gambar & URL detail
            image_url = raw_image if validate_url_regex(raw_image) else "-"
            detail_url = f"https://www.gramedia.com/products/{slug}" if slug else "-"

            book_record = {
                "id_produk": item.get("product_meta_id", "-"),
                "judul_buku": clean_title,
                "penulis": clean_author,
                "format_kategori": clean_format,
                "harga_asli": harga_asli,
                "harga_diskon": harga_diskon,
                "diskon_persen": raw_discount,
                "isbn": detected_isbn,
                "url_detail": detail_url,
                "url_gambar": image_url,
            }

            scraped_books.append(book_record)

        page += 1

    print(f"\n[+] Scraping selesai! Berhasil menghimpun {len(scraped_books)} data buku.")
    raw_combined_text = json.dumps(raw_responses, ensure_ascii=False, indent=2)
    return scraped_books, raw_combined_text


# ======================================================================================
# CHAPTER 10: READING AND WRITING FILES (File Handling & Reporting)
# ======================================================================================
def save_raw_data(raw_content: str, destination_path: Path) -> None:
    """
    Menyimpan respons mentah scraping ke file data/raw_data.txt menggunakan fungsi open().
    Sesuai materi Chapter 10: Reading and Writing Files.

    Args:
        raw_content (str): Isi respons mentah JSON / data string.
        destination_path (Path): Path lokasi data/raw_data.txt.
    """
    try:
        with open(destination_path, mode="w", encoding="utf-8") as file:
            file.write(raw_content)
        print(f"[+] Data mentah berhasil disimpan di: {destination_path}")
    except OSError as err:
        print(f"[!] Gagal menulis file raw data: {err}", file=sys.stderr)

def save_books_to_csv(books: List[Dict[str, Any]], destination_path: Path) -> None:
    """
    Menyimpan data buku terstruktur ke file CSV menggunakan modul bawaan csv.
    """

    if not books:
        print("[!] Dataset buku kosong, pembatalan penulisan CSV.", file=sys.stderr)
        return

    fieldnames = [
        "id_produk",
        "judul_buku",
        "penulis",
        "format_kategori",
        "harga_asli",
        "harga_diskon",
        "diskon_persen",
        "isbn",
        "url_detail",
        "url_gambar",
    ]

    try:
        with open(
            destination_path,
            mode="w",
            encoding="utf-8-sig",
            newline=""
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
                delimiter=","
            )

            writer.writeheader()
            writer.writerows(books)

        print(f"[+] Dataset terstruktur CSV tersimpan di: {destination_path}")

    except OSError as err:
        print(f"[!] Gagal menulis dataset CSV: {err}", file=sys.stderr)

def generate_execution_report(
    report_path: Path,
    keyword: str,
    target_url: str,
    total_scraped: int,
    books: List[Dict[str, Any]],
    backup_created: bool,
    backup_file_path: Optional[Path] = None,
) -> None:
    """
    Membuat file ringkasan laporan eksekusi otomatis ke output/laporan.txt.
    Menghitung metrik analitik: Rata-rata harga buku, harga terendah, harga tertinggi,
    dan status pembuatan arsip backup ZIP.

    Args:
        report_path (Path): Lokasi file laporan ringkasan.
        keyword (str): Kata kunci yang dicari.
        target_url (str): URL sumber scraping.
        total_scraped (int): Jumlah total buku yang didapat.
        books (List[Dict[str, Any]]): Kumpulan record buku.
        backup_created (bool): Status apakah file backup zip dibuat.
        backup_file_path (Optional[Path]): Lokasi file backup zip jika dibuat.
    """
    waktu_eksekusi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Hitung metrik statistik harga buku
    if books:
        prices = [b["harga_diskon"] for b in books if b["harga_diskon"] > 0]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
    else:
        avg_price = 0
        min_price = 0
        max_price = 0

    backup_info = (
        f"BERHASIL DIBUAT ({backup_file_path.name})"
        if backup_created and backup_file_path
        else "TIDAK DIAKTIFKAN"
    )

    report_content = f"""================================================================================
LAPORAN EKSEKUSI AUTOMATION SCRAPING & CATALOG ORGANIZER
Mata Kuliah    : Automation Systems
Program Studi  : Teknik Informatika - Universitas Pelita Bangsa
================================================================================

1. INFORMASI UMUM EKSEKUSI
--------------------------------------------------------------------------------
Tanggal & Waktu Eksekusi : {waktu_eksekusi}
Website Target           : {target_url}
Kata Kunci Pencarian     : "{keyword}"
Status Eksekusi          : SUKSES SELESAI

2. METRIK DAN STATISTIK PENGAMBILAN DATA
--------------------------------------------------------------------------------
Total Data Buku Berhasil : {total_scraped} buku
Rata-rata Harga Buku     : Rp {avg_price:,.2f}
Harga Termurah           : Rp {min_price:,.2f}
Harga Termahal           : Rp {max_price:,.2f}

3. STATUS PENYIMPANAN & MANAJEMEN FILE
--------------------------------------------------------------------------------
File Data Mentah (Raw)   : data/raw_data.txt
File Dataset (CSV)       : output/hasil_scraping.csv
File Laporan (TXT)       : output/laporan.txt
Status Arsip Backup      : {backup_info}
Lokasi File Backup ZIP   : {str(backup_file_path) if backup_created and backup_file_path else '-'}

================================================================================
Dibuat secara otomatis oleh Automated Scraping Pipeline (Python 3)
================================================================================
"""

    try:
        # Chapter 10: Menulis file laporan teks ringkasan
        with open(report_path, mode="w", encoding="utf-8") as file:
            file.write(report_content)
        print(f"[+] Laporan ringkasan eksekusi tersimpan di: {report_path}")
    except OSError as err:
        print(f"[!] Gagal menulis file laporan: {err}", file=sys.stderr)


# ======================================================================================
# CHAPTER 12: COMMAND LINE PROGRAMS (Argparse CLI Interface)
# ======================================================================================
def build_cli_parser() -> argparse.ArgumentParser:
    """
    Membangun antarmuka Command Line Interface (CLI) menggunakan argparse.
    Menyediakan parameter:
    - --url     : Target base URL katalog (default: https://www.gramedia.com)
    - --keyword : Kata kunci pencarian buku (default: python)
    - --limit   : Batas minimal record yang diambil (default: 30)
    - --output  : Nama custom file CSV output (default: hasil_scraping.csv)
    - --backup  : Flag boolean untuk memicu kompresi arsip ZIP folder output

    Returns:
        argparse.ArgumentParser: Objek parser yang telah dikonfigurasi.
    """
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Aplikasi Otomatisasi Scraping & Pengorganisasian Katalog Buku Gramedia\n"
            "UTS Automation Systems - Teknik Informatika Universitas Pelita Bangsa"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Contoh Penggunaan Terminal:\n"
            "  python main.py --keyword python --limit 30 --backup\n"
            "  python main.py --keyword 'data science' --limit 40 --output buku_ds.csv --backup\n"
            "  python main.py --url https://www.gramedia.com --keyword novel --limit 35\n"
        ),
    )

    parser.add_argument(
        "--url",
        type=str,
        default=GRAMEDIA_BASE_URL,
        help=f"Target URL / base website katalog (default: '{GRAMEDIA_BASE_URL}').",
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default="python",
        help="Kata kunci pencarian buku pada katalog (default: 'python').",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Batas minimal jumlah record data buku yang diambil (default: 30).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="hasil_scraping.csv",
        help="Nama file CSV hasil penyimpanan data terstruktur (default: 'hasil_scraping.csv').",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Flag boolean: Jika diaktifkan, otomatis membuat arsip ZIP di folder backup/.",
    )

    return parser


# ======================================================================================
# FUNGSI UTAMA (Main Workflow Pipeline)
# ======================================================================================
def print_banner() -> None:
    """Mencetak header terminal aplikasi."""
    banner = """
================================================================================
   UTS AUTOMATION SYSTEMS - PROGRAM STUDI TEKNIK INFORMATIKA
   UNIVERSITAS PELITA BANGSA (TA 2025/2026)
   TEMA: ONLINE BOOK CATALOG ORGANIZER (TARGET: GRAMEDIA.COM)
================================================================================
"""
    print(banner)


def print_terminal_summary(
    keyword: str,
    total_records: int,
    csv_file: Path,
    report_file: Path,
    raw_file: Path,
    backup_file: Optional[Path],
) -> None:
    """Menampilkan ringkasan hasil pemrosesan pada layar terminal (Persyaratan Teknis 8)."""
    print("\n" + "=" * 80)
    print("                    RINGKASAN STATUS PEMROSESAN OTOMATIS")
    print("=" * 80)
    print(f"  * Kata Kunci Pencarian : '{keyword}'")
    print(f"  * Total Data Buku      : {total_records} record berhasil diproses")
    print(f"  * Lokasi File Raw Data : {raw_file}")
    print(f"  * Lokasi File CSV      : {csv_file}")
    print(f"  * Lokasi File Laporan  : {report_file}")
    if backup_file and backup_file.exists():
        backup_size_kb = backup_file.stat().st_size / 1024
        print(f"  * Status Backup ZIP    : AKTIF -> {backup_file} ({backup_size_kb:.2f} KB)")
    else:
        print("  * Status Backup ZIP    : NONAKTIF (Gunakan argumen --backup untuk membuat)")
    print("=" * 80)
    print("  [V] Seluruh alur otomatisasi selesai dengan sukses tanpa kendala!\n")


def main() -> None:
    """Fungsi eksekusi entry-point aplikasi."""
    print_banner()

    # 1. Parsing argumen CLI (Chapter 12: Command Line Programs)
    parser = build_cli_parser()
    args = parser.parse_args()

    # Validasi input limit
    if args.limit <= 0:
        print("[!] Nilai --limit harus bilangan positif lebih dari 0.", file=sys.stderr)
        sys.exit(1)

    # 2. Persiapan struktur folder dinamis menggunakan pathlib.Path (Chapter 11: Organizing Files)
    dirs = setup_directories(BASE_DIR)
    raw_data_file = dirs["data"] / "raw_data.txt"
    csv_output_file = dirs["output"] / args.output
    report_output_file = dirs["output"] / "laporan.txt"
    backup_zip_file = dirs["backup"] / "backup_data.zip"

    # 3. Scraping data web dengan requests dan bs4 (Chapter 13: Web Scraping)
    try:
        books_data, raw_json_text = scrape_gramedia_catalog(
            base_url=args.url,
            keyword=args.keyword,
            limit=args.limit,
        )
    except Exception as scrape_err:
        print(f"\n[!] Terjadi kesalahan tidak terduga pada proses scraping: {scrape_err}", file=sys.stderr)
        sys.exit(1)

    # Penanganan data kosong / tidak ditemukan (Persyaratan Teknis 7)
    if not books_data:
        print(f"\n[!] PERINGATAN: Tidak ada data buku yang ditemukan untuk kata kunci '{args.keyword}'.", file=sys.stderr)
        print("[!] Silakan coba kata kunci lain seperti 'python', 'komputer', 'novel', atau 'bisnis'.", file=sys.stderr)
        sys.exit(1)

    # 4. Penyimpanan data mentah ke data/raw_data.txt (Chapter 10: Reading & Writing Files)
    save_raw_data(raw_json_text, raw_data_file)

    # 5. Penyimpanan dataset buku ke output/*.csv (Chapter 10: Reading & Writing Files)
    save_books_to_csv(books_data, csv_output_file)

    # 6. Pembuatan backup arsip zip jika opsi --backup diberikan (Chapter 11: Organizing Files)
    backup_success = False
    if args.backup:
        print(f"\n[*] Menjalankan proses backup folder '{dirs['output'].name}' ke ZIP...")
        # Simpan laporan terlebih dahulu agar laporan masuk ke dalam arsip zip
        generate_execution_report(
            report_path=report_output_file,
            keyword=args.keyword,
            target_url=args.url,
            total_scraped=len(books_data),
            books=books_data,
            backup_created=True,
            backup_file_path=backup_zip_file,
        )
        backup_success = create_backup_archive(dirs["output"], backup_zip_file)
        if backup_success:
            print(f"[+] Backup zip berhasil dibuat di: {backup_zip_file}")
    else:
        # Buat laporan tanpa backup
        generate_execution_report(
            report_path=report_output_file,
            keyword=args.keyword,
            target_url=args.url,
            total_scraped=len(books_data),
            books=books_data,
            backup_created=False,
            backup_file_path=None,
        )

    # 7. Menampilkan ringkasan pemrosesan di layar terminal (Persyaratan Teknis 8)
    print_terminal_summary(
        keyword=args.keyword,
        total_records=len(books_data),
        csv_file=csv_output_file,
        report_file=report_output_file,
        raw_file=raw_data_file,
        backup_file=backup_zip_file if backup_success else None,
    )


if __name__ == "__main__":
    main()
