import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from models import Base
from crud import (
    create_algorithm, get_algorithm_by_id, get_algorithm_by_name,
    get_all_algorithms, update_algorithm, delete_algorithm,
    create_framework, get_framework_by_id, get_framework_by_name,
    get_all_frameworks, update_framework, delete_framework,
    create_key, get_key_by_id, get_keys_by_algorithm,
    get_all_keys, update_key, revoke_key, delete_key,
    create_file, get_file_by_id, get_all_files,
    get_files_by_status, update_file, delete_file,
    create_crypto_operation, get_operation_by_id, get_all_operations,
    get_operations_by_file, update_operation, delete_operation,
    create_performance, get_performance_by_id, get_performance_by_operation,
    get_all_performances, update_performance, delete_performance,
)


class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)

        @event.listens_for(cls.engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        cls.SessionFactory = sessionmaker(bind=cls.engine)

    def setUp(self):
        Base.metadata.create_all(bind=self.engine)
        self.session = self.SessionFactory()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)


class TestAlgorithmCRUD(BaseTestCase):

    def test_create_algorithm(self):
        alg = create_algorithm(self.session, "AES-256-CBC", "symmetric", 256,
                               block_size=128, mode="CBC",
                               description="AES 256 CBC")
        self.assertIsNotNone(alg.id)
        self.assertEqual(alg.name, "AES-256-CBC")
        self.assertEqual(alg.type, "symmetric")
        self.assertEqual(alg.key_size, 256)
        self.assertEqual(alg.block_size, 128)
        self.assertEqual(alg.mode, "CBC")

    def test_get_algorithm_by_id(self):
        alg = create_algorithm(self.session, "RSA-2048", "asymmetric", 2048)
        fetched = get_algorithm_by_id(self.session, alg.id)
        self.assertEqual(fetched.name, "RSA-2048")

    def test_get_algorithm_by_name(self):
        create_algorithm(self.session, "AES-128-CBC", "symmetric", 128, mode="CBC")
        fetched = get_algorithm_by_name(self.session, "AES-128-CBC")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.key_size, 128)

    def test_get_all_algorithms(self):
        create_algorithm(self.session, "AES-256-CBC", "symmetric", 256)
        create_algorithm(self.session, "RSA-2048", "asymmetric", 2048)
        all_algs = get_all_algorithms(self.session)
        self.assertEqual(len(all_algs), 2)

    def test_update_algorithm(self):
        alg = create_algorithm(self.session, "AES-256-CBC", "symmetric", 256)
        updated = update_algorithm(self.session, alg.id, description="Updated desc")
        self.assertEqual(updated.description, "Updated desc")

    def test_delete_algorithm(self):
        alg = create_algorithm(self.session, "AES-256-CBC", "symmetric", 256)
        result = delete_algorithm(self.session, alg.id)
        self.assertTrue(result)
        self.assertIsNone(get_algorithm_by_id(self.session, alg.id))

    def test_delete_nonexistent(self):
        result = delete_algorithm(self.session, 9999)
        self.assertFalse(result)


class TestFrameworkCRUD(BaseTestCase):

    def test_create_framework(self):
        fw = create_framework(self.session, "OpenSSL", version="3.0", language="C")
        self.assertIsNotNone(fw.id)
        self.assertEqual(fw.name, "OpenSSL")

    def test_get_framework_by_name(self):
        create_framework(self.session, "PyCryptodome", version="3.20", language="Python")
        fetched = get_framework_by_name(self.session, "PyCryptodome")
        self.assertEqual(fetched.language, "Python")

    def test_update_framework(self):
        fw = create_framework(self.session, "OpenSSL", version="3.0")
        updated = update_framework(self.session, fw.id, version="3.2")
        self.assertEqual(updated.version, "3.2")

    def test_delete_framework(self):
        fw = create_framework(self.session, "OpenSSL")
        result = delete_framework(self.session, fw.id)
        self.assertTrue(result)


