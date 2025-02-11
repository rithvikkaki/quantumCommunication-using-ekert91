# encryption.py
def generate_shared_key(result, aliceMeasurementChoices, bobMeasurementChoices, circuits, numberOfSinglets):
    key_alice = []
    key_bob = []
    
    for i in range(numberOfSinglets):
        # Alice's and Bob's bases need to match for a key to be generated
        if aliceMeasurementChoices[i] == bobMeasurementChoices[i]:
            res = list(result.get_counts(circuits[i]).keys())[0]
            # Extract Alice's and Bob's measurement outcomes for key generation
            key_alice.append(int(res[-4]))  # Alice's outcome is stored in cr[0]
            key_bob.append(int(res[-3]))    # Bob's outcome is stored in cr[1]
    
    # Return keys after matching their lengths
    return key_alice[:len(key_bob)], key_bob

# Function to XOR encrypt healthcare data using the shared key
def encrypt_healthcare_data(data, key):
    # Convert data to binary
    binary_data = ''.join(format(ord(char), '08b') for char in data)
    encrypted_data = ''.join(str(int(binary_data[i]) ^ key[i % len(key)]) for i in range(len(binary_data)))
    return encrypted_data

# Function to XOR decrypt healthcare data using the shared key
def decrypt_healthcare_data(encrypted_data, key):
    decrypted_binary = ''.join(str(int(encrypted_data[i]) ^ key[i % len(key)]) for i in range(len(encrypted_data)))
    decrypted_data = ''.join(chr(int(decrypted_binary[i:i+8], 2)) for i in range(0, len(decrypted_binary), 8))
    return decrypted_data
