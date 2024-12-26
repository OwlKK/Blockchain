import hashlib
data = "Hello, blockchain!"
hash_value = hashlib.sha256(data.encode()).hexdigest()
print("Data:", data)
print("SHA-256 Hash:", hash_value)