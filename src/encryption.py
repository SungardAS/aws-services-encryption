
import boto3
import json
from base64 import b64encode, b64decode
import traceback

def put_job_success(job, message):
    """Notify CodePipeline of a successful job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_success_result()

    """
    print('Putting job success')
    print(message)
    boto3.client('codepipeline').put_job_success_result(jobId=job)


def put_job_failure(job, message):
    """Notify CodePipeline of a failed job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_failure_result()

    """
    print('Putting job failure')
    print(message)
    boto3.client('codepipeline').put_job_failure_result(jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})


def encrypt_secret_env_vars(stack_name):

    # find stack template
    stack_response = boto3.client('cloudformation').get_template(
        StackName=stack_name
    )

    # find secret parameters
    params = stack_response['TemplateBody'].get('Parameters')
    secret_params = None
    if params:
        secret_params = [key for key in params.keys() if params[key].get('NoEcho')]
    print("Secret parameters are '%s'" % secret_params)

    # find lambda function names
    stack_resources = stack_response['TemplateBody'].get('Resources')
    lambda_functions = [key for key in stack_resources.keys() if stack_resources[key]['Type']=='AWS::Lambda::Function']

    # find lambda function with secret env variables
    functions_with_secret = []
    for function in lambda_functions:
        if 'Environment' not in stack_resources[function]['Properties']:    continue
        if 'Variables' not in stack_resources[function]['Properties']['Environment']:   continue
        env_vars = stack_resources[function]['Properties']['Environment']['Variables']
        secret_vars = [key for key in env_vars.keys() if 'Ref' in env_vars[key] and env_vars[key]['Ref'] in secret_params]
        if len(secret_vars) > 0:
            functions_with_secret.append({function: secret_vars})
        # [{u'LambdaFunction': [u'SSO_MASTER_TOKEN', u'SSO_BASIC_AUTH_PASSWORD']}]

    print("Functions with secret params : %s" % functions_with_secret)

    if len(functions_with_secret) == 0: return

    for secret_function in functions_with_secret:

        resource_response = boto3.client('cloudformation').describe_stack_resource(
            StackName=stack_name,
            LogicalResourceId=secret_function.keys()[0]
        )
        function_name = resource_response['StackResourceDetail']['PhysicalResourceId']
        print("Found a function with secret params : %s" % function_name)

        lambda_response = boto3.client('lambda').get_function_configuration(
            FunctionName=function_name
        )

        """if 'KMSKeyArn' in lambda_response:
            print("Env variables of function, '%s' are already encoded" % function_name)
            continue"""

        if 'Environment' not in lambda_response:    continue
        if 'Variables' not in lambda_response['Environment']:   continue

        # encrypt secret variables
        env_vars = lambda_response['Environment']['Variables']
        #print(env_vars)
        for key in env_vars.keys():
            if key not in secret_function[secret_function.keys()[0]]:    continue

            try:
                encrypted = b64decode(env_vars[key])
                # the value was already encrypted, so re-encrypt
                kms_response = boto3.client('kms').re_encrypt(
                    CiphertextBlob=b64decode(env_vars[key]),
                    DestinationKeyId=env_vars['KMS_KEY_ID']
                )
            except:
                # the value was not encrypted, so just encrypt
                kms_response = boto3.client('kms').encrypt(
                    KeyId=env_vars['KMS_KEY_ID'],
                    Plaintext=env_vars[key]
                )

            env_vars[key] = b64encode(kms_response['CiphertextBlob'])

        print(env_vars)

        # update env variables of the target Lambda Function
        update_response = boto3.client('lambda').update_function_configuration(
            FunctionName=function_name,
            Environment={'Variables': env_vars},
            #KMSKeyArn=env_vars['KMS_KEY_ARN']
        )
        print("Successfully encrypted env variables of function, '%s'" % function_name)


def lambda_handler(event, context):

    print(event)

    # Extract the Job ID
    job_id = event['CodePipeline.job']['id']

    # Extract the Job Data
    job_data = event['CodePipeline.job']['data']

    # Extract the params
    user_parameters = job_data['actionConfiguration']['configuration']['UserParameters']
    decoded_parameters = json.loads(user_parameters)

    stack_name = decoded_parameters['stack_name']
    print("stack_name: " + stack_name)

    try:
        encrypt_secret_env_vars(stack_name)
        put_job_success(job_id, "Successfully encrypted env variables of all functions")
    except Exception, ex:
        # If any other exceptions which we didn't expect are raised
        # then fail the job and log the exception message.
        print('Function failed due to exception.')
        print(ex)
        traceback.print_exc()
        put_job_failure(job_id, 'Function exception: ' + str(ex))

    return "Complete."
