# Customer Service Chat Bot

This project implements a chatbot for handling customer service inquiries. It leverages modern technologies such as natural language processing and a Docker-based deployment to create a responsive and scalable service.

## Overview

The chatbot system is designed to automate responses to common customer inquiries, reducing the need for human customer service representatives and speeding up response times. The architecture includes a web-based interface, a backend processing brain, a logging system, and a database for storing interaction histories.

## Project Structure

- `app.py`: The main entry point for the chatbot application. It handles web requests and integrates all components of the project.
- `brain.py`: Contains the logic for processing user inputs and generating responses using NLP models.
- `database.py`: Manages interactions with the SQLite database, `isp_database.db`, which stores chat histories and user interactions.
- `logger.py`: Provides logging functionality to help in debugging and tracking the operations of the chatbot.
- `docker-compose.yaml` & `DockerFile`: Define the Docker environment for the project, ensuring consistent setups across different machines and deployments.
- `nginx.conf`: Configuration file for the nginx server, which acts as a reverse proxy, handling incoming HTTP requests efficiently.
- `requirements.txt`: Lists all Python libraries required for the project, ensuring easy setup on any development or production environment.
- `isp_database.db`: A SQLite database file that the application uses to store relevant data.

## Key Features

- **Natural Language Understanding**: Utilizes libraries like `transformers` and `langchain` to understand and process user queries.
- **Efficient Searching**: Integrates `faiss-cpu` for fast retrieval of relevant information from the database.
- **PDF Processing**: Capable of processing PDF documents to extract useful information using the `pypdf` library.
- **Logging and Monitoring**: Tracks system behavior and logs important events for troubleshooting and analysis.
- **Web Interface**: Uses `streamlit` for creating a user-friendly web interface that allows users to interact with the chatbot.
- **API Integration**: Incorporates `requests` to connect with external APIs for extended functionalities.

## Installation

1. **Clone the Repository**
  ```
  git clone [repository-url]
  cd [repository-name]
  ```
2. **Set Up the Environment**
- Ensure Docker is installed on your system.
- Build the Docker containers:
  ```
  docker-compose up --build
  ```

3. **Install Python Dependencies**
- Recommended to use a virtual environment:
  ```
  python -m venv venv
  source venv/bin/activate  # On Windows use `venv\Scripts\activate`
  pip install -r requirements.txt
  ```

4. **Running the Application**
- Once the Docker containers are up and running, access the web interface via `http://localhost:8501` or as configured in your Docker and nginx setup.

## Usage

After starting the service, users can interact with the chatbot through the provided web interface. The chatbot will handle queries as configured and provide responses based on its training and the information available in the database.

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your features or fixes.

## License

Specify your project's license here, detailing how others can use it and any restrictions imposed.
   
