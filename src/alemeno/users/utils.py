import pandas as pd
from datetime import datetime

today = datetime.now()

# Credit scores is determined by these factors:
# 1. How much percentage of the approved limit has the customer used to take their active loans since it is recommended that
#    30% is ideal (source: https://www.paisabazaar.com/credit-score/cibil-score-calculation/), we give scores based on that.
# 2. Percentage of emis paid on time vs emis not paid on time, since customers can pay in advance higher score is given to
#    customers who pay in advance.
# 3. Customers who take loans for higher periods on a average are given a higher score.
# 4. Older customers are trusted and deserve a higher rating, so the oldest loan the custimer has taken
#    the better the score they get.
# 5. The more the number of loans they are approved the more rating the customer gets.
#
# These points have weightages:
# pt:          1     2     3     4     5
# weightage:  25%   30%   15%   10%   20%

def calculate_credit_score(customer_data, customer_loan_data):
    customer_data_df = pd.DataFrame.from_records(customer_data)    
    customer_loan_data_df = pd.DataFrame.from_records(customer_loan_data)
    
    # convert dates to pandas dattime format
    customer_loan_data_df['date_of_approval'] = pd.to_datetime(customer_loan_data_df['date_of_approval'])
    customer_loan_data_df['end_date'] = pd.to_datetime(customer_loan_data_df['end_date'])
    
    customer_active_loans = customer_loan_data_df[customer_loan_data_df['end_date'] > today]
    
    credit_score = 0
    warning = []
    
    perc_amount_vs_limit = (customer_active_loans['loan_amount'].sum() / customer_data_df['approved_limit'] * 100).iloc[0]
    if perc_amount_vs_limit < 15:
        credit_score += 25
    elif perc_amount_vs_limit < 30:
        credit_score += 22
    elif perc_amount_vs_limit < 35:
        credit_score += 16
    elif perc_amount_vs_limit < 40:
        credit_score += 14
    elif perc_amount_vs_limit < 55:
        credit_score += 10
    elif perc_amount_vs_limit < 60:
        credit_score += 6
    elif perc_amount_vs_limit < 80:
        credit_score += 4
        warning.append("You are very close to your approved limit")
    elif perc_amount_vs_limit < 95:
        credit_score += 2
        warning.append("You are very close to your approved limit")
    else:
        return 0, warning
    
    # months since approval is the total number of EMI's
    months_since_approval = (today.year - customer_loan_data_df['date_of_approval'].dt.year) * 12 + (today.month - customer_loan_data_df['date_of_approval'].dt.month)
    perc_emi_paid_on_time = 0 if months_since_approval.sum() == 0 else (customer_loan_data_df['emis_paid_on_time'].sum()/months_since_approval.sum())*100
    if perc_emi_paid_on_time >= 120:
        credit_score += 30
    elif perc_emi_paid_on_time >= 100:
        credit_score += 26
    elif perc_emi_paid_on_time >= 90:
        credit_score += 22
    elif perc_emi_paid_on_time >= 80:
        credit_score += 18
    elif perc_emi_paid_on_time >= 70:
        credit_score += 15
    elif perc_emi_paid_on_time >= 60:
        credit_score += 12
    elif perc_emi_paid_on_time >= 50:
        credit_score += 8
        warning.append("You have not paid over 50% EMI's on time. Start paying your EMI's on time")
    elif perc_emi_paid_on_time >= 30:
        warning.append("You have not paid over 70% EMI's on time. Start paying your EMI's on time")
        credit_score += 4
    elif perc_emi_paid_on_time >= 20:
        warning.append("You have not paid over 80% EMI's on time. Start paying your EMI's on time")
        credit_score += 2
    else:
        warning.append(f"You have not paid over {(100-perc_emi_paid_on_time) if perc_emi_paid_on_time else 100}% EMI's on time. Start paying your EMI's on time")
        
    # the average tenure of all loans in years
    avg_tenures = (customer_loan_data_df['tenure'].mean()) / 12
    if avg_tenures >= 15:
        credit_score += 15
    elif avg_tenures >= 10:
        credit_score += 12
    elif avg_tenures >= 8:
        credit_score += 8
    elif avg_tenures >= 6:
        credit_score += 6
    elif avg_tenures >= 4:
        credit_score += 4
    elif avg_tenures >= 2:
        credit_score += 2
    else:
        credit_score += 1
    
    oldest_loan_year = customer_loan_data_df['date_of_approval'].min().year
    if oldest_loan_year <= 2010:
        credit_score += 10
    elif oldest_loan_year < 2014:
        credit_score += 8
    elif oldest_loan_year < 2016:
        credit_score += 5
    elif oldest_loan_year < 2020:
        credit_score += 2
        
    number_of_loans_taken = len(customer_loan_data_df)
    if number_of_loans_taken > 15:
        credit_score += 20
    elif number_of_loans_taken >= 10:
        credit_score += 15
    elif number_of_loans_taken >= 6:
        credit_score += 12
    elif number_of_loans_taken >= 2:
        credit_score += 8
    else:
        credit_score += 2
    
    return credit_score, warning

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    monthly_interest_rate = interest_rate / 12 / 100
    total_months = tenure
    monthly_installment = (loan_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -total_months)

    return monthly_installment

def emis_exceed_limit(customer_data, customer_loan_data, current_loan_installment):
    customer_loan_data_df = pd.DataFrame.from_records(customer_loan_data)
    customer_data_df = pd.DataFrame.from_records(customer_data)
    
    customer_loan_data_df['end_date'] = pd.to_datetime(customer_loan_data_df['end_date'])
    customer_active_loans = customer_loan_data_df[customer_loan_data_df['end_date'] > today]
    
    monthly_salary = customer_data_df.iloc[0]['monthly_salary']
    sum_of_current_emis = customer_active_loans['monthly_payment'].sum()

    return (sum_of_current_emis+current_loan_installment) > (monthly_salary * 0.5)

def get_eligibility(credit_score, interest_rate):
    rejected_reason = []
    
    approval=True
    
    if credit_score > 50:
        corrected_interest_rate = interest_rate
        approval = True
    elif 30 < credit_score <= 50:
        if interest_rate < 12:
            approval = False
            rejected_reason.append("You are only eligible for interest rates above 12%")
        corrected_interest_rate = max(interest_rate, 12)
    elif 10 < credit_score <= 30:
        if interest_rate < 16:
            approval = False
            rejected_reason.append("You are only eligible for interest rates above 16%")
        corrected_interest_rate = max(interest_rate, 16)
    else:
        approval = False
        rejected_reason.append("Your credit score is too low.")
        corrected_interest_rate = None
        
    return approval, corrected_interest_rate, rejected_reason