import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000/api/search"

st.set_page_config(page_title="Semantic vs Keyword Search", layout="wide")

st.title("Semantic Search vs Keyword Search ")

query = st.text_input("Enter your search query:")

if st.button("Search") and query:

    col1, col2 = st.columns(2)

    # -------- KEYWORD SEARCH --------
    with col1:
        st.subheader("Keyword Search")

        try:
            keyword_response = requests.get(
                f"{BACKEND_URL}/keyword/",
                params={"q": query}
            )
            
            if keyword_response.status_code == 200:
                data = keyword_response.json()
                st.success(f"Response Time: {data['response_time']} sec")
                st.caption(f"Results Found: {len(data['results'])}")

                if data["results"]:
                    for item in data["results"]:
                        st.markdown(f"**{item['title']}**")
                        st.write(item["content"])
                        st.divider()
                else:
                    st.warning("No results found.")
            else:
                st.error("Keyword API error.")

        except Exception as e:
            st.error(f"Error: {e}")

    # -------- SEMANTIC SEARCH --------
    with col2:
        st.subheader("Semantic Search")

        try:
            semantic_response = requests.post(
                f"{BACKEND_URL}/semantic/",
                json={"query": query}
            )

            if semantic_response.status_code == 200:
                data = semantic_response.json()

                if data.get("cached"):
                    st.success(" Served from Redis Cache")
                    
                st.success(f"Response Time: {data['response_time']} sec")
                st.caption(f"Results Found: {len(data['results'])}")
                

                if data["results"]:
                    for item in data["results"]:
                        st.markdown(f"**{item['title']}**")
                        st.write(item["content"])
                        st.write(f"Similarity: {item['similarity']}")
                        st.divider()
                else:
                    st.warning("No results found.")
            else:
                st.error("Semantic API error.")

        except Exception as e:
            st.error(f"Error: {e}")