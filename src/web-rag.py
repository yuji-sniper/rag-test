from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
import requests
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
def most_similar_documents(question, documents, count=2):
    document_vectors = [vectorize(doc) for doc in documents]
    question_vector = vectorize(question)
    
    similarities = cosine_similarity([question_vector], document_vectors)[0]
    most_similar_indices = similarities.argsort()[-count:][::-1]
    
    return [documents[i] for i in most_similar_indices]


# テキストを取得する関数
def scrape_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text_nodes = soup.find_all("div")
    joined_text = ""
    for t in text_nodes:
        joined_text += t.text.replace("\n", "").replace("\t", "")
    return joined_text


# テキストをチャンク分割する関数
def chunk_text(joined_text):
    chunk_size = 400
    overlap_size = 50
    chunks = []
    for i in range(0, len(joined_text), chunk_size - overlap_size):
        chunks.append(joined_text[i:i+chunk_size])
    return chunks


# プロンプトを生成する関数
def generate_prompt(question, chunked_text):
    infos = most_similar_documents(question, chunked_text)
    info_text = "\n".join(infos)
    prompt = f'''
        以下の情報を元に、ユーザーの質問に回答してください。
        [ユーザーの質問]
        {question}

        [情報]
        {info_text}
    '''
    print(prompt)
    return prompt


# プロンプトを実行
def execute_prompt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
    )
    print(response.choices[0].message.content)


# 実行関数
def handle():
    url = "https://toukei-lab.com/achademy/?page_id=1619"
    # question = "プレミアムプランの料金は？"
    question = "オーダーメイドプランの料金は？"
    
    joined_text = scrape_article(url)
    chunked_text = chunk_text(joined_text)
    prompt = generate_prompt(question, chunked_text)
    execute_prompt(prompt)


handle()
