from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Select your database (replace 'your_database' with the actual database name)
db = client['testDB']

mycol = db["customers"]

mydict = { "name": "John", "address": "Highway 37" }

x = mycol.insert_one(mydict)

import gridfs

# Create a GridFS object for the selected database
fs = gridfs.GridFS(db)

# Define the file path you want to upload
file_path = '../test_doctor.wav'

# Open the file and upload it
with open(file_path, 'rb') as file_data:
    file_id = fs.put(file_data, filename='file.wav', description='Sample wav file')

print(f"File uploaded with file_id: {file_id}")

# Fetch the file using its filename
file_data = fs.find_one({'filename': 'file.wav'})

if file_data:
    # Save the file to disk
    with open('downloaded_file.wav', 'wb') as output_file:
        output_file.write(file_data.read())
    print("File downloaded successfully")
else:
    print("File not found")

# Fetch the file metadata
file_data = fs.find_one({'filename': 'file.wav'})

if file_data:
    print(f"Filename: {file_data.filename}")
    print(f"Upload Date: {file_data.upload_date}")
    print(f"Description: {file_data.description}")
    print(f"File Size: {file_data.length / 1024} KB")

# Delete the file by file_id
fs.delete(file_id)
print(f"File with file_id: {file_id} has been deleted")

# Upload a file with metadata
with open(file_path, 'rb') as file_data:
    file_id = fs.put(file_data, filename='file.txt', description='Sample file with tags', 
                     tags=['example', 'wav', 'test'])

print(f"File uploaded with metadata, file_id: {file_id}")

# Find a file based on metadata (e.g., description)
file_data = fs.find_one({'description': 'Sample file with tags'})

if file_data:
    print(f"Found file with ID: {file_data._id} and filename: {file_data.filename}")
else:
    print("No file found")

file_data = fs.find_one({'tags': {'$in':['wav']}})

if file_data:
    print(f"Found file with ID: {file_data._id} and filename: {file_data.filename}")
else:
    print("No file found")

