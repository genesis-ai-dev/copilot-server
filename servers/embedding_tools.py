from codex_tools import CodexReader
from txtai import Embeddings


class DataBase:
    def __init__(self, name: str) -> None:
        self.name = name
        self.embeddings = Embeddings(path="sentence-transformers/nli-mpnet-base-v2", content=True)
        try:
           self.embeddings.load(self.name)
        except:
           print("No embeddings to load yet")

    def upsert_codex_file(self, path: str, verse_chunk_size: int = 4):
        reader = CodexReader(verse_chunk_size=verse_chunk_size)
        results = reader.get_embed_format(path)
        self.upsert_all(results)
        
    def index_all(self, data):
        self.embeddings.index(data)

    def save(self):
       self.embeddings.save(self.name)

    def upsert(self, new_data):
       self.embeddings.upsert(new_data)
       self.save()

    def upsert_all(self, new_data: list) -> None:
        for data in new_data:
            self.embeddings.upsert(data)
        self.save()


    def search(self, query: str, limit: int = 1):
       result = self.embeddings.search(query, limit)
       return result

database = DataBase('db1')
print(database.search("dog"))
database.save()