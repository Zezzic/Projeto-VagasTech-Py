from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017")
banco = cliente["vagas_remotas"]
colecao = banco["vagas"]
