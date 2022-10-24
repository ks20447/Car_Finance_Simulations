# Car finance simulation

from matplotlib import pyplot as plt
import random as rn
import numpy as np
import pandas as pd
import time
import math
from colorama import Fore, Style

# Simulation parameters and counters
ALL_BUYERS = []
ALL_LENDERS = []
NUM_BUYERS = 0
MAX_BUYERS = 10
NUM_LENDERS = 0
MAX_LENDERS = 3
ALL_BANDS = [0, 1, 2, 3, 4]
ALL_ASSETS = [4000, 8000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000]
SIMULATION_TIME = 120


# Buyer object and attributes
class Buyer:
    def __init__(self, num, income, credit_band, month):
        self.num = num
        self.income = income
        self.credit = credit_band                           # Currently randomised
        self.asset = rn.choice(ALL_ASSETS)
        self.offered_asset = 0
        self.allowance = (self.income*0.3) / 12             # Allowance based off 50/30/20 rule of income spending
        self.duration = rn.choice([12, 24, 36, 48])
        self.status = "Applying"
        self.eligible = True
        self.preferred_duration = True
        self.preferred_asset = True
        self.offer = []
        self.defaulting = rn.random()/(10*12)               # Currently randomised
        self.start_month = month

    def pay_loan(self, counter, lender):
        if self.offered_asset != 0:
            self.asset = self.offered_asset
        monthly = self.offer[1]
        total = monthly * self.duration - ((counter - self.start_month) * monthly)
        if round(total, 2) <= 0:
            self.status = "Finished"
        else:
            if math.floor(rn.uniform(0, 1 / (1 - self.defaulting))):
                print(f"Buyer {self.num} (Lender {lender.num}) defaulted. "
                      f"Total remaining: £{round(total, 2)} ")
                usage_parameter = 0.9
                collateral = (self.asset - (counter - self.start_month) * usage_parameter) * 0.8
                lender.loss += (total - collateral)
                lender.collateral += collateral
                self.status = 'Defaulted'
            else:
                lender.profit += monthly


# Lender object and attributes
class Lender:
    def __init__(self, num, credit_limit):
        self.num = num
        self.credit_limit = credit_limit
        self.max_duration = 48
        self.profit = 0
        self.loss = 0
        self.collateral = 0
        self.max_loan = 500000
        self.current_loan = 0
        self.current_lending = 0

    # Function for lender to check credit band against their specific credit threshold
    def credit_check(self, buyer):
        if buyer.credit < self.credit_limit:
            print(f"Buyer {buyer.num} (Lender {self.num}): Rejected for credit")
            buyer.eligible = False
            buyer.status = "Rejected"
        else:
            buyer.status = 'Approved'

    # Function for lender to generate offer to the buyer
    def monthly_offer(self, buyer):
        principle = buyer.asset
        allowance = buyer.allowance
        rate = rate_generate(buyer.income, buyer.asset, buyer.credit)
        r = rate / (12*100)
        duration = buyer.duration
        monthly_payments = principle * (r * ((1 + r) ** duration)) / (((1 + r) ** duration) - 1)
        if monthly_payments > allowance and duration == self.max_duration and ALL_ASSETS.index(buyer.asset) == 0:
            print(f"Buyer {buyer.num} (lender {self.num}): No affordable assets")
            buyer.eligible = False
        elif monthly_payments < allowance:
            monthly_payments = monthly_payments
        else:
            while duration < self.max_duration:
                duration += 12
                rate += 0.5
                r = rate / (12*100)
                monthly_payments = principle * (r * ((1 + r) ** duration)) / (((1 + r) ** duration) - 1)
                if monthly_payments < allowance:
                    break
            buyer.preferred_duration = False
            buyer.duration = duration
            if monthly_payments > allowance:
                lower_asset(self.num, buyer, allowance, duration, r)
        return rate, monthly_payments, duration


def lower_asset(num, buyer, allowance, duration, r):
    possible_assets = ALL_ASSETS[0:ALL_ASSETS.index(buyer.asset)+1]
    possible_assets.reverse()
    for principle in possible_assets:
        monthly_payments = principle * (r * ((1 + r) ** duration)) / (((1 + r) ** duration) - 1)
        if monthly_payments < allowance:
            print(f"Buyer {buyer.num} (Lender {num}): Original asset: £{buyer.asset}. Max affordable asset: £{principle}")
            buyer.offered_asset = principle
            buyer.preferred_asset = False
            break
        elif monthly_payments > allowance and principle == possible_assets[-1]:
            print(f"Unable to offer alternative asset")
            buyer.eligible = False
    return monthly_payments


