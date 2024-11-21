import pickle

def load_data(serialized_data):
    # Vulnerable: Directly deserializing untrusted data
    data = pickle.loads(serialized_data)
    print("Deserialized data:", data)

# Example usage
user_input = input("Enter serialized data: ")
load_data(user_input.encode())
