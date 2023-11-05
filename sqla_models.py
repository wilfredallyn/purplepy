from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()


class Event(Base):
    __tablename__ = "event"
    id = Column(String, primary_key=True)
    created_at = Column(BigInteger)
    kind = Column(BigInteger)
    tags = Column(JSONB)
    pubkey = Column(String)
    content = Column(String)
    sig = Column(String)


class User(Base):
    __tablename__ = "user"
    id = Column(String)
    created_at = Column(BigInteger)
    pubkey = Column(String, primary_key=True)
    tags = Column(JSONB)
    name = Column(String)
    about = Column(String)
    website = Column(String)
    nip05 = Column(String)
    lud16 = Column(String)
    picture = Column(String)
    banner = Column(String)


class Follow(Base):
    __tablename__ = "follow"
    pubkey = Column(String, nullable=False, primary_key=True)
    p = Column(String, nullable=False, primary_key=True)
    created_at = Column(BigInteger)


class Reply(Base):
    __tablename__ = "reply"
    id = Column(String, primary_key=True)
    pubkey = Column(String)
    ref_id = Column(String)
    created_at = Column(BigInteger)
    kind = Column(BigInteger)
    relay_url = Column(String)
    marker = Column(String)


class Mention(Base):
    __tablename__ = "mention"
    id = Column(String, primary_key=True)
    pubkey = Column(String)
    ref_pubkey = Column(String)
    created_at = Column(BigInteger)
    kind = Column(BigInteger)
    relay_url = Column(String)
    petname = Column(String)


class Reaction(Base):
    __tablename__ = "reaction"
    id = Column(String, primary_key=True)
    pubkey = Column(String)
    created_at = Column(BigInteger)
    content = Column(String)
    e = Column(String)
    p = Column(String)