class TestKeyCRUD(BaseTestCase):

    def _create_alg(self):
        return create_algorithm(self.session, "AES-256-CBC", "symmetric", 256)

    def test_create_key_symmetric(self):
        alg = self._create_alg()
        key = create_key(self.session, alg.id, b"0123456789abcdef" * 2,
                         256, iv=b"1234567890abcdef", label="Test Key AES")
        self.assertIsNotNone(key.id)
        self.assertEqual(key.status, "active")
        self.assertEqual(key.key_size_bits, 256)
        self.assertIsNotNone(key.iv)

    def test_create_key_asymmetric(self):
        alg = create_algorithm(self.session, "RSA-2048", "asymmetric", 2048)
        key = create_key(self.session, alg.id, b"dummy_key_data", 2048,
                         public_key=b"pub_key_data", private_key=b"priv_key_data",
                         label="Test RSA Key")
        self.assertIsNotNone(key.public_key)
        self.assertIsNotNone(key.private_key)

    def test_revoke_key(self):
        alg = self._create_alg()
        key = create_key(self.session, alg.id, b"test_key_data", 256)
        revoked = revoke_key(self.session, key.id)
        self.assertEqual(revoked.status, "revoked")

    def test_get_keys_by_algorithm(self):
        alg = self._create_alg()
        create_key(self.session, alg.id, b"key1", 256)
        create_key(self.session, alg.id, b"key2", 256)
        keys = get_keys_by_algorithm(self.session, alg.id)
        self.assertEqual(len(keys), 2)

    def test_delete_key(self):
        alg = self._create_alg()
        key = create_key(self.session, alg.id, b"to_delete", 256)
        result = delete_key(self.session, key.id)
        self.assertTrue(result)


class TestFileCRUD(BaseTestCase):

    def test_create_file(self):
        f = create_file(self.session, "document.pdf", "/home/user/document.pdf",
                        1024000, file_hash="abc123sha256hash")
        self.assertIsNotNone(f.id)
        self.assertEqual(f.status, "original")
        self.assertEqual(f.file_size, 1024000)

    def test_update_file_status(self):
        f = create_file(self.session, "doc.txt", "/tmp/doc.txt", 500)
        updated = update_file(self.session, f.id, status="encrypted",
                              encrypted_path="/tmp/doc.txt.enc")
        self.assertEqual(updated.status, "encrypted")
        self.assertIsNotNone(updated.encrypted_path)

    def test_get_files_by_status(self):
        create_file(self.session, "a.txt", "/a.txt", 100, status="original")
        create_file(self.session, "b.txt", "/b.txt", 200, status="encrypted")
        create_file(self.session, "c.txt", "/c.txt", 300, status="encrypted")
        encrypted = get_files_by_status(self.session, "encrypted")
        self.assertEqual(len(encrypted), 2)

    def test_delete_file(self):
        f = create_file(self.session, "del.txt", "/del.txt", 10)
        result = delete_file(self.session, f.id)
        self.assertTrue(result)


class TestCryptoOperationCRUD(BaseTestCase):

    def _setup_dependencies(self):
        alg = create_algorithm(self.session, "AES-256-CBC", "symmetric", 256)
        fw  = create_framework(self.session, "OpenSSL", version="3.0")
        key = create_key(self.session, alg.id, b"test_key_32bytes_long!!", 256)
        f   = create_file(self.session, "test.txt", "/tmp/test.txt", 1024)
        return alg, fw, key, f

    def test_create_operation(self):
        alg, fw, key, f = self._setup_dependencies()
        op = create_crypto_operation(self.session, f.id, alg.id, fw.id, key.id,
                                     "encrypt", output_path="/tmp/test.txt.enc")
        self.assertIsNotNone(op.id)
        self.assertEqual(op.operation_type, "encrypt")
        self.assertEqual(op.status, "pending")

    def test_update_operation_status(self):
        alg, fw, key, f = self._setup_dependencies()
        op = create_crypto_operation(self.session, f.id, alg.id, fw.id, key.id, "encrypt")
        updated = update_operation(self.session, op.id, status="success")
        self.assertEqual(updated.status, "success")

    def test_get_operations_by_file(self):
        alg, fw, key, f = self._setup_dependencies()
        create_crypto_operation(self.session, f.id, alg.id, fw.id, key.id, "encrypt")
        create_crypto_operation(self.session, f.id, alg.id, fw.id, key.id, "decrypt")
        ops = get_operations_by_file(self.session, f.id)
        self.assertEqual(len(ops), 2)

    def test_operation_relationships(self):
        alg, fw, key, f = self._setup_dependencies()
        op = create_crypto_operation(self.session, f.id, alg.id, fw.id, key.id, "encrypt")
        fetched = get_operation_by_id(self.session, op.id)
        self.assertEqual(fetched.algorithm.name, "AES-256-CBC")
        self.assertEqual(fetched.framework.name, "OpenSSL")
        self.assertEqual(fetched.file.original_name, "test.txt")

    def test_delete_operation(self):
        alg, fw, key, f = self._setup_dependencies()
        op = create_crypto_operation(self.session, f.id, alg.id, fw.id, key.id, "encrypt")
        result = delete_operation(self.session, op.id)
        self.assertTrue(result)


