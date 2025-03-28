from rdklib import Evaluator, Evaluation, ConfigRule, ComplianceType
import json


def check_ssm_permissions(iam_client, role_name):
    try:
        attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']

        for policy in attached_policies:
            policy_arn = policy['PolicyArn']

            if policy_arn == "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore":
                return True
    except Exception as e:
        print(f"Error checking permissions for role {role_name}: {str(e)}")

    return False


class WKL06_USE_SYSTEMS_MANAGER_INSTEAD_OF_SSH_OR_RDP(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        invoking_event = json.loads(event['invokingEvent'])
        resource_id = invoking_event['configurationItem']['resourceId']
        resource_type = "AWS::EC2::Instance"
        base_client = client_factory.build_client('ec2')
        iam_base_client = client_factory.build_client('iam')

        try:
            # Get Instance details
            response = base_client.describe_instances(InstanceIds=[resource_id])
            instance = response['Reservations'][0]['Instances'][0]
        except base_client.exceptions.NoSuchEntityException:
            return [Evaluation(ComplianceType.NON_COMPLIANT,
                               resourceId=resource_id,
                               resourceType=resource_type,
                               annotation=f"Unable to fetch Instance Details")]
        # check if instance has profile attached
        if 'IamInstanceProfile' in instance:
            profile_arn = instance['IamInstanceProfile']['Arn']
            profile_id = profile_arn.split('/')[-1]
            try:
                instance_profile = iam_base_client.get_instance_profile(InstanceProfileName=profile_id)
                if 'Roles' in instance_profile['InstanceProfile'] and instance_profile['InstanceProfile'][
                    'Roles']:
                    iam_role = instance_profile['InstanceProfile']['Roles'][0]['RoleName']
                    if not check_ssm_permissions(iam_base_client, iam_role):
                        return [Evaluation(ComplianceType.NON_COMPLIANT,
                                           resourceId=instance['InstanceId'],
                                           resourceType=resource_type,
                                           annotation=f"EC2 instance does not have the permissions to connect to ssm manager")]
                    else:
                        return [Evaluation(ComplianceType.COMPLIANT,
                                           resourceId=instance['InstanceId'],
                                           resourceType=resource_type,
                                           annotation=f"EC2 Instance Profile exists and has the permissions to be managed by SSM")]
            except iam_base_client.exceptions.NoSuchEntityException:
                return [Evaluation(ComplianceType.NON_COMPLIANT,
                                   resourceId=instance['InstanceId'],
                                   resourceType=resource_type,
                                   annotation=f"EC2 Instance profile exists, but unable to fetch role details")]

        return [Evaluation(ComplianceType.NON_COMPLIANT,
                           resourceId=instance['InstanceId'],
                           resourceType=resource_type,
                           annotation=f"EC2 instance does not have a role Attached")]

    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        ###############################
        # Add your custom logic here. #
        ###############################

        return [Evaluation(ComplianceType.NOT_APPLICABLE)]

    def evaluate_parameters(self, rule_parameters):
        valid_rule_parameters = rule_parameters
        return valid_rule_parameters


################################
# DO NOT MODIFY ANYTHING BELOW #
################################
def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event, indent=4, sort_keys=True)}")
    my_rule = WKL06_USE_SYSTEMS_MANAGER_INSTEAD_OF_SSH_OR_RDP()
    evaluator = Evaluator(my_rule, expected_resource_types="AWS::EC2::Instance")
    return evaluator.handle(event, context)
