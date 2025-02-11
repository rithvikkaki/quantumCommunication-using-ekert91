from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
import numpy as np
import random
import re
from qiskit.visualization import plot_histogram
from qiskit_aer import Aer
from encryption import generate_shared_key, encrypt_healthcare_data, decrypt_healthcare_data

with open('healthcare_data.txt', 'r') as file:
    healthcare_data = file.read()

print(f"Original Healthcare Data: {healthcare_data}")

# Creating registers
qr = QuantumRegister(2, name="qr")
cr = ClassicalRegister(4, name="cr")

# Prepare the singlet state (entangled qubits)
singlet = QuantumCircuit(qr, cr, name='singlet')
singlet.x(qr[0])
singlet.x(qr[1])
singlet.h(qr[0])
singlet.cx(qr[0], qr[1])

# Define Alice's measurement circuits for different bases
measureA1 = QuantumCircuit(qr, cr, name='measureA1')
measureA1.h(qr[0])
measureA1.measure(qr[0], cr[0])

measureA2 = QuantumCircuit(qr, cr, name='measureA2')
measureA2.s(qr[0])
measureA2.h(qr[0])
measureA2.t(qr[0])
measureA2.h(qr[0])
measureA2.measure(qr[0], cr[0])

measureA3 = QuantumCircuit(qr, cr, name='measureA3')
measureA3.measure(qr[0], cr[0])

# Define Bob's measurement circuits for different bases
measureB1 = QuantumCircuit(qr, cr, name='measureB1')
measureB1.s(qr[1])
measureB1.h(qr[1])
measureB1.t(qr[1])
measureB1.h(qr[1])
measureB1.measure(qr[1], cr[1])

measureB2 = QuantumCircuit(qr, cr, name='measureB2')
measureB2.measure(qr[1], cr[1])

measureB3 = QuantumCircuit(qr, cr, name='measureB3')
measureB3.s(qr[1])
measureB3.h(qr[1])
measureB3.tdg(qr[1])
measureB3.h(qr[1])
measureB3.measure(qr[1], cr[1])

# Create measurement choices and combine with singlet
aliceMeasurements = [measureA1, measureA2, measureA3]
bobMeasurements = [measureB1, measureB2, measureB3]

numberOfSinglets = 4000
aliceMeasurementChoices = [random.randint(1, 3) for _ in range(numberOfSinglets)]
bobMeasurementChoices = [random.randint(1, 3) for _ in range(numberOfSinglets)]

circuits = []
for i in range(numberOfSinglets):
    combined_circuit = singlet.compose(aliceMeasurements[aliceMeasurementChoices[i] - 1])
    combined_circuit = combined_circuit.compose(bobMeasurements[bobMeasurementChoices[i] - 1])
    circuits.append(combined_circuit)

backend = Aer.get_backend('qasm_simulator')
transpiled_result = transpile(circuits, backend)
job = backend.run(transpiled_result, shots=500).result()  # Increase shots from the default


# Patterns for measurement results
abPatterns = [
    re.compile('..00$'),
    re.compile('..01$'),
    re.compile('..10$'),
    re.compile('..11$')
]

# Function to calculate the CHSH correlation value
def chsh_corr(result):
    countA1B1 = [0, 0, 0, 0]
    countA1B3 = [0, 0, 0, 0]
    countA3B1 = [0, 0, 0, 0]
    countA3B3 = [0, 0, 0, 0]

    for i in range(numberOfSinglets):
        res = list(result.get_counts(circuits[i]).keys())[0]
        if (aliceMeasurementChoices[i] == 1 and bobMeasurementChoices[i] == 1):
            for j in range(4):
                if abPatterns[j].search(res):
                    countA1B1[j] += 1

        if (aliceMeasurementChoices[i] == 1 and bobMeasurementChoices[i] == 3):
            for j in range(4):
                if abPatterns[j].search(res):
                    countA1B3[j] += 1

        if (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 1):
            for j in range(4):
                if abPatterns[j].search(res):
                    countA3B1[j] += 1

        if (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 3):
            for j in range(4):
                if abPatterns[j].search(res):
                    countA3B3[j] += 1

    total11 = sum(countA1B1)
    total13 = sum(countA1B3)
    total31 = sum(countA3B1)
    total33 = sum(countA3B3)

    # Expectation values calculation (correcting the sign convention and expectation formula)
    expect11 = (countA1B1[0] - countA1B1[1] - countA1B1[2] + countA1B1[3]) / total11
    expect13 = (countA1B3[0] - countA1B3[1] - countA1B3[2] + countA1B3[3]) / total13
    expect31 = (countA3B1[0] - countA3B1[1] - countA3B1[2] + countA3B1[3]) / total31
    expect33 = (countA3B3[0] - countA3B3[1] - countA3B3[2] + countA3B3[3]) / total33

    print(f'E(a1, b1) = {expect11}')
    print(f'E(a1, b3) = {expect13}')
    print(f'E(a3, b1) = {expect31}')
    print(f'E(a3, b3) = {expect33}')

    # CHSH value calculation
    corr = expect11 - expect13 + expect31 + expect33
    return corr

# Calculate and print CHSH correlation value
corr = chsh_corr(job)
print(f'CHSH correlation value: {round(corr, 3)}')

# Plotting histogram for verification
plot_histogram(job.get_counts(circuits[0]))

key_alice, key_bob = generate_shared_key(job, aliceMeasurementChoices, bobMeasurementChoices, circuits, numberOfSinglets)

# encrypting and decrypting data
def encrypting():
    with open('healthcare_data.txt', 'r') as file:
        healthcare_data = file.read()


    patient_records = healthcare_data.split('Patient: ')
    print(patient_records)

    encrypted_records = list()

    for record in patient_records:

        encrypted_record = encrypt_healthcare_data(record, key_alice)

        encrypted_records.append(encrypted_record)

        print(f"Encrypted data: {encrypted_record}")

        decrypted_data = decrypt_healthcare_data(encrypted_record, key_bob)
        print(f"Decrypted data: {decrypted_data}")

if __name__ == "__main__":
    encrypting()
