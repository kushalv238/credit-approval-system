# Credit Approval System

This project is a credit approval system that determines loan eligibility based on past loan data. It includes APIs for adding new customers, checking loan eligibility, processing new loans, and viewing loan details.

## Features

- Add a new customer to the customer table
- Check loan eligibility based on credit score
- Process a new loan based on eligibility
- View loan details and customer details
- View all current loan details by customer ID

## Technologies Used

- Django
- PostgreSQL
- Docker
- Docker Compose

## API Endpoints

All APIs run under `/api/v1/`:
1. `/register/`: Add a new customer
2. `/check-eligibility/`: Check loan eligibility based on credit score
3. `/create-loan/`: Process a new loan based on eligibility
4. `/view-loan/loan_id/`: View loan details and customer details by loan ID
5. `/view-loans/customer_id/`: View all current loan details by customer ID

Note: Make sure to add a slash ('/') at the end of the API.

## Pre-requisites

- python
- docker
- Docker Desktop
- docker-compose

## Running the Application

>Clone this project
```bash
git clone https://github.com/kushalv238/credit_approval_system.git
```
>Navigate to the project directory
```bash
cd credit_approval_system
```
>Start the Docker engine by starting the Docker Desktop or by using [OS utilities](https://docs.docker.com/config/daemon/start/)

>Run Docker Compose
```bash
docker-compose up
```
>Access the APIs at
```bash
http://localhost:8000/api/v1/
```

## Testing the project
Use this Postman collection with existing APIs to test the project

[Collection](https://www.postman.com/telecoms-geologist-66457404/workspace/open/collection/26309885-7d351ebb-b7c9-4ee6-8447-239e59c549bc)

Note: Change the agent to [desktop agent](https://www.postman.com/downloads/postman-agent/) if you run Postman on a browser. The option can be found on the bottom right.

## Author
[Kushal Vadodaria](https://github.com/kushalv238)
