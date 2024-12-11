import random


class LotteryPoS:
    # Initialize the Lottery system with validators and stakes
    def __init__(self):
        self.validators = {}  # Validators + stakes
        self.total_stake = 0
        self.lottery_prize = 0

    # Allow a validator to stake a certain amount of tokens
    def stake(self, validator, amount):
        if validator in self.validators:
            self.validators[validator] += amount  # Accumulate stakes across rounds
        else:
            self.validators[validator] = amount

        self.total_stake += amount
        print(f"{validator} staked {amount} tokens. Total stake: {self.total_stake}")

    # Simulate the lottery draw PoS
    def draw_winner(self):
        if not self.validators:
            print("No validators to select from.")
            return None

        # Calculate the total stake
        self.lottery_prize = self.total_stake
        print(f"Total stake in the lottery: {self.lottery_prize} tokens")

        # Select a winner based on their stake
        # Weighted random selection method where higher stakes have higher chances of winning
        total_weight = sum(self.validators.values())
        random_value = random.uniform(0, total_weight)
        cumulative_stake = 0
        winner = None

        # Iterate through validators and select the one whose stake range includes the random value
        for validator, stake in self.validators.items():
            cumulative_stake += stake
            if cumulative_stake >= random_value:
                winner = validator
                break

        print(f"Winner: {winner} with a stake of {self.validators[winner]} tokens.")
        print(f"{winner} wins the lottery prize of {self.lottery_prize} tokens!\n")
        return winner

    # Reset the lottery for the next round
    def reset_lottery(self, reset_stakes=False):
        self.total_stake = 0
        if reset_stakes:
            self.validators.clear()  # Clear validators if stakes are reset
        print("Lottery has been reset for the next round.\n")


if __name__ == "__main__":
    # Initialize the lottery system
    lottery = LotteryPoS()

    # Input the number of rounds to be played
    rounds = int(input("Enter the number of rounds to be played: "))
    reset_stakes = input("Reset stakes after each round? (yes/no): ").strip().lower() == "yes"

    # Validators and their initial stakes
    initial_stakes = {
        "Validator A": random.randint(50, 150),
        "Validator B": random.randint(50, 150),
        "Validator C": random.randint(50, 150),
        "Validator D": random.randint(50, 150),
    }

    # Stake initial amounts for each validator
    for validator, stake in initial_stakes.items():
        lottery.stake(validator, stake)

    # Run the lottery for the specified number of rounds
    for round_num in range(1, rounds + 1):
        print(f"\n--- Round {round_num} ---")

        # Draw a winner for this round
        winner = lottery.draw_winner()

        # Optionally reset stakes for the next round
        lottery.reset_lottery(reset_stakes=reset_stakes)

        # If stakes are not reset, allow validators to add more tokens
        if not reset_stakes:
            for validator in initial_stakes.keys():
                additional_stake = random.randint(10, 100)  # Additional stake for the next round
                lottery.stake(validator, additional_stake)
