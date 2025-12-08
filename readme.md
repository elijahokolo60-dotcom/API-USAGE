Running the Application
Install dependencies:

bash
pip install -r requirements.txt
Run the server:

bash
python modal_api.py
# or with uvicorn directly:
# uvicorn modal_api:app --reload --host 0.0.0.0 --port 8000
Run the client:

bash
python api_client.py
Access the API documentation:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc