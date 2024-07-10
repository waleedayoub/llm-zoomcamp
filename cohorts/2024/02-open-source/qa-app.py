import streamlit as st
from openai import OpenAI
from elasticsearch import Elasticsearch

# Assume a few things are already complete at this point:
# 1. We've downloaded all the documents and put them into a list called documents
# 2. We've indexed the documents into Elasticsearch in an index called course-questions

# Set up the LLM client
client = OpenAI(
    base_url="http://192.168.50.49:11434/v1/",
    api_key="ollama",
)

# Set up the Elastic client
es_client = Elasticsearch("http://192.168.50.49:9200")


## Define the search function
def elastic_search(query, index_name="course-questions"):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields",
                    }
                },
                "filter": {"term": {"course": "data-engineering-zoomcamp"}},
            }
        },
    }

    response = es_client.search(index=index_name, body=search_query)

    result_docs = []

    for hit in response["hits"]["hits"]:
        result_docs.append(hit["_source"])

    return result_docs


## Create the build prompt function:


def build_prompt(query, search_results):
    prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

    context = ""

    for doc in search_results:
        context = (
            context
            + f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}\n\n"
        )

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


def llm(prompt):
    response = client.chat.completions.create(
        model="phi3", messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def rag(query):
    search_results = elastic_search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer


def main():
    st.title("QA App")
    input_text = st.text_input("Enter your question:")
    if st.button("Ask"):
        with st.spinner("Running RAG function..."):
            output = rag(input_text)
            st.success(output)


if __name__ == "__main__":
    main()
