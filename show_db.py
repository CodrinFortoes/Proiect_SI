from database import init_db, get_session
from seed import run_seed
from crud import (
    get_all_algorithms, get_all_frameworks, get_all_keys, get_all_files,
    get_all_operations, get_all_performances,
    create_key, create_file, create_crypto_operation, create_performance,
    get_algorithm_by_name, get_framework_by_name
)
import os


def print_table(title, headers, rows):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_row = "|" + "|".join(f" {h:<{col_widths[i]}} " for i, h in enumerate(headers)) + "|"

    print(f"\n{'=' * len(separator)}")
    print(f"  {title}")
    print(separator)
    print(header_row)
    print(separator)
    for row in rows:
        print("|" + "|".join(f" {str(v):<{col_widths[i]}} " for i, v in enumerate(row)) + "|")
    print(separator)
    print(f"  Total: {len(rows)} inregistrari")


def add_demo_data(session):
    aes = get_algorithm_by_name(session, "AES-256-CBC")
    rsa = get_algorithm_by_name(session, "RSA-2048")
    openssl = get_framework_by_name(session, "OpenSSL")
    pycrypto = get_framework_by_name(session, "PyCryptodome")

    if not aes or not openssl:
        print("[!] Ruleaza mai intai seed.py")
        return

    k1 = create_key(session, aes.id, b"0123456789abcdef0123456789abcdef",
                     256, iv=b"abcdef0123456789", label="Cheie AES demo")
    k2 = create_key(session, rsa.id, b"rsa_key_placeholder", 2048,
                     public_key=b"rsa_pub_demo", private_key=b"rsa_priv_demo",
                     label="Cheie RSA demo")

    f1 = create_file(session, "raport.pdf", "C:/Users/docs/raport.pdf", 2048000,
                     file_hash="a1b2c3d4e5f6...")
    f2 = create_file(session, "poze.zip", "C:/Users/docs/poze.zip", 5120000,
                     file_hash="f6e5d4c3b2a1...")

    op1 = create_crypto_operation(session, f1.id, aes.id, openssl.id, k1.id,
                                   "encrypt", output_path="C:/Users/docs/raport.pdf.enc",
                                   status="success")
    op2 = create_crypto_operation(session, f2.id, aes.id, pycrypto.id, k1.id,
                                   "encrypt", output_path="C:/Users/docs/poze.zip.enc",
                                   status="success")
    op3 = create_crypto_operation(session, f1.id, rsa.id, openssl.id, k2.id,
                                   "encrypt", output_path="C:/Users/docs/raport.pdf.rsa",
                                   status="success")

    create_performance(session, op1.id, execution_time_ms=12.5, memory_usage_kb=1024,
                       cpu_usage_percent=15.3, input_size_bytes=2048000,
                       output_size_bytes=2048016, throughput_mbps=156.2)
    create_performance(session, op2.id, execution_time_ms=28.7, memory_usage_kb=2048,
                       cpu_usage_percent=22.1, input_size_bytes=5120000,
                       output_size_bytes=5120016, throughput_mbps=170.4)
    create_performance(session, op3.id, execution_time_ms=145.3, memory_usage_kb=4096,
                       cpu_usage_percent=45.8, input_size_bytes=2048000,
                       output_size_bytes=2048256, throughput_mbps=13.4)

    print("[+] Date demo adaugate cu succes!")


def show_all_tables(session):
    algs = get_all_algorithms(session)
    print_table("ALGORITHMS (Algoritmi)",
                ["ID", "Nume", "Tip", "Key Size", "Block Size", "Mode"],
                [(a.id, a.name, a.type, a.key_size, a.block_size or "-", a.mode or "-") for a in algs])

    fws = get_all_frameworks(session)
    print_table("FRAMEWORKS",
                ["ID", "Nume", "Versiune", "Limbaj"],
                [(f.id, f.name, f.version or "-", f.language or "-") for f in fws])

    keys = get_all_keys(session)
    print_table("KEYS (Chei)",
                ["ID", "Algoritm ID", "Dimensiune (biti)", "Status", "Label", "Creat la"],
                [(k.id, k.algorithm_id, k.key_size_bits, k.status, k.label or "-",
                  str(k.created_at)[:19]) for k in keys])

    files = get_all_files(session)
    print_table("FILES (Fisiere)",
                ["ID", "Nume", "Dimensiune", "Status", "Hash"],
                [(f.id, f.original_name, f"{f.file_size:,} B", f.status,
                  (f.file_hash or "-")[:20]) for f in files])

    ops = get_all_operations(session)
    print_table("CRYPTO_OPERATIONS (Operatii)",
                ["ID", "Fisier ID", "Algoritm ID", "Framework ID", "Cheie ID", "Tip", "Status"],
                [(o.id, o.file_id, o.algorithm_id, o.framework_id, o.key_id,
                  o.operation_type, o.status) for o in ops])

    perfs = get_all_performances(session)
    print_table("PERFORMANCES (Performante)",
                ["ID", "Operatie ID", "Timp (ms)", "Memorie (KB)", "CPU %", "Input (B)", "Throughput (MB/s)"],
                [(p.id, p.operation_id, p.execution_time_ms, p.memory_usage_kb,
                  p.cpu_usage_percent, f"{p.input_size_bytes:,}" if p.input_size_bytes else "-",
                  p.throughput_mbps) for p in perfs])


if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), "crypto_manager.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    run_seed()

    session = get_session()
    add_demo_data(session)

    print("\n" + "=" * 60)
    print("  VIZUALIZARE BAZA DE DATE - CRYPTO MANAGER")
    print("=" * 60)

    show_all_tables(session)
    session.close()