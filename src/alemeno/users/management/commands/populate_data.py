import csv
from django.core.management.base import BaseCommand
from users.models import Customer, LoanData

from datetime import datetime

class Command(BaseCommand):
    help = 'Populate the database with existing data'

    def add_arguments(self, parser):
        parser.add_argument('customer_csv', type=str, help='Path to the customer CSV file')
        parser.add_argument('loan_csv', type=str, help='Path to the loan CSV file')

    def handle(self, *args, **kwargs):
        customer_csv = kwargs['customer_csv']
        loan_csv = kwargs['loan_csv']

        if not Customer.objects.exists():
            with open(customer_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    Customer.objects.create(
                        first_name=row['First Name'],
                        last_name=row['Last Name'],
                        age=row['Age'],
                        phone_number=row['Phone Number'],
                        monthly_salary=row['Monthly Salary'],
                        approved_limit=row['Approved Limit'],
                    )
            print("Initial Customer data populated")

        if not LoanData.objects.exists():
            with open(loan_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    customer_data = Customer.objects.get(customer_id=row['Customer ID'])
                    LoanData.objects.create(
                        customer_id=customer_data,
                        loan_id=row['Loan ID'],
                        loan_amount=row['Loan Amount'],
                        tenure=row['Tenure'],
                        interest_rate=row['Interest Rate'],
                        monthly_payment=row['Monthly payment'],
                        emis_paid_on_time=row['EMIs paid on Time'],
                        date_of_approval=datetime.strptime(row['Date of Approval'], "%m/%d/%Y").strftime("%Y-%m-%d"),
                        end_date=datetime.strptime(row['End Date'], "%m/%d/%Y").strftime("%Y-%m-%d"),
                    )
            print("Initial Loan data populated")
            