from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float,
    DateTime, ForeignKey, LargeBinary, BigInteger
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Algorithm(Base):
    __tablename__ = "algorithms"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(50), nullable=False, unique=True)
    type        = Column(String(20), nullable=False)
    key_size    = Column(Integer, nullable=False)
    block_size  = Column(Integer, nullable=True)
    mode        = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)

    keys        = relationship("Key",             back_populates="algorithm", cascade="all, delete-orphan")
    operations  = relationship("CryptoOperation", back_populates="algorithm", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Algorithm(id={self.id}, name='{self.name}', type='{self.type}', key_size={self.key_size})>"


class Framework(Base):
    __tablename__ = "frameworks"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(100), nullable=False, unique=True)
    version     = Column(String(30), nullable=True)
    language    = Column(String(30), nullable=True)
    description = Column(Text, nullable=True)

    operations  = relationship("CryptoOperation", back_populates="framework", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Framework(id={self.id}, name='{self.name}', version='{self.version}')>"


class Key(Base):
    __tablename__ = "keys"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    algorithm_id    = Column(Integer, ForeignKey("algorithms.id"), nullable=False)
    key_data        = Column(LargeBinary, nullable=False)
    iv              = Column(LargeBinary, nullable=True)
    public_key      = Column(LargeBinary, nullable=True)
    private_key     = Column(LargeBinary, nullable=True)
    key_size_bits   = Column(Integer, nullable=False)
    status          = Column(String(20), nullable=False, default="active")
    created_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at      = Column(DateTime, nullable=True)
    label           = Column(String(100), nullable=True)

    algorithm       = relationship("Algorithm", back_populates="keys")
    operations      = relationship("CryptoOperation", back_populates="key", cascade="all, delete-orphan")

    def __repr__(self):
        return (f"<Key(id={self.id}, algorithm='{self.algorithm_id}', "
                f"size={self.key_size_bits}, status='{self.status}')>")


class File(Base):
    __tablename__ = "files"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    original_name   = Column(String(255), nullable=False)
    original_path   = Column(Text, nullable=False)
    encrypted_path  = Column(Text, nullable=True)
    decrypted_path  = Column(Text, nullable=True)
    file_size       = Column(BigInteger, nullable=False)
    file_hash       = Column(String(128), nullable=True)
    status          = Column(String(20), nullable=False, default="original")
    created_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                             onupdate=lambda: datetime.now(timezone.utc))

    operations      = relationship("CryptoOperation", back_populates="file", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<File(id={self.id}, name='{self.original_name}', status='{self.status}')>"


class CryptoOperation(Base):
    __tablename__ = "crypto_operations"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    file_id         = Column(Integer, ForeignKey("files.id"),       nullable=False)
    algorithm_id    = Column(Integer, ForeignKey("algorithms.id"),  nullable=False)
    framework_id    = Column(Integer, ForeignKey("frameworks.id"),  nullable=False)
    key_id          = Column(Integer, ForeignKey("keys.id"),        nullable=False)
    operation_type  = Column(String(20), nullable=False)
    status          = Column(String(20), nullable=False, default="pending")
    output_path     = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    file            = relationship("File",      back_populates="operations")
    algorithm       = relationship("Algorithm", back_populates="operations")
    framework       = relationship("Framework", back_populates="operations")
    key             = relationship("Key",       back_populates="operations")
    performance     = relationship("Performance", back_populates="operation",
                                   uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return (f"<CryptoOperation(id={self.id}, type='{self.operation_type}', "
                f"status='{self.status}')>")


class Performance(Base):
    __tablename__ = "performances"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    operation_id        = Column(Integer, ForeignKey("crypto_operations.id"), nullable=False, unique=True)
    execution_time_ms   = Column(Float, nullable=False)
    memory_usage_kb     = Column(Float, nullable=True)
    cpu_usage_percent   = Column(Float, nullable=True)
    input_size_bytes    = Column(BigInteger, nullable=True)
    output_size_bytes   = Column(BigInteger, nullable=True)
    throughput_mbps     = Column(Float, nullable=True)
    created_at          = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    operation           = relationship("CryptoOperation", back_populates="performance")

    def __repr__(self):
        return (f"<Performance(id={self.id}, time={self.execution_time_ms}ms, "
                f"memory={self.memory_usage_kb}KB)>")