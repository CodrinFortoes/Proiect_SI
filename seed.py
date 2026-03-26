from database import init_db, get_session
from crud import (
    create_algorithm, get_algorithm_by_name,
    create_framework, get_framework_by_name,
)


def seed_algorithms(session):
    algorithms = [
        {
            "name": "AES-256-CBC",
            "alg_type": "symmetric",
            "key_size": 256,
            "block_size": 128,
            "mode": "CBC",
            "description": "AES cu cheie de 256 biti, modul CBC (Cipher Block Chaining). "
                           "Necesita IV de 16 bytes. Padding PKCS7."
        },
        {
            "name": "AES-256-GCM",
            "alg_type": "symmetric",
            "key_size": 256,
            "block_size": 128,
            "mode": "GCM",
            "description": "AES cu cheie de 256 biti, modul GCM (Galois/Counter Mode). "
                           "Ofera autentificare integrata (AEAD). Nonce de 12 bytes."
        },
        {
            "name": "AES-128-CBC",
            "alg_type": "symmetric",
            "key_size": 128,
            "block_size": 128,
            "mode": "CBC",
            "description": "AES cu cheie de 128 biti, modul CBC."
        },
        {
            "name": "RSA-2048",
            "alg_type": "asymmetric",
            "key_size": 2048,
            "block_size": None,
            "mode": None,
            "description": "RSA cu cheie de 2048 biti. Folosit pentru criptarea cheilor simetrice "
                           "(envelope encryption) sau semnare digitala."
        },
        {
            "name": "RSA-4096",
            "alg_type": "asymmetric",
            "key_size": 4096,
            "block_size": None,
            "mode": None,
            "description": "RSA cu cheie de 4096 biti. Securitate sporita, performanta mai redusa."
        },
    ]

    added = 0
    for alg_data in algorithms:
        if not get_algorithm_by_name(session, alg_data["name"]):
            create_algorithm(session, **alg_data)
            added += 1
            print(f"  + Algoritm adaugat: {alg_data['name']}")
        else:
            print(f"  - Algoritm existent: {alg_data['name']}")
    return added


def seed_frameworks(session):
    frameworks = [
        {
            "name": "OpenSSL",
            "version": "3.0",
            "language": "C",
            "description": "Biblioteca standard de criptografie. "
                           "Apelata prin subprocess din Python (openssl CLI)."
        },
        {
            "name": "PyCryptodome",
            "version": "3.20",
            "language": "Python",
            "description": "Biblioteca Python nativa de criptografie. "
                           "Alternativa la OpenSSL pentru compararea performantelor."
        },
    ]

    added = 0
    for fw_data in frameworks:
        if not get_framework_by_name(session, fw_data["name"]):
            create_framework(session, **fw_data)
            added += 1
            print(f"  + Framework adaugat: {fw_data['name']}")
        else:
            print(f"  - Framework existent: {fw_data['name']}")
    return added


def run_seed():
    init_db()
    session = get_session()

    print("\n=== SEED: Algoritmi ===")
    alg_count = seed_algorithms(session)

    print("\n=== SEED: Framework-uri ===")
    fw_count = seed_frameworks(session)

    session.close()
    print(f"\n[SEED] Finalizat: {alg_count} algoritmi, {fw_count} framework-uri adaugate.\n")


if __name__ == "__main__":
    run_seed()