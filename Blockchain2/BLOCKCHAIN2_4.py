import random


def simulate_51_percent_attack(total_hashrate, attacker_hashrate):
    honest_hashrate = total_hashrate - attacker_hashrate
    rounds = 1000
    honest_blocks = 0
    attacker_blocks = 0
    for _ in range(rounds):
        if random.uniform(0, total_hashrate) < honest_hashrate:
            honest_blocks += 1
        else:
            attacker_blocks += 1

        print(f"Honest blocks: {honest_blocks}")
        print(f"Attacker blocks: {attacker_blocks}")

total_hashrate = 1000
attacker_hashrate = 600

simulate_51_percent_attack(total_hashrate, attacker_hashrate)
