from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True, db_column='Customer ID')
    first_name = models.CharField(max_length=100, db_column='First Name')
    last_name = models.CharField(max_length=100, db_column='Last Name')
    age = models.IntegerField(db_column='Age')
    phone_number = models.BigIntegerField(db_column='Phone Number')
    monthly_salary = models.IntegerField(db_column='Monthly Salary')
    approved_limit = models.IntegerField(db_column='Approved Limit')

    class Meta:
        db_table = 'customer_data'


class LoanData(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='Customer ID')
    loan_id = models.IntegerField(db_column='Loan ID')
    loan_amount = models.IntegerField(db_column='Loan Amount')
    tenure = models.IntegerField(db_column='Tenure')
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, db_column='Interest Rate')
    monthly_payment = models.IntegerField(db_column='Monthly Payment')
    emis_paid_on_time = models.IntegerField(db_column='EMIs paid on Time')
    date_of_approval = models.DateField(db_column='Date of Approval')
    end_date = models.DateField(db_column='End Date')

    class Meta:
        db_table = 'loan_data'
