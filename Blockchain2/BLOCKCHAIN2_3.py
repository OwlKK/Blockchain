import random

validators = ["Validator A", "Validator B", "Validator C", "Validator D"]
stake = {"Validator A": 100, "Validator B": 150, "Validator C": 200, "Validator D": 120}


def select_validator(stake):
    total_stake = sum(stake.values())
    selected_value = random.uniform(0, total_stake)
    current_sum = 0

    # Shuffle the stake items to avoid bias from order
    shuffled_stake = list(stake.items())
    random.shuffle(shuffled_stake)

    for validator, value in stake.items():
        current_sum += value
        if current_sum >= selected_value:
            return validator


selected_validator = select_validator(stake)
print(f"Selected validator: {selected_validator}")
