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


class Reply(Base):
    __tablename__ = "reply"
    id = Column(String, primary_key=True)
    ref_id = Column(String)
    created_at = Column(BigInteger)
    kind = Column(BigInteger)
    relay_url = Column(String)
    marker = Column(String)


class Mention(Base):
    __tablename__ = "mention"
    id = Column(String, primary_key=True)
    ref_id = Column(String)
    created_at = Column(BigInteger)
    kind = Column(BigInteger)
    relay_url = Column(String)
    petname = Column(String)


class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True)
    name = Column(String)  # display_name/name/displayName
    about = Column(String)
    website = Column(String)
    nip05 = Column(String)
    lud16 = Column(String)
    picture = Column(String)
    banner = Column(String)
    created_at = Column(BigInteger)
    # bech32
    # relays = Column(JSONB)


# ['e',
#   '02648a5c060dd1afc4c5fbf5ec7f3e44139b497698dd0de8c02f3bd748af290e',
#   '',
#   'root']
# class Tags(Base):
#     id = Column(String)  # composite key with tag, value
#     tag = Column(String)
#     value = Column(String)
#     relay_url = Column(String)
#     item_4 = Column(String)


# can have duplicate tags
# [
#     [
#         "e",
#         "02648a5c060dd1afc4c5fbf5ec7f3e44139b497698dd0de8c02f3bd748af290e",
#         "",
#         "root",
#     ],
#     [
#         "e",
#         "1fcc26a8e225b05da651b5c99ce83f8be90740a47406b6e1e6b37353867d0cde",
#         "wss://nos.lol/",
#         "reply",
#     ],
#     ["p", "5c508c34f58866ec7341aaf10cc1af52e9232bb9f859c8103ca5ecf2aa93bf78"],
#     ["p", "e82b70606c437b8338c49d5dcb950c650f79a967e9db7d47283c89f8d6491d8d"],
#     ["p", "1bc70a0148b3f316da33fe3c89f23e3e71ac4ff998027ec712b905cd24f6a411"],
# ]

# 3rd field is not always relay_url
# [['relays',
#   'wss://pablof7z.nostr1.com',
#   'wss://purplepag.es',
#   'wss://nos.lol',
#   'wss://relay.f7z.io',
#   'wss://relay.damus.io',
#   'wss://relay.snort.social',
#   'wss://relay.noswhere.com',
#   'wss://relay.nostr.band/',
#   'wss://nostr.mom'],
#  ['p', '73c6bb92440a9344279f7a36aa3de1710c9198b1e9e8a394cd13e0dd5c994c63'],
#  ['param', 't', 'philosophy'],
#  ['param', 't', 'seneca'],
#  ['param', 't', 'stoicism']]


# class Relays(Base):
#     id = Column(String, primary_key=True)
#     url = Column(String)
