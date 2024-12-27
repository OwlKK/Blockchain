import hashlib
import time
from cryptography.fernet import Fernet


class Block:
    def __init__(self, previous_hash, transactions):
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = str(self.timestamp) + str(self.previous_hash) + str(self.transactions)
        return hashlib.sha256(data.encode()).hexdigest()


class Transaction:
    def __init__(self, sender, receiver, product, quantity, description=""):
        self.timestamp = time.time()
        self.sender = sender
        self.receiver = receiver
        self.product = product
        self.quantity = quantity
        self.description = description
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Fernet symmetric key encryption (more secure than Caesar cipher)
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)

        encrypted_data = cipher_suite.encrypt(str(self.sender).encode() +
                                              str(self.receiver).encode() +
                                              str(self.product).encode() +
                                              str(self.quantity).encode() +
                                              str(self.description).encode())

        return hashlib.sha256(encrypted_data).hexdigest()

    def calculate_hash2(self):
        # Caesar cipher for basic encryption
        encrypted_data = self.encrypt_data()
        data = str(self.timestamp) + str(encrypted_data)
        return hashlib.sha256(data.encode()).hexdigest()

    def encrypt_data(self):
        key = 3  # Caesar cipher key
        encrypted_data = ""
        for char in str(self.sender) + str(self.receiver) + str(self.product) + str(self.quantity) + str(
                self.description):
            if char.isalpha():
                encrypted_data += chr((ord(char) + key - ord('a')) % 26 + ord('a'))
            else:
                encrypted_data += char
        return encrypted_data


class Participant:
    def __init__(self, participant_id, public_key):
        self.participant_id = participant_id
        self.public_key = public_key


class SupplyChainNode:
    def __init__(self, node_id, admin_key):
        self.node_id = node_id
        self.admin_key = admin_key
        self.participants = {}
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(previous_hash="1", transactions=[])

    def add_transaction(self, sender, receiver, product, quantity, description=""):
        if sender not in self.participants or receiver not in self.participants:
            print("Invalid participant(s). Transaction aborted.")
            return

        transaction = Transaction(sender, receiver, product, quantity, description)
        block = self.create_block([transaction])
        self.chain.append(block)
        print("Transaction added to the blockchain.")

    def create_block(self, transactions):
        previous_hash = self.get_previous_hash()
        return Block(previous_hash, transactions)

    def get_previous_hash(self):
        return self.chain[-1].hash if self.chain else "0"

    def add_participant(self, participant):
        if participant.participant_id not in self.participants:
            self.participants[participant.participant_id] = participant
            print(f"Participant {participant.participant_id} added.")
        else:
            print(f"Participant {participant.participant_id} already exists.")

    def view_participants(self):
        if not self.participants:
            print("No participants available.")
        else:
            print("Participants:")
            for participant_id, participant in self.participants.items():
                print(f"  ID: {participant_id}, Public Key: {participant.public_key}")

    def view_blockchain(self):
        for idx, block in enumerate(self.chain):
            print(f"Block {idx}:")
            print(f"  Timestamp: {time.ctime(block.timestamp)}")
            print(f"  Previous Hash: {block.previous_hash}")
            print(f"  Hash: {block.hash}")
            print(f"  Transactions:")
            for transaction in block.transactions:
                print(f"    Sender: {transaction.sender}, Receiver: {transaction.receiver}, Product: {transaction.product}")
                print(f"    Quantity: {transaction.quantity}, Description: {transaction.description}")
                print(f"    Timestamp: {time.ctime(transaction.timestamp)}, Hash: {transaction.hash}")


# Command-line interface
def user_interface():
    print("Welcome to the Supply Chain Node CLI!")
    node_id = input("Enter Node ID: ")
    admin_key = input("Enter Admin Key: ")
    supply_chain_node = SupplyChainNode(node_id, admin_key)

    while True:
        print("\nCommands:")
        print("1. Add Participant")
        print("2. Add Transaction")
        print("3. View Participants")
        print("4. View Blockchain")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            participant_id = input("Enter Participant ID: ")
            public_key = input("Enter Public Key: ")
            participant = Participant(participant_id, public_key)
            supply_chain_node.add_participant(participant)

        elif choice == "2":
            sender = input("Enter Sender Participant ID: ")
            receiver = input("Enter Receiver Participant ID: ")
            product = input("Enter Product: ")
            quantity = input("Enter Quantity: ")
            description = input("Enter Description (optional): ")
            supply_chain_node.add_transaction(sender, receiver, product, quantity, description)

        elif choice == "3":
            supply_chain_node.view_participants()

        elif choice == "4":
            supply_chain_node.view_blockchain()

        elif choice == "5":
            print("Exiting the Supply Chain Node CLI. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a valid option.")


# Example Usage:
# Create participants with unique public keys
participant1 = Participant(participant_id="SupplierA", public_key="SUPPLIER_KEY")
participant2 = Participant(participant_id="ManufacturerB", public_key="MANUFACTURER_KEY")

# Instantiate the supply chain node with an admin key
supply_chain_node = SupplyChainNode(node_id="Node1", admin_key="ADMIN_KEY")

# Add participants to the supply chain node
supply_chain_node.add_participant(participant1)
supply_chain_node.add_participant(participant2)

# Add a sample transaction to the blockchain
supply_chain_node.add_transaction(sender="SupplierA", receiver="ManufacturerB", product="RawMaterialX", quantity=100,
                                  description="Initial supply")

# Attempting to add a transaction with invalid participants
supply_chain_node.add_transaction(sender="NonexistentParticipant", receiver="ManufacturerB", product="RawMaterialX",
                                  quantity=50, description="Invalid transaction")

# Display the blockchain
supply_chain_node.view_blockchain()

# CLI Start:
if __name__ == "__main__":
    user_interface()
