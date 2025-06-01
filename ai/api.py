from urllib.request import Request

import numpy as np
from scipy.spatial.distance import cdist
from ai.config import *
from database.db import DB


class AI:
    def makeQuery(id, query):
        query += DB.GetChoosenLang(id)["makeQuery"]
        return query

    def makeEmbeddingQuery(id, chunk, query):
        result = DB.GetChoosenLang(id)["askAnswer"]
        result += chunk
        result += DB.GetChoosenLang(id)["askGet"]
        result += query
        result += DB.GetChoosenLang(id)["makeQuery"]
        return result

    def makeTask(id, query, type):
        if type == 0:
            result = DB.GetChoosenLang(id)["practiceTest"]
            result += query
            result += DB.GetChoosenLang(id)["practiceAnswer"]
            result += DB.GetChoosenLang(id)["makeQuery"]
            return result
        else:
            result = DB.GetChoosenLang(id)["practiceQuestion"]
            result += query
            result += DB.GetChoosenLang(id)["practiceAnswer"]
            result += DB.GetChoosenLang(id)["makeQuery"]
            return result

    def makeEmbeddingTask(id, chunk, type):
        if type == 0:
            result = DB.GetChoosenLang(id)["practiceEmbeddingTest"]
            result += chunk
            result += DB.GetChoosenLang(id)["practiceAnswer"]
            result += DB.GetChoosenLang(id)["makeQuery"]
            return result
        else:
            result = DB.GetChoosenLang(id)["practiceEmbeddingQuestion"]
            result += chunk
            result += DB.GetChoosenLang(id)["practiceAnswer"]
            result += DB.GetChoosenLang(id)["makeQuery"]
            return result

    def Request(query):
        model = API_SDK.models.completions("yandexgpt-lite", model_version="rc")
        model = model.configure(temperature=API_TEMPERATURE)
        result = model.run(query)

        return result[0].text

    def EmbeddingsRequest(chunks, query):

        if len(chunks) == 0:
            return Request(query)
        else:
            query_model = API_SDK.models.text_embeddings("query")
            query_embedding = query_model.run(query)

            doc_model = API_SDK.models.text_embeddings("doc")
            doc_embeddings = [doc_model.run(text) for text in chunks]

            query_embedding = np.array(query_embedding)

            dist = cdist([query_embedding], doc_embeddings, metric="cosine")
            sim = 1 - dist
            result = chunks[np.argmax(sim)]
            return result

# querr = AI.makeTask("948641423", "Computer Science", 0)
# print( AI.Request(querr) )