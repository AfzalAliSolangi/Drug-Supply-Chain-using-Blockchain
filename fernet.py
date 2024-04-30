from cryptography.fernet import Fernet

# Generate a secret key for encryption
SECRET_KEY = Fernet.generate_key()
cipher_suite = Fernet(SECRET_KEY)

print(SECRET_KEY)