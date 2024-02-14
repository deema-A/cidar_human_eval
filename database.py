from pymongo import MongoClient

uri = "mongodb+srv://cluster0.tzvxqk3.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile="X509-cert-2433626168795922546.pem")

db = client['testDB']
collection = db['testCol']


def save_response(response_data):
    """Saves a response to the MongoDB collection."""

    try:
        # Insert the response data into the collection
        collection.insert_one(response_data)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(0)

def read_responses(filter_query=None):
    """Reads responses from the MongoDB collection based on an optional filter."""
    try:
        if filter_query is None:
            filter_query = {}  # An empty query will return all documents
        responses = collection.find(filter_query)
        return list(responses)  # Convert cursor to list
    except Exception as e:
        print(f"An error occurred: {e}")
        return []