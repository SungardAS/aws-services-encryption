
import sys
sys.path.insert(0, r"../src")

from encryption import lambda_handler
context = None
event = {
    "stack_name": "aws-services-authorizer"
}
lambda_handler(event, context)
