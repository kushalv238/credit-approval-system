from rest_framework.decorators import api_view
from rest_framework import status

from django.http import JsonResponse

from dateutil.relativedelta import relativedelta

from math import floor
import random

from users.models import Customer, LoanData
from users.serializer import CustomerSerializer
from users.utils import *

# /api/v1/register/
@api_view(['POST'])
def register_customer(request):
    serializer = CustomerSerializer(data=request.data)

    if serializer.is_valid():
        if serializer.validated_data['age'] < 18:
            return JsonResponse({'message': 'Age must be at least 18'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.validated_data['phone_number'] < 1000000000 or serializer.validated_data['phone_number'] > 9999999999:
            return JsonResponse({'message': 'Phone number must be a 10-digit number'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.validated_data['monthly_salary'] < 0:
            return JsonResponse({'message': 'Monthly salary cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)

        monthly_salary = serializer.validated_data['monthly_salary']
        approved_limit = floor(36 * monthly_salary / 100000) * 100000
        serializer.validated_data['approved_limit'] = approved_limit

        serializer.save()

        return JsonResponse(
            {
                'data':
                {
                    'customer_id': serializer.instance.customer_id,
                    'name': serializer.validated_data['first_name'] + " " + serializer.validated_data['last_name'],
                    'age': serializer.validated_data['age'],
                    'monthly_income': serializer.validated_data['monthly_salary'],
                    'approved_limit': serializer.validated_data['approved_limit'],
                    'phone_number': serializer.validated_data['phone_number']
                },
                    'message': 'User added successfully!'
            },
            status=status.HTTP_201_CREATED
        )

    return JsonResponse({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
# /api/v1/check-eligibility/
@api_view(['POST'])
def check_eligibility(request):
    customer_id = request.data.get("customer_id")
    loan_amount = request.data.get("loan_amount")
    interest_rate = request.data.get("interest_rate")
    tenure = request.data.get("tenure")

    if not all([customer_id, loan_amount, interest_rate, tenure]):
        return JsonResponse({'message': "Missing required data"}, status=status.HTTP_400_BAD_REQUEST)

    customer_data = Customer.objects.filter(customer_id=customer_id).values()
    if not customer_data.exists():
        return JsonResponse({'message': "No such user exists"}, status=status.HTTP_404_NOT_FOUND)

    loan_data = LoanData.objects.filter(customer_id=customer_id).values()
    if not loan_data.exists():
        return JsonResponse({'message': "User has no credit history"}, status=status.HTTP_404_NOT_FOUND)

    credit_score, warning = calculate_credit_score(customer_data, customer_loan_data=loan_data)
    
    approval, corrected_interest_rate, rejected_reason = get_eligibility(credit_score, interest_rate)
    
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
    
    if emis_exceed_limit(customer_data, customer_loan_data=loan_data, current_loan_installment=monthly_installment):
        rejected_reason.append("Sum of all your EMIs exceeds 50% of your monthly salary.")
        approval = False
    
    
    return JsonResponse(
        {
            'data': 
                {
                    "credit_score": credit_score,
                    "customer_id": customer_id,
                    "approval": approval,
                    "interest_rate": interest_rate,
                    "corrected_interest_rate": corrected_interest_rate,
                    "tenure": tenure,
                    "monthly_installment": monthly_installment,
                    "reason_for_reason": rejected_reason or None,
                    "warnings": warning
                },
            'message': "Eligible for loan" if approval else "Not Eligible for loan"
        },
        status = status.HTTP_200_OK if approval else status.HTTP_403_FORBIDDEN
    )

# /api/v1/create-loan/
@api_view(['POST'])
def create_loan(request):
    customer_id = request.data.get("customer_id")
    loan_amount = request.data.get("loan_amount")
    interest_rate = request.data.get("interest_rate")
    tenure = request.data.get("tenure")
    
    if not all([customer_id, loan_amount, interest_rate, tenure]):
        return JsonResponse({'message': "Missing required data"}, status=status.HTTP_400_BAD_REQUEST)
    
    customer_data = Customer.objects.filter(customer_id=customer_id).values()
    if not customer_data.exists():
        return JsonResponse({'message': "No such user exists"}, status=status.HTTP_404_NOT_FOUND)

    approval = True
    rejected_reason = []
    corrected_interest_rate = None
    
    loan_data = LoanData.objects.filter(customer_id=customer_id).values()
    
    if loan_data.exists():
        credit_score, _ = calculate_credit_score(customer_data, loan_data)
        approval, corrected_interest_rate, rejected_reason = get_eligibility(credit_score, interest_rate)
        
        monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
        
        if emis_exceed_limit(customer_data, customer_loan_data=loan_data, current_loan_installment=monthly_installment):
            rejected_reason.append("Sum of all your EMIs exceeds 50% of your monthly salary.")
            approval = False
    else:
        if loan_amount > 10_00_000:
            approval = False
            rejected_reason.append("Since you have no credit history, you are not eligible for loans exeeding amount 10,00,000.")
        
        if interest_rate < 12:
            approval = False
            rejected_reason.append("Since you have no credit history, you are not eligible for loans with Interest Rates less than 12%.")
        
    if approval:
        monthly_installment = calculate_monthly_installment(loan_amount, interest_rate, tenure) if approval else None
        # Save approved loan to database
        loan = LoanData.objects.create(
            customer_id=Customer.objects.get(customer_id=customer_id),
            loan_id=random.randint(1000, 10000),
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=corrected_interest_rate or interest_rate,
            monthly_payment=monthly_installment,
            emis_paid_on_time=0,
            date_of_approval=today,
            end_date=(today + relativedelta(months=tenure)).strftime('%Y-%m-%d')
        )
        loan_id = loan.id
    else:
        loan_id = None
    
    return JsonResponse(
        {
            'loan_data': {
                "loan_id": loan_id,
                "customer_id": customer_id,
                "loan_approved": approval,
                "message": rejected_reason,
                "monthly_installment": monthly_installment if approval else None
            },
            'message': "Loan created successfully" if approval else "Loan creation failed"
        },
        status=status.HTTP_200_OK
    )

# /api/v1/view-loan/
@api_view(["GET"])
def view_loan(_, loan_id):
    try:
        loan_data = LoanData.objects.get(id=loan_id)
    except LoanData.DoesNotExist:
        return JsonResponse({'message': "No such loan data"}, status=status.HTTP_404_NOT_FOUND)
    
    customer_data = loan_data.customer_id
    
    return JsonResponse(
        {
            "data": {
                "loanid": loan_id,
                "customer": {
                    "id": customer_data.customer_id,
                    "first_name": customer_data.first_name,
                    "last_name": customer_data.last_name,
                    "phone_number": customer_data.phone_number,
                    "age": customer_data.age
                },
                "loan_amount": loan_data.loan_amount,
                "interest_rate": loan_data.interest_rate,
                "monthly_installment": loan_data.monthly_payment,
                "tenure": loan_data.tenure
            },
            "message": "Loan data found"
        },
        status=status.HTTP_200_OK
    )

# /api/v1/view-loans/
@api_view(["GET"])
def view_loans(_, customer_id):
    loan_data = LoanData.objects.filter(customer_id=customer_id).values()
    if not loan_data.exists():
        return JsonResponse({'message': "User has no loan history"}, status=status.HTTP_404_NOT_FOUND)
    
    loans = []
    for loan in loan_data:
        date_of_approval = loan['date_of_approval']
        tenure = loan['tenure']
        today = datetime.now().date()
        
        months_diff = (today.year - date_of_approval.year) * 12 + today.month - date_of_approval.month
        
        repayments_left = tenure - months_diff


        loans.append({
            "id": loan['id'],
            "loan_id": loan['loan_id'],
            "loan_amount": loan['loan_amount'],
            "interest_rate": float(loan['interest_rate']),
            "monthly_installment": float(loan['monthly_payment']),
            "repayments_left": repayments_left if repayments_left > 0 else 0
        })
    
    return JsonResponse(
        {
            'no_of_loans': len(loans),
            'loan_data': loans,
            'message': 'Loans data found',
        },
        status=status.HTTP_200_OK
    )
