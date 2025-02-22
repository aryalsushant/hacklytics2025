# backend/database.py
import os
import atexit
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mongo_client = None

def get_database():
    """Connect to MongoDB and return the database object."""
    global mongo_client
    try:
        connection_string = os.getenv('MONGODB_URI')
        mongo_client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,
            tlsAllowInvalidCertificates=True
        )
        # Test the connection
        mongo_client.admin.command('ping')
        db = mongo_client[os.getenv('DB_NAME', 'drug_interactions')]
        print("✅ Connected to MongoDB successfully")
        atexit.register(cleanup_mongo_client)
        return db
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        if mongo_client:
            mongo_client.close()
        return None

def cleanup_mongo_client():
    """Close the MongoDB connection when the application exits."""
    global mongo_client
    if mongo_client:
        print("Closing MongoDB connection...")
        mongo_client.close()

def populate_mongodb(db):
    """Populate MongoDB with CSV data if the collection is empty."""
    if db is None:
        print("❌ No database connection available")
        return

    collection_name = os.getenv('COLLECTION_NAME', 'drug_interaction')
    interactions_collection = db[collection_name]

    try:
        doc_count = interactions_collection.count_documents({})
        print(f"Current documents in MongoDB: {doc_count}")
        if doc_count == 0:
            print("💾 Populating MongoDB with CSV data...")
            import pandas as pd
            try:
                df = pd.read_csv('dataset/twosides_aggregated.csv')
                print(f"✅ CSV loaded successfully with {len(df)} rows")
                records = df.to_dict('records')
                print("Converting DataFrame to records...")
                result = interactions_collection.insert_many(records)
                print(f"✅ Inserted {len(result.inserted_ids)} records into MongoDB")
                new_count = interactions_collection.count_documents({})
                print(f"New document count in MongoDB: {new_count}")
            except FileNotFoundError:
                print("❌ Error: CSV file not found at 'dataset/twosides_aggregated.csv'")
            except Exception as e:
                print(f"❌ Error during CSV processing: {e}")
        else:
            print(f"✅ MongoDB collection already populated with {doc_count} documents")
    except Exception as e:
        print(f"❌ Error in populate_mongodb: {e}")

def create_indexes(db):
    """Create indexes for better query performance."""
    if db is None:
        print("❌ No database connection available")
        return

    collection_name = os.getenv('COLLECTION_NAME', 'drug_interaction')
    interactions_collection = db[collection_name]

    try:
        print("Creating indexes...")
        interactions_collection.create_index([("X1", 1), ("X2", 1)], name="drug_pair_index")
        interactions_collection.create_index([("X1", 1)], name="drug1_index")
        interactions_collection.create_index([("X2", 1)], name="drug2_index")
        interactions_collection.create_index([("Top_5_Side_Effects", 1)], name="side_effects_index")
        print("✅ Indexes created successfully")
        indexes = interactions_collection.list_indexes()
        print("\nCurrent indexes:")
        for index in indexes:
            print(f"- {index['name']}: {index['key']}")
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
