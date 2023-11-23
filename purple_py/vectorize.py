from dotenv import load_dotenv
import os
import weaviate


load_dotenv()


def get_user_class():
    user_class = {
        "class": "User",
        "description": "Users",
        "vectorIndexType": "hnsw",
        "vectorIndexConfig": {
            "skip": True,  # don't need to vector index users
        },
        "properties": [
            {"name": "pubkey", "dataType": ["text"]},
            {"name": "name", "dataType": ["text"]},
            {"name": "hasCreated", "dataType": ["Event"]},  # cross-reference
        ],
        "vectorizer": None,
    }
    return user_class


def get_event_class():
    event_class = {
        "class": "Event",
        "description": "Events",
        "vectorIndexType": "hnsw",
        "vectorIndexConfig": {
            "distance": "cosine",
        },
        "invertedIndexConfig": {
            "stopwords": {
                "preset": "en",
            }
        },
        "properties": [
            {
                "name": "event_id",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "created_at",
                "dataType": ["int"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "pubkey",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "kind",
                "dataType": ["int"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "content",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": False,
                        "vectorizePropertyName": False,
                    }
                },
            },
            # tags
        ],
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "vectorizeClassName": False,
            }
        },
    }
    return event_class


def create_classes():
    weaviate_client_url = os.getenv("WEAVIATE_CLIENT_URL")
    client = weaviate.Client(url=weaviate_client_url)

    user_class = get_user_class()
    # client.schema.delete_class('User')
    client.schema.create_class(user_class)

    event_class = get_event_class()
    # client.schema.delete_class('Event')
    client.schema.create_class(event_class)