# Randomly assigns an income value based on ONS income distribution data in the UK
def income_generate():
    income_table = pd.read_table('IncomeDistribution.txt')
    income_band = np.array(income_table[income_table.columns[0]])
    count = np.array(income_table[income_table.columns[1]])
    income_data = []
    for i in range(len(income_band)):
        income_data.append([income_band[i]] * count[i])
    income_data = np.concatenate(income_data)
    income = rn.choice(income_data)
    return income


def rate_generate(income, asset, credit):
    rates_array = np.zeros([3, len(ALL_BANDS)])
    for i in range(len(ALL_BANDS)):
        for j in range(3):
            rates_array[j][i] = ((i + 0.25) * (j + 0.25)) + 9
    if income/asset >= rn.randint(2, 4):
        ratio = 2
    elif income/asset <= rn.random():
        ratio = 0
    else:
        ratio = 1
    rate = (rates_array[ratio][credit - 1] + rn.random())
    return rate


def buyer_setup(index, t, num_buyers):
    global ALL_BUYERS, NUM_BUYERS
    for i in range(num_buyers):
        buyer_income = income_generate()*1000
        buyer_band = rn.choice(ALL_BANDS)                 # This will be swapped for credit score process
        buyer_num = i + (index*num_buyers)
        ALL_BUYERS.append(Buyer(buyer_num, buyer_income, buyer_band, t))
        NUM_BUYERS += 1


def lender_setup(num_lenders):
    global ALL_LENDERS, NUM_LENDERS
    for j in range(num_lenders):
        lender_check = rn.choice(ALL_BANDS)
        ALL_LENDERS.append(Lender(j, lender_check))
        NUM_LENDERS += 1


def ret_2nd_ele(tuple_1):
    return tuple_1[1]


def generate_offers(all_buyers, all_lenders):
    for current_buyer in all_buyers:
        for current_lender in all_lenders:
            current_lender.credit_check(current_buyer)
            if current_lender.max_loan > current_lender.current_lending:
                if current_buyer.eligible:
                    offer_rate, offer_monthly, offer_duration = current_lender.monthly_offer(current_buyer)
                if current_buyer.eligible:
                    if current_buyer.offered_asset == 0:
                        asset = current_buyer.asset
                    else:
                        asset = current_buyer.offered_asset
                    print(f"Buyer {current_buyer.num} (Lender {current_lender.num}): "
                          f"Loan principle of £{asset} with an "
                          f"interest rate of {offer_rate:.1f}% for {offer_duration} months."
                          f" Total Monthly payments: £{offer_monthly:.2f}")
                    current_buyer.offer.append((current_lender.num, offer_monthly))
                    current_buyer.status = "Paying"
                current_buyer.eligible = True
            else:
                print(f"Max loans exceeded")
        if current_buyer.offer:
            accepted_offer = min(current_buyer.offer, key=ret_2nd_ele)
            print(f"Accepted offer: Lender {accepted_offer[0]}. Monthly payments of £{round(accepted_offer[1], 2)}. "
                  f"Preferred duration - {current_buyer.preferred_duration}. "
                  f"Preferred asset - {current_buyer.preferred_asset}")
            current_buyer.offer = accepted_offer
            lender = all_lenders[accepted_offer[0]]
            lender.current_loan += current_buyer.asset
        print(f"")


def loan_payments(month, all_buyers, all_lenders):
    for payee in all_buyers:
        if payee.offer:
            lender = all_lenders[payee.offer[0]]
            payee.pay_loan(month, lender)
    for lender in all_lenders:
        lender.current_lending = lender.current_loan - lender.profit
        print(f"Lender {lender.num}: Profit/Loss/Collateral" +
              Fore.GREEN + f" +£{round(lender.profit, 2)}" + Style.RESET_ALL + f" / " +
              Fore.RED + f"-£{round(lender.loss, 2)}" + Style.RESET_ALL +
              f" / £{round(lender.collateral,2)}")
        print(f"Total amount borrowed by customers: £{lender.current_loan}")
        print(f"Current lending: £{round(lender.current_lending, 2)}")
        print(f"")


def simulation(sim_time, num_buyers, num_lenders):
    global ALL_BUYERS, ALL_LENDERS
    lender_setup(num_lenders)
    index = 0
    for t in range(sim_time):
        print(Fore.BLUE + f"Month {t}" + Style.RESET_ALL)
        if t % 12 == 0:
            buyer_setup(index, t, num_buyers)
            current_buyers = ALL_BUYERS[num_buyers*index:num_buyers+(num_buyers*index)]
            generate_offers(current_buyers, ALL_LENDERS)
            index += 1
            print(f"")
        loan_payments(t, ALL_BUYERS, ALL_LENDERS)


if __name__ == '__main__':
    start = time.perf_counter()
    simulation(SIMULATION_TIME, MAX_BUYERS, MAX_LENDERS)
    end = time.perf_counter()
    print(f"Simulation finished in {round(end - start, 2)}s")
