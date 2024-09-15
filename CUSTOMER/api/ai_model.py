from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import pdfplumber
import uuid
import requests
import os
from django.conf import settings
load_dotenv()
api_key = "AIzaSyB53J7RDezS0P1thyXJpkIo68HDTS2HIAE"
def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def get_response(company_file_url, user_question):
    print(company_file_url)
    file = company_file_url.split('media/')
    file_path = os.path.join(settings.MEDIA_ROOT, file[1])

    # Print the file path for debugging
    print("Corrected File Path:", file_path)
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = pdfplumber.open(pdf_file)
        data = []
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                data.append(page_text)
                print(f"Page {i + 1}: {page_text[:200]}...")  # Print the first 200 characters for inspection
            else:
                print(f"Page {i + 1} contains no extractable text.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    content = "\n\n".join(data)
    texts = text_splitter.split_text(content)
    ids = [str(uuid.uuid4()) for _ in texts]

    embed = GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key=api_key)
    vector_store = Chroma.from_texts(texts, embed, ids=ids).as_retriever()

    prompt_template = """
      Please answer the question in as much detail as possible based on the provided context.
      Ensure to include all relevant details. If the answer is not available in the provided context,
      kindly respond with "The answer is not available in the context." Please avoid providing incorrect answers. If the question is greating then responde by greating the user too.
    \n\n
      Context:\n {context}?\n
      Question: \n{question}\n

      Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    model = ChatGoogleGenerativeAI(model='gemini-pro', api_key=api_key, temperature=.9)
    chain = load_qa_chain(model, chain_type='stuff', prompt=prompt)
    docs = vector_store.get_relevant_documents(user_question)
    responses = chain(
        {'input_documents': docs, "question": user_question},
        return_only_outputs=True
    )
    print(responses['output_text'])
    return responses['output_text']
