import pickle
import base64

def load_data(serialized_data, trusted_keys=None):
    try:
        # Deserialize safely by verifying the data comes from a trusted source
        data = pickle.loads(serialized_data)
        if trusted_keys and not all(key in data for key in trusted_keys):
            raise ValueError("Untrusted data structure")
        print("Deserialized data:", data)
    except Exception as e:
        print("Failed to deserialize data:", e)

# Example usage
trusted_serialized_data = base64.b64encode(pickle.dumps({"key1": "value1", "key2": "value2"}))
load_data(base64.b64decode(trusted_serialized_data))
