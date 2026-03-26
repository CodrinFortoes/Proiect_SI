from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import Algorithm, Framework, Key, File, CryptoOperation, Performance


def create_algorithm(session: Session, name: str, alg_type: str, key_size: int,
                     block_size: int = None, mode: str = None,
                     description: str = None) -> Algorithm:
    alg = Algorithm(
        name=name, type=alg_type, key_size=key_size,
        block_size=block_size, mode=mode, description=description
    )
    session.add(alg)
    session.commit()
    session.refresh(alg)
    return alg


def get_algorithm_by_id(session: Session, alg_id: int) -> Optional[Algorithm]:
    return session.query(Algorithm).filter(Algorithm.id == alg_id).first()


def get_algorithm_by_name(session: Session, name: str) -> Optional[Algorithm]:
    return session.query(Algorithm).filter(Algorithm.name == name).first()


def get_all_algorithms(session: Session) -> list[Algorithm]:
    return session.query(Algorithm).all()


def update_algorithm(session: Session, alg_id: int, **kwargs) -> Optional[Algorithm]:
    alg = get_algorithm_by_id(session, alg_id)
    if not alg:
        return None
    for key, value in kwargs.items():
        if hasattr(alg, key):
            setattr(alg, key, value)
    session.commit()
    session.refresh(alg)
    return alg


def delete_algorithm(session: Session, alg_id: int) -> bool:
    alg = get_algorithm_by_id(session, alg_id)
    if not alg:
        return False
    session.delete(alg)
    session.commit()
    return True


def create_framework(session: Session, name: str, version: str = None,
                     language: str = None, description: str = None) -> Framework:
    fw = Framework(name=name, version=version, language=language, description=description)
    session.add(fw)
    session.commit()
    session.refresh(fw)
    return fw


def get_framework_by_id(session: Session, fw_id: int) -> Optional[Framework]:
    return session.query(Framework).filter(Framework.id == fw_id).first()


def get_framework_by_name(session: Session, name: str) -> Optional[Framework]:
    return session.query(Framework).filter(Framework.name == name).first()


def get_all_frameworks(session: Session) -> list[Framework]:
    return session.query(Framework).all()


def update_framework(session: Session, fw_id: int, **kwargs) -> Optional[Framework]:
    fw = get_framework_by_id(session, fw_id)
    if not fw:
        return None
    for key, value in kwargs.items():
        if hasattr(fw, key):
            setattr(fw, key, value)
    session.commit()
    session.refresh(fw)
    return fw


def delete_framework(session: Session, fw_id: int) -> bool:
    fw = get_framework_by_id(session, fw_id)
    if not fw:
        return False
    session.delete(fw)
    session.commit()
    return True


def create_key(session: Session, algorithm_id: int, key_data: bytes,
               key_size_bits: int, iv: bytes = None,
               public_key: bytes = None, private_key: bytes = None,
               status: str = "active", label: str = None,
               expires_at: datetime = None) -> Key:
    k = Key(
        algorithm_id=algorithm_id, key_data=key_data, iv=iv,
        public_key=public_key, private_key=private_key,
        key_size_bits=key_size_bits, status=status,
        label=label, expires_at=expires_at
    )
    session.add(k)
    session.commit()
    session.refresh(k)
    return k


def get_key_by_id(session: Session, key_id: int) -> Optional[Key]:
    return session.query(Key).filter(Key.id == key_id).first()


def get_keys_by_algorithm(session: Session, algorithm_id: int) -> list[Key]:
    return session.query(Key).filter(Key.algorithm_id == algorithm_id).all()


def get_all_keys(session: Session) -> list[Key]:
    return session.query(Key).all()


def update_key(session: Session, key_id: int, **kwargs) -> Optional[Key]:
    k = get_key_by_id(session, key_id)
    if not k:
        return None
    for key, value in kwargs.items():
        if hasattr(k, key):
            setattr(k, key, value)
    session.commit()
    session.refresh(k)
    return k


def revoke_key(session: Session, key_id: int) -> Optional[Key]:
    return update_key(session, key_id, status="revoked")


def delete_key(session: Session, key_id: int) -> bool:
    k = get_key_by_id(session, key_id)
    if not k:
        return False
    session.delete(k)
    session.commit()
    return True


