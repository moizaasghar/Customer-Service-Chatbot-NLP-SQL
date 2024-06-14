import streamlit as st
from brain import get_index_for_pdf, search_index
import requests
import re
from database import create_connection, execute_query
from logger import log_message

API_URL = "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"
headers = {"Authorization": "xxx"}
	
def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
st.title("RAG enhanced Chatbot")
# create_database() # Create the database if it doesn't exist

database = "isp_database.db"
conn = create_connection(database)

# Upload PDF files using Streamlit's file uploader
pdf_files = st.file_uploader("Upload PDF files:", type="pdf", accept_multiple_files=True, label_visibility='collapsed')


# Cached function to create a vectordb for the provided PDF files
@st.cache_resource()
def create_vectordb(files, filenames):
    with st.spinner("Creating vector database..."):
        documents, vectordb = get_index_for_pdf([file.getvalue() for file in files], filenames)
        print(vectordb)  
    return documents, vectordb


# If PDF files are uploaded, create the vectordb and store it in the session state
if pdf_files:
    pdf_file_names = [file.name for file in pdf_files]
    documents, vectordb = create_vectordb(pdf_files, pdf_file_names) 
    st.session_state['vectordb'] = vectordb
    st.session_state['documents'] = documents
# Initialize prompt
prompt = st.session_state.get("prompt", [{"role": "system", "content": "none"}])

# Display previous chat messages
for idx, message in enumerate(prompt):
    if message["role"] == "user":
        st.text_area(f"User {idx}", value=message["content"], height=75, disabled=True)
    else:
        st.text_area(f"Assistant {idx}", value=message["content"], height=75, disabled=True)

# User input for new message
user_message = st.text_input("Type your message here:", label_visibility='collapsed')

def extract_sql_query(full_response):
    match = re.search(r"```\n(.*?)\n```", full_response, re.DOTALL)
    if match:
        # Return the extracted SQL query
        return match.group(1)
    else:
        # Return None or an appropriate message if no SQL is found
        return None

def generate_sql_query(user_message):
    with st.spinner("Generating response..."):
        # Prepare the input text by combining user message and documents content
        database_schema = f"""
        CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        address TEXT NOT NULL,
        area_id INTEGER,
        FOREIGN KEY (area_id) REFERENCES areas_of_operation (area_id)
        );,
        CREATE TABLE IF NOT EXISTS packages (
        package_id INTEGER PRIMARY KEY AUTOINCREMENT,
        package_name TEXT NOT NULL,
        speed_limit TEXT NOT NULL,
        monthly_cost REAL NOT NULL
        );,
        CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        address TEXT NOT NULL,
        area_id INTEGER,
        FOREIGN KEY (area_id) REFERENCES areas_of_operation (area_id)
        );,
        CREATE TABLE IF NOT EXISTS packages (
        package_id INTEGER PRIMARY KEY AUTOINCREMENT,
        package_name TEXT NOT NULL,
        speed_limit TEXT NOT NULL,
        monthly_cost REAL NOT NULL
        );,
        CREATE TABLE IF NOT EXISTS areas_of_operation (
        area_id INTEGER PRIMARY KEY AUTOINCREMENT,
        area_name TEXT NOT NULL,
        description TEXT
        );,
        CREATE TABLE IF NOT EXISTS service_tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        issue_description TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
        );,
        CREATE TABLE IF NOT EXISTS payment_records (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL NOT NULL,
        payment_date DATE NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
        );
        """
        messages = [
            {
            "role": "system",
            "content": "You are a code chatbot who write SQL Quries from simple text. You are here to help the customers." +
            "You need to understand following database schema: " + database_schema +" and then provide SQL Qurey. Your Response should be SQL:"
            },
            {"role": "user", "content": user_message},
    ]
            # Send the prompt text to the API for response generation    	
        response = query({
                "inputs": messages,
            })
        generated_sql_query = extract_sql_query(response[0]['generated_text'][2]['content'])
        
        log_message("Database Access: ", generated_sql_query)  # Log system response
        query_result = execute_query(conn, generated_sql_query)
        
        if query_result is None:
            return "No results found."
        
        messages = [
        {
            "role": "system",
            "content": (
                "You are an intelligent chatbot tasked with converting SQL query results into easily understandable text for users. "
                "Understand the context provided by the database schema and SQL query, but your response should focus purely on interpreting the results. "
                "Do not mention the SQL query, its structure, or any database schema details in your response. Just provide a clear and concise summary of the results for a non-technical audience. "
                "Database Schema: " + database_schema + " SQL Query: " + generated_sql_query + " Query Results: " + str(query_result) + "."
            )
        },
        {"role": "user", "content": user_message},
    ]

        nl_response = query({
            "inputs": messages,
        })

        return nl_response[0]['generated_text'][2]['content']
    

def generate_response_with_context(user_message, documents):
    with st.spinner("Generating response..."):
        
        # Prepare document text
        document_text = " ".join(documents) if documents else ""
     
        # Prepare messages for the API
        messages = [
            {
                "role": "system",
                "content": ("You are a friendly chatbot who always has a positive attitude. You are here to help customers with their questions. "
                            "Please keep your answer brief and relevant. If the text is not applicable to the question, reply with 'Not applicable.' "
                            "You need to provide an answer based on the following content: " + document_text)
            },
            {"role": "user", "content": user_message}
        ]

        # Send the messages to the API for response generation
        response = query({
            "inputs": messages
        })

        print(response)

        # Extract the generated text from the response
        generated_text = response[0]['generated_text'][2]['content']

        return generated_text



if st.button("Send"):
    prompt.append({"role": "user", "content": user_message})
    log_message("User Message", user_message)

    # Decide whether to run SQL-related functions or general context-based response
    if "user id" in user_message.lower():
        # Generate response directly related to SQL queries
        api_response = generate_sql_query(user_message)
        log_message("System Response", api_response)  # Log system response
    else:
        # Search for the top 3 results
        results = search_index(user_message, vectordb, documents, top_k=3)
        
        # Extract content from top 3 results to provide as context
        context_documents = [doc.page_content for doc, dist in results]  # Adjusted unpacking here
        
        # Generate response using the specified API
        api_response = generate_response_with_context(user_message, context_documents)
        log_message("System Response", api_response)  # Log system response

    # Append the generated response to the prompt
    prompt.append({"role": "system", "content": api_response})
    
    st.session_state["prompt"] = prompt
    
    # Display the generated response
    st.text_area("Generated Response", value=api_response, height=75, disabled=True, key="generated_response")
