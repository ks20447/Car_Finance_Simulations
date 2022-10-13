import random as rn
import numpy as np
import pandas as pd

ALL_BUYERS = []
ALL_LENDERS = []
NUM_BUYERS = 0
MAX_BUYERS = 5
NUM_LENDERS = 0
MAX_LENDERS = 1


class Buyer:
    def __init__(self, num, income, credit_band):
        self.num = num
        self.income = income
        self.credit = credit_band
        self.asset = rn.choice([15000, 30000, 60000])
        self.allowance = (self.income*0.2) / 12
        self.eligible = True


class Lender:
    def __init__(self, num, credit_limit):
        self.num = num
        self.credit_limit = credit_limit
        self.interest_rates = [9, 8, 7, 6, 5]
        self.durations = [48, 36, 24, 12]

    def credit_check(self, buyer):
        if buyer.credit < self.credit_limit:
            print(f"Buyer {buyer.num} rejected")
            buyer.num = -1
            buyer.eligible = False

    def monthly_offer(self, buyer):
        principle = buyer.asset
        allowance = buyer.allowance
        rate = self.interest_rates[buyer.credit]
        r = rate / (12*100)
        durations = self.durations
        for i in range(len(durations)):
            possible_payments = (principle * (r * ((1 + r) ** durations[i])) / (((1 + r) ** durations[i]) - 1))
            if possible_payments > allowance and i > 0:
                monthly_payments = \
                    (principle * (r * ((1 + r) ** durations[i - 1])) / (((1 + r) ** durations[i - 1]) - 1))
                duration = durations[i - 1]
                break
            elif possible_payments > allowance and i == 0:
                print(f"Buyer {buyer.num}: Not enough income for asset loan")
                monthly_payments = 0
                duration = 0
                buyer.eligible = False
                break
        return rate, round(monthly_payments, 2), duration


def simulation_setup(num_buyers, num_lenders):
    global ALL_BUYERS, ALL_LENDERS, NUM_BUYERS, NUM_LENDERS
    for i in range(num_buyers):
        buyer_income = income_generate()*1000
        buyer_band = rn.choice([0, 1, 2, 3, 4])  # This will be swapped for credit score process
        ALL_BUYERS.append(Buyer(i, buyer_income, buyer_band))
        NUM_BUYERS += 1
    for j in range(num_lenders):
        lender_check = rn.choice([0, 1])
        ALL_LENDERS.append(Lender(j, lender_check))
        NUM_LENDERS += 1


def income_generate():
    # randomly chooses an income value based on ONS income distribution data in the UK
    income_table = pd.read_table('IncomeDistribution.txt')
    income_band = np.array(income_table[income_table.columns[0]])
    count = np.array(income_table[income_table.columns[1]])
    income_data = []
    for i in range(len(income_band)):
        income_data.append([income_band[i]] * count[i])
    income_data = np.concatenate(income_data)
    income = rn.choice(income_data)
    return income


if __name__ == '__main__':
    simulation_setup(MAX_BUYERS, MAX_LENDERS)
    for current_buyer in ALL_BUYERS:
        for current_lender in ALL_LENDERS:
            current_lender.credit_check(current_buyer)
            if current_buyer.eligible:
                offer_rate, offer_monthly, offer_duration = current_lender.monthly_offer(current_buyer)
            if current_buyer.eligible:
                print(f"Buyer {current_buyer.num}: Loan principle of £{current_buyer.asset} with an "
                      f"interest rate of {offer_rate}% for {offer_duration} months."
                      f" Total Monthly payments: £{offer_monthly}")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
