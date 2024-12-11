class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.data = []

    def add_data(self, data):
        self.data.append(data)

    def get_data(self):
        return self.data


if __name__ == "__main__":
    nodes = [Node("Node 1"), Node("Node 2"), Node("Node 3")]

    # Simulating data distribution
    nodes[0].add_data("Transaction A")
    nodes[1].add_data("Transaction B")
    nodes[2].add_data("Transaction C")
    for node in nodes:
        print(f"{node.node_id} data: {node.get_data()}")
