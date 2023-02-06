import boto3
import shutil
from os import listdir

def get_lambda_layer_version(AWS_PROFILE=False):
    if AWS_PROFILE:
        session = boto3.Session(profile_name=AWS_PROFILE)
        cf_client = session.client('cloudformation')
    else:
        cf_client = boto3.client('cloudformation')
    try:    
        outputs = cf_client.describe_stacks(StackName='serverlessrepo-rdklib')['Stacks'][0]['Outputs']
        return [x['OutputValue'] for x in outputs if x['OutputKey'] == 'RdklibLayerArn'][0]
    except:
        return False

def build_lambda():
    functions = listdir('src')
    for function in functions:
        shutil.make_archive(f"out/{function}", 'zip', f"src/{function}")
    return functions