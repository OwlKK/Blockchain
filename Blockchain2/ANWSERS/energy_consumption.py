# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt

# File paths
bitcoin_file = '../ANWSERS/bitcoin-energy-consumpti.csv'
ethereum_file = '../ANWSERS/ethereum-energy-consumpt.csv'

# Load the CSV files
bitcoin_data = pd.read_csv(bitcoin_file)
ethereum_data = pd.read_csv(ethereum_file)

# Convert DateTime columns to datetime objects
bitcoin_data['DateTime'] = pd.to_datetime(bitcoin_data['DateTime'])
ethereum_data['DateTime'] = pd.to_datetime(ethereum_data['DateTime'])

# Identify the approximate date of Ethereum's switch to PoS by observing energy patterns
ethereum_data.sort_values(by='DateTime', inplace=True)
transition_threshold = 1  # Define a threshold for identifying PoS transition (TWh/year)
ethereum_pos_start = ethereum_data.loc[ethereum_data['Estimated TWh per Year'] <= transition_threshold, 'DateTime'].min()

# Segment Ethereum data into PoW and PoS phases
ethereum_pow = ethereum_data[ethereum_data['DateTime'] < ethereum_pos_start]
ethereum_pos = ethereum_data[ethereum_data['DateTime'] >= ethereum_pos_start]

# Segment Bitcoin data up to and after the Ethereum PoS transition date
bitcoin_upto_pos = bitcoin_data[bitcoin_data['DateTime'] < ethereum_pos_start]
bitcoin_after_pos = bitcoin_data[bitcoin_data['DateTime'] >= ethereum_pos_start]

# Plot all diagrams in a single figure
plt.figure(figsize=(18, 15))

# Subplot 1: Ethereum PoW vs PoS energy consumption
plt.subplot(3, 1, 1)
plt.plot(ethereum_pow['DateTime'], ethereum_pow['Estimated TWh per Year'], label='Ethereum PoW', color='blue')
plt.plot(ethereum_pos['DateTime'], ethereum_pos['Estimated TWh per Year'], label='Ethereum PoS', color='green')
plt.axvline(ethereum_pos_start, color='red', linestyle='--', label='Ethereum PoS Transition (2022-09-16)')
plt.title('Ethereum Energy Consumption: PoW vs PoS')
plt.xlabel('Date')
plt.ylabel('Estimated TWh per Year')
plt.legend()
plt.grid(True)

# Subplot 2: Bitcoin vs Ethereum PoW
plt.subplot(3, 1, 2)
plt.plot(bitcoin_upto_pos['DateTime'], bitcoin_upto_pos['Estimated TWh per Year'], label='Bitcoin', color='orange')
plt.plot(ethereum_pow['DateTime'], ethereum_pow['Estimated TWh per Year'], label='Ethereum PoW', color='blue')
plt.title('Energy Consumption: Bitcoin vs Ethereum PoW')
plt.xlabel('Date')
plt.ylabel('Estimated TWh per Year')
plt.legend()
plt.grid(True)

# Subplot 3: Bitcoin vs Ethereum after PoS transition
plt.subplot(3, 1, 3)
plt.plot(bitcoin_after_pos['DateTime'], bitcoin_after_pos['Estimated TWh per Year'], label='Bitcoin', color='orange')
plt.plot(ethereum_pos['DateTime'], ethereum_pos['Estimated TWh per Year'], label='Ethereum PoS', color='green')
plt.title('Energy Consumption: Bitcoin vs Ethereum (Post-PoS)')
plt.xlabel('Date')
plt.ylabel('Estimated TWh per Year')
plt.legend()
plt.grid(True)

# Show all subplots
plt.tight_layout()
plt.show()