class TestPerformanceCRUD(BaseTestCase):

    def _setup_operation(self):
        alg = create_algorithm(self.session, "AES-256-CBC", "symmetric", 256)
        fw  = create_framework(self.session, "OpenSSL")
        key = create_key(self.session, alg.id, b"key_data_32bytes_long!!!", 256)
        f   = create_file(self.session, "perf.txt", "/tmp/perf.txt", 2048)
        op  = create_crypto_operation(self.session, f.id, alg.id, fw.id, key.id, "encrypt")
        return op

    def test_create_performance(self):
        op = self._setup_operation()
        perf = create_performance(
            self.session, op.id,
            execution_time_ms=45.3,
            memory_usage_kb=1280.5,
            cpu_usage_percent=23.1,
            input_size_bytes=2048,
            output_size_bytes=2064,
            throughput_mbps=0.043
        )
        self.assertIsNotNone(perf.id)
        self.assertAlmostEqual(perf.execution_time_ms, 45.3)
        self.assertAlmostEqual(perf.memory_usage_kb, 1280.5)

    def test_get_performance_by_operation(self):
        op = self._setup_operation()
        create_performance(self.session, op.id, execution_time_ms=10.0)
        perf = get_performance_by_operation(self.session, op.id)
        self.assertIsNotNone(perf)

    def test_update_performance(self):
        op = self._setup_operation()
        perf = create_performance(self.session, op.id, execution_time_ms=10.0)
        updated = update_performance(self.session, perf.id,
                                     execution_time_ms=12.5, memory_usage_kb=900.0)
        self.assertAlmostEqual(updated.execution_time_ms, 12.5)
        self.assertAlmostEqual(updated.memory_usage_kb, 900.0)

    def test_performance_cascade_delete(self):
        op = self._setup_operation()
        perf = create_performance(self.session, op.id, execution_time_ms=5.0)
        perf_id = perf.id
        delete_operation(self.session, op.id)
        self.assertIsNone(get_performance_by_id(self.session, perf_id))


class TestForeignKeys(BaseTestCase):

    def test_cascade_delete_algorithm_keys(self):
        alg = create_algorithm(self.session, "AES-256-CBC", "symmetric", 256)
        create_key(self.session, alg.id, b"key1", 256)
        create_key(self.session, alg.id, b"key2", 256)
        delete_algorithm(self.session, alg.id)
        self.assertEqual(len(get_all_keys(self.session)), 0)

    def test_cascade_delete_file_operations(self):
        alg = create_algorithm(self.session, "AES-256-CBC", "symmetric", 256)
        fw  = create_framework(self.session, "OpenSSL")
        key = create_key(self.session, alg.id, b"key_data", 256)
        f   = create_file(self.session, "cascade.txt", "/cascade.txt", 100)
        op  = create_crypto_operation(self.session, f.id, alg.id, fw.id, key.id, "encrypt")
        create_performance(self.session, op.id, execution_time_ms=1.0)

        delete_file(self.session, f.id)
        self.assertEqual(len(get_all_operations(self.session)), 0)
        self.assertEqual(len(get_all_performances(self.session)), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)