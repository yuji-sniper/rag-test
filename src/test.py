from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()


client = OpenAI()


# テキストをベクトル化する関数
def vectorize(text):
    res = client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    
    return res.data[0].embedding


# 最も類似した文書を返す関数
def most_similar_document(question, documents):
    document_vectors = [vectorize(doc) for doc in documents]
    question_vector = vectorize(question)

    max_similarity = 0
    most_similar_index = 0

    for i, vector in enumerate(document_vectors):
        similarity = cosine_similarity([question_vector], [vector])[0][0]
        print(f"Document {i}: {similarity}")
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_index = i

    return documents[most_similar_index]


# 実行関数
def handle():
    question = "2023年の第一事業部の売り上げはどのくらい？"

    documents = [
        "2023年の上期売上200億円、下期売上300億円",
        "2023年第一事業部売上300億円、第二事業部売上150億円、第三事業部売上100億円",
        "2024年は第一事業部の売上400億円を目指す",
    ]

    info = most_similar_document(question, documents)

    prompt = f'''
        以下の情報を元に、ユーザーの質問に回答してください。
        [ユーザーの質問]
        {question}

        [情報]
        {info}
    '''

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
    )
    
    print(response.choices[0].message.content)


handle()
