import hashlib
import datetime


class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

    # Convert string value of self.data into byte format [sha256 requires bytes]
    # sha256 - generate hash from self.data in byte format
    # hexdigest() - convert hash into string representation
    def calculate_data_hash(self):
        return hashlib.sha256(self.data.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", datetime.datetime.now(), "Genesis Block",
                              self.calculate_hash(0, "0", datetime.datetime.now(), "Genesis Block"))

        self.chain.append(genesis_block)

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_index = previous_block.index + 1
        new_timestamp = datetime.datetime.now()
        new_hash = self.calculate_hash(new_index, previous_block.hash,
                                       new_timestamp, data)

        # Create the new block
        new_block = Block(new_index, previous_block.hash, new_timestamp, data, new_hash)

        # Calculate the hash of the new block's data
        new_data_hash = new_block.calculate_data_hash()
        print(f"Data Hash for Block {new_index}: {new_data_hash}")

        # Calculate the hash of the previous block's data
        previous_data_hash = previous_block.calculate_data_hash()
        print(f"Data Hash for Previous Block {previous_block.index}: {previous_data_hash}")

        # Check integrity
        if new_data_hash != previous_data_hash:
            print(f"Integrity check passed for Block {new_index}.")

            # Add the block to the chain
            self.chain.append(new_block)
        else:
            raise ValueError(
                f"Integrity check failed: Data hash of Block {new_index} matches the previous block. "
                "Blockchain halted."
            )

    def calculate_hash(self, index, previous_hash, timestamp, data):
        hash_data = str(index) + previous_hash + str(timestamp) + data

        return hashlib.sha256(hash_data.encode()).hexdigest()

    def print_chain(self):
        for block in self.chain:
            print(f"Block {block.index} - Timestamp: {block.timestamp} - Data:{block.data} - Hash: {block.hash}")
            exit(1)


if __name__ == "__main__":
    # Create a blockchain
    blockchain = Blockchain()

    # Add blocks to the blockchain
    blockchain.add_block("Transaction 1")
    blockchain.add_block("Transaction 2")
    blockchain.add_block("Transaction 3")

    # Print the entire blockchain
    blockchain.print_chain()

"""
--- Comparative analysis of centralized, decentralized, and distributed systems ---

    *Centralised (Private/Permissioned blockchain)
    
        +Single point of control that governs data storage, decision-making, and system operations
        +Efficiency due to the absence of consensus mechanisms
        +Simplicity due to the absence of consensus mechanisms
        
        -Single point of failure
        
        Examples:
            *Centralised cloud storage
            
    *Decentralised
    
        +Shared (between participants) point of control, nodes work independently 
        and collaborate to achieve system-wide goals.
        +Improved resilience against failures
        +Security
        +Reduced reliance on central trust
        
        -Multiple points of failure (Failure of one node doesnt disrupt the system as a whole)
        -Coordination among nodes can be complex
        -Consensus can be resource intensive
        
        Examples: 
            *Bittorrent
            *Bitcoin
            *Ethereum

    *Distributed
        +Scalability
        +Improved adaptability
        +Latency
        -Complex data maintenance
        -Sync issues
        
        Examples:
            Distributed databases i.e. Cassandra
            CDN's
            

--- Real-world use case for each blockchain type (public, private, consortium) with their strengths and weaknesses ---
    *Public
    
        + Decentralisation - no single point of failure
        + Transparency - transactions are visible to all participants
        
        - Scalability - slower transaction speeds and higher costs due to extensive validation processes
        - Energy consumption - Resource-intensive consensus mechanisms e.g. Mining
        
        Examples:
            Bitcoin - cross-border payments
            Ethereum
        
    *Private
    
        + Control - access is restricted to trusted participants
        + Efficiency - faster transaction processing and reduced operational costs due to limited trusted participants
        + Privacy - sensitive data is secured - only authorized participants can access transaction details.
        
        - Centralistion - limited to a single entity or organization - less resilient to single points of failure
        - Trust - Stakeholders need to trust the managing entity
        
        Examples:
            Walmart’s blockchain for food traceability
            IBM’s Food Trust
        
    
    *Consortium
    
        + Collaborative Effort - a group of trusted organizations manages the network,
                                 distributing control and reducing reliance on a single entity.
        + Efficiency - fewer validators allow for quicker and more cost-effective transactions than public blockchains
        
        - Governance complexity - decision-making among multiple organizations can be slow and challenging
        - Limited Decentralisation - more centralized than public blockchains,
                                    potentially introducing risks if trust between entities fails
        
        Examples:
            Interbank Settlements - R3 Corda - used for banking systems to streamline processes like trade finance
                                               and interbank transactions
                                    Hyperledger Fabric - banking


--- Compare the energy efficiency of PoW and PoS consensus mechanisms
 with energy consumption for validating a transaction in each case ---
 
 *PoW
    Bitcoin, which operates on PoW, consumes between 70–150 terawatt-hours (TWh) annually
    Each Bitcoin transaction consumes around 707 kWh - yhe high energy cost is due to specialized hardware (ASICs)
    and computational effort to solve the cryptographic challenge
 
 *PoS
    PoS instead of using computational work it uses system where validators are chosen
    based on their cryptocurrency holdings ("stake") - validators only need to prove ownership of the stake 
    and execute lightweight validation logic. The energy required for a single transaction in PoS systems
    is minimal—about 0.0002 kWh
 
 
Sources:
    https://www.scalingparrots.com/en/decentralized-vs-centralized-blockchain/
    https://101blockchains.com/decentralized-vs-centralized/
    https://www.researchgate.net/publication/380302887_Drawing_the_Boundaries_Between_Blockchain_and_Blockchain-Like_Systems_A_Comprehensive_Survey_on_Distributed_Ledger_Technologies
    https://www.morpher.com/blog/consortium-blockchain
    https://zebpay.com/blog/consortium-blockchains-the-middle-ground-between-public-and-private
    https://cms.parallelchain.io/uploads/IEEE_From_Use_Case_to_Benchmark_Comparing_Consortium_and_Private_Blockchains_31d5ffbfb3.pdf
    https://www.morpher.com/blog/consortium-blockchain
    https://www.investopedia.com/the-ethereum-merge-6504132
    https://www.investopedia.com/ethereum-completes-the-merge-6666337
"""
