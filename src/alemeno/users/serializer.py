from rest_framework import serializers
from users.models import Customer, LoanData

class CustomerSerializer(serializers.ModelSerializer):
    approved_limit = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ('customer_id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_salary', 'approved_limit')
    
    def validate_phone_number(self, value):
        if Customer.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A customer with this phone number already exists.")
        return value

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanData
        felds = ('customer_id', 'loan_id', 'loan_amount', 'tenure', 'interest_rate', 'monthly_payment', 'emis_paid_on_time', 'date_of_approval', 'end_date')
