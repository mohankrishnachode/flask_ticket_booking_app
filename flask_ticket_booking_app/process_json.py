import json

# Open the JSON file for reading and writing
f = open('data.json', 'r+')
# Load the data from the file into a Python dictionary
data = json.load(f)

# Perform operations on the data dictionary as if it were a MongoDB collection
# For example, to insert a new document:
new_document = {'name': 'John', 'age': 30}
data.append(new_document)

# After performing operations, write the updated data back to the JSON file
f.seek(0)
json.dump(data, f, indent=4)
