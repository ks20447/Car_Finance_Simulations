from matplotlib import pyplot as plt
import random as rn
import numpy as np
from numpy.random import choice
import time
from colorama import Fore, Style
from LogisticRegression import *

# Simulation parameters and counters
ALL_BUYERS = []
ALL_LENDERS = []
TOTAL_CUSTOMERS = 10000
NUM_BUYERS = 0
MAX_BUYERS = 100
NUM_LENDERS = 0
MAX_LENDERS = 3
ALL_BANDS = [0, 1, 2, 3, 4]
ALL_ASSETS = [5000, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
SIMULATION_TIME = 120
MARKET_VALUE = ALL_ASSETS[-1] * MAX_BUYERS * SIMULATION_TIME


class Customer:
    def __init__(self, income):
        self.Client_Income = income
        self.House_Own = choice((0, 1), p=[0.398, 0.602])  # 0 denotes no house, 1 means owns at least one house
        self.Credit_Amount = rn.choice(ALL_ASSETS)
        self.Client_Marital_Status = choice(['M', 'W', 'S', 'D'], p=[0.5105, 0.0571, 0.3350, 0.0974])
        self.Client_Gender = choice(['Male', 'Female'], p=[0.50, 0.50])
        self.Age_Days = choice(choice([range(18, 20), range(20, 24), range(25, 29), range(30, 34),
                                       range(35, 44), range(45, 54), range(55, 64)],
                                      p=[0.0626, 0.1095, 0.1049, 0.1064, 0.2332, 0.2254, 0.1580]))*365
        self.Client_Family_Members = choice([0, 1, 2, 3, 4, 5, 6],
                                            p=[0.2727, 0.3333, 0.1616, 0.1414, 0.0606, 0.0202, 0.0102])
        self.wait = np.random.normal(14, 6, None)
        if self.Age_Days > 23725:
            self.Employed_Days = rn.randint(0, 17155)
        elif self.Age_Days <= 23725:
            self.Employed_Days = rn.randint(0, self.Age_Days - 6570)
        possession_docs = rn.choices([True, False], [95, 5], k=3)
        if all(possession_docs):
            self.eligible = True
        else:
            self.eligible = False


# Buyer object and attributes
class Buyer:
    def __init__(self, num, income, credit_band, asset, defaulting, month):
        self.num = num
        self.income = income
        self.credit = credit_band                           # Currently randomised
        self.asset = asset
        self.offered_asset = 0
        self.allowance = (self.income*0.3) / 12             # Allowance based off 50/30/20 rule of income spending
        self.duration = rn.choice([12, 24, 36, 48])
        self.status = "Applying"
        self.eligible = True
        self.preferred_duration = True
        self.preferred_asset = True
        self.offer = []
        self.defaulting = (1 - defaulting) / 12
        self.start_month = month

    def pay_loan(self, counter, lender):
        if self.offered_asset != 0:
            self.asset = self.offered_asset
        monthly = self.offer[1]
        total = monthly * self.duration - ((counter - self.start_month) * monthly)
        if round(total, 2) <= 0:
            self.status = "Finished"
        else:
            if rn.random() < self.defaulting:
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
    def __init__(self, num, credit_limit, max_duration, market_share):
        self.num = num
        self.credit_limit = credit_limit
        self.max_duration = max_duration
        self.profit = 0
        self.loss = 0
        self.collateral = 0
        self.max_loan = market_share
        self.current_loan = 0
        self.current_lending = 0
        self.rates = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

    # Function for lender to check credit band against their specific credit threshold
    def credit_check(self, buyer):
        if buyer.credit > self.credit_limit:
            print(f"Buyer {buyer.num} (Lender {self.num}): Rejected for credit")
            buyer.eligible = False
            buyer.status = "Rejected"
        else:
            buyer.status = 'Approved'

    # Function for lender to generate offer to the buyer
    # def monthly_offer(self, buyer):
    #     principle = buyer.asset
    #     allowance = buyer.allowance
    #     rate = rate_generate(buyer.income, buyer.asset, buyer.credit)
    #     r = rate / (12*100)
    #     duration = buyer.duration
    #     monthly_payments = principle * (r * ((1 + r) ** duration)) / (((1 + r) ** duration) - 1)
    #     if monthly_payments > allowance and duration == self.max_duration and ALL_ASSETS.index(buyer.asset) == 0:
    #         print(f"Buyer {buyer.num} (lender {self.num}): No affordable assets")
    #         buyer.eligible = False
    #     elif monthly_payments < allowance:
    #         monthly_payments = monthly_payments
    #     else:
    #         while duration < self.max_duration:
    #             duration += 12
    #             rate += 0.5
    #             r = rate / (12*100)
    #             monthly_payments = principle * (r * ((1 + r) ** duration)) / (((1 + r) ** duration) - 1)
    #             if monthly_payments < allowance:
    #                 break
    #         buyer.preferred_duration = False
    #         buyer.duration = duration
    #         if monthly_payments > allowance:
    #             lower_asset(self.num, buyer, allowance, duration, r)
    #     return rate, monthly_payments, duration

    def monthly_offer(self, buyer):
        principle = buyer.asset
        allowance = buyer.allowance
        rate = self.rates[buyer.credit]
        r = rate / (12 * 100)
        duration = buyer.duration
        monthly_payments = principle * (r * ((1 + r) ** duration)) / (((1 + r) ** duration) - 1)
        if monthly_payments > allowance:
            print(f"Buyer {buyer.num} (Lender {self.num}): Cannot afford loan")
            buyer.eligible = False
        return rate, monthly_payments, duration


# def lower_asset(num, buyer, allowance, duration, r):
#     possible_assets = ALL_ASSETS[0:ALL_ASSETS.index(buyer.asset)+1]
#     possible_assets.reverse()
#     for principle in possible_assets:
#         monthly_payments = principle * (r * ((1 + r) ** duration)) / (((1 + r) ** duration) - 1)
#         if monthly_payments < allowance:
#             print(f"Buyer {buyer.num} (Lender {num}): Original asset: £{buyer.asset}. Max affordable asset: £{principle}")
#             buyer.offered_asset = principle
#             buyer.preferred_asset = False
#             break
#         elif monthly_payments > allowance and principle == possible_assets[-1]:
#             print(f"Unable to offer alternative asset")
#             buyer.eligible = False
#     return monthly_payments


# Randomly assigns an income value based on ONS income distribution data in the UK
def income_generate():
    data_average = 13750
    data_std_dev = 7566
    sigma_log_normal = np.sqrt(np.log(1 + (data_std_dev / data_average) ** 2))
    mean_log_normal = np.log(data_average) - sigma_log_normal ** 2 / 2
    income = np.random.lognormal(mean=mean_log_normal, sigma=sigma_log_normal, size=1)
    income = round(income[0])
    return income

# def rate_generate(income, asset, credit):
#     rates_array = np.zeros([3, len(ALL_BANDS)])
#     for i in range(len(ALL_BANDS)):
#         for j in range(3):
#             rates_array[j][i] = ((i + 0.25) * (j + 0.25)) + 9
#     if income/asset >= rn.randint(2, 4):
#         ratio = 2
#     elif income/asset <= rn.random():
#         ratio = 0
#     else:
#         ratio = 1
#     rate = (rates_array[ratio][credit - 1] + rn.random())
#     return rate


def customer_setup(num_customers):
    accepted_customers = []
    fields = ['Client_Income', 'House_Own', 'Credit_Amount', 'Client_Marital_Status', 'Client_Gender', 'Age_Days',
              'Employed_Days', 'Client_Family_Members']
    for i in range(num_customers):
        customer_income = income_generate()
        customer = Customer(customer_income)
        if customer.eligible:
            accepted_customers.append(customer.__dict__)
    df = pd.DataFrame(accepted_customers, columns=fields)
    df.to_csv("customers_dataframe.csv")


def buyer_setup(index, t, buyers_dataframe):
    global ALL_BUYERS, NUM_BUYERS
    num_buyers = len(buyers_dataframe)
    for i in range(num_buyers):
        buyer_num = i + (index * num_buyers)
        buyer_income = buyers_dataframe.iloc[i, 1]
        buyer_band = buyers_dataframe.iloc[i, -1]
        buyer_asset = buyers_dataframe.iloc[i, 3]
        buyer_default = buyers_dataframe.iloc[i, -2]
        ALL_BUYERS.append(Buyer(buyer_num, buyer_income, buyer_band, buyer_asset, buyer_default, t))
        NUM_BUYERS += 1


def lender_setup(market_share):
    global ALL_LENDERS
    ALL_LENDERS.append(Lender(0, 3, 48, market_share * 0.5))
    ALL_LENDERS.append(Lender(1, 10, 48, market_share * 0.5))


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
              Fore.GREEN + f" +£{round(lender.profit, 2):,}" + Style.RESET_ALL + f" / " +
              Fore.RED + f"-£{round(lender.loss, 2):,}" + Style.RESET_ALL +
              f" / £{round(lender.collateral,2):,}")
        print(f"Total amount borrowed by customers: £{lender.current_loan:,}")
        print(f"Current lending: £{round(lender.current_lending, 2):,}")
        print(f"")


def simulation(sim_time, num_customers, num_buyers):
    global ALL_BUYERS, ALL_LENDERS
    lender_setup(MARKET_VALUE)
    index = 0
    customer_setup(num_customers)
    xd = predict_from_generated_customer("customers_dataframe.csv", "Train_Dataset.csv")
    xd = xd.loc[xd["Band"] != 10]
    xd.to_csv("buyers_dataframe.csv")
    buyers_dataframe = pd.read_csv("buyers_dataframe.csv")
    for t in range(sim_time):
        print(Fore.BLUE + f"Month {t}" + Style.RESET_ALL)
        if t % 6 == 0:
            buyer_setup(index, t, buyers_dataframe[num_buyers*index:num_buyers+(num_buyers*index)])
            current_buyers = ALL_BUYERS[num_buyers*index:num_buyers+(num_buyers*index)]
            generate_offers(current_buyers, ALL_LENDERS)
            index += 1
            print(f"")
        loan_payments(t, ALL_BUYERS, ALL_LENDERS)


if __name__ == '__main__':
    start = time.perf_counter()
    simulation(SIMULATION_TIME, TOTAL_CUSTOMERS, MAX_BUYERS)
    end = time.perf_counter()
    print(f"Simulation finished in {round(end - start, 2)}s")