def create_file(session: Session, original_name: str, original_path: str,
                file_size: int, file_hash: str = None,
                status: str = "original") -> File:
    f = File(
        original_name=original_name, original_path=original_path,
        file_size=file_size, file_hash=file_hash, status=status
    )
    session.add(f)
    session.commit()
    session.refresh(f)
    return f


def get_file_by_id(session: Session, file_id: int) -> Optional[File]:
    return session.query(File).filter(File.id == file_id).first()


def get_all_files(session: Session) -> list[File]:
    return session.query(File).all()


def get_files_by_status(session: Session, status: str) -> list[File]:
    return session.query(File).filter(File.status == status).all()


def update_file(session: Session, file_id: int, **kwargs) -> Optional[File]:
    f = get_file_by_id(session, file_id)
    if not f:
        return None
    for key, value in kwargs.items():
        if hasattr(f, key):
            setattr(f, key, value)
    f.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(f)
    return f


def delete_file(session: Session, file_id: int) -> bool:
    f = get_file_by_id(session, file_id)
    if not f:
        return False
    session.delete(f)
    session.commit()
    return True


def create_crypto_operation(session: Session, file_id: int, algorithm_id: int,
                            framework_id: int, key_id: int,
                            operation_type: str, output_path: str = None,
                            status: str = "pending") -> CryptoOperation:
    op = CryptoOperation(
        file_id=file_id, algorithm_id=algorithm_id,
        framework_id=framework_id, key_id=key_id,
        operation_type=operation_type, output_path=output_path,
        status=status
    )
    session.add(op)
    session.commit()
    session.refresh(op)
    return op


def get_operation_by_id(session: Session, op_id: int) -> Optional[CryptoOperation]:
    return session.query(CryptoOperation).filter(CryptoOperation.id == op_id).first()


def get_all_operations(session: Session) -> list[CryptoOperation]:
    return session.query(CryptoOperation).all()


def get_operations_by_file(session: Session, file_id: int) -> list[CryptoOperation]:
    return session.query(CryptoOperation).filter(CryptoOperation.file_id == file_id).all()


def update_operation(session: Session, op_id: int, **kwargs) -> Optional[CryptoOperation]:
    op = get_operation_by_id(session, op_id)
    if not op:
        return None
    for key, value in kwargs.items():
        if hasattr(op, key):
            setattr(op, key, value)
    session.commit()
    session.refresh(op)
    return op


def delete_operation(session: Session, op_id: int) -> bool:
    op = get_operation_by_id(session, op_id)
    if not op:
        return False
    session.delete(op)
    session.commit()
    return True


def create_performance(session: Session, operation_id: int,
                       execution_time_ms: float, memory_usage_kb: float = None,
                       cpu_usage_percent: float = None,
                       input_size_bytes: int = None, output_size_bytes: int = None,
                       throughput_mbps: float = None) -> Performance:
    p = Performance(
        operation_id=operation_id, execution_time_ms=execution_time_ms,
        memory_usage_kb=memory_usage_kb, cpu_usage_percent=cpu_usage_percent,
        input_size_bytes=input_size_bytes, output_size_bytes=output_size_bytes,
        throughput_mbps=throughput_mbps
    )
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


def get_performance_by_id(session: Session, perf_id: int) -> Optional[Performance]:
    return session.query(Performance).filter(Performance.id == perf_id).first()


def get_performance_by_operation(session: Session, operation_id: int) -> Optional[Performance]:
    return session.query(Performance).filter(Performance.operation_id == operation_id).first()


def get_all_performances(session: Session) -> list[Performance]:
    return session.query(Performance).all()


def update_performance(session: Session, perf_id: int, **kwargs) -> Optional[Performance]:
    p = get_performance_by_id(session, perf_id)
    if not p:
        return None
    for key, value in kwargs.items():
        if hasattr(p, key):
            setattr(p, key, value)
    session.commit()
    session.refresh(p)
    return p


def delete_performance(session: Session, perf_id: int) -> bool:
    p = get_performance_by_id(session, perf_id)
    if not p:
        return False
    session.delete(p)
    session.commit()
    return True