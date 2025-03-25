from rdklib import Evaluator, Evaluation, ConfigRule, ComplianceType


class WK12_USE_VPC_ENDPOINTS_TO_ACCESS_SUPPORTED_SERVICES(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        ###############################
        # Add your custom logic here. #
        ###############################

        return [Evaluation(ComplianceType.NOT_APPLICABLE)]

    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):

        resource_id = event["accountId"]
        resource_type = "AWS::::Account"
        base_client = client_factory.build_client('ec2')

        # find all active regions
        active_regions = [region['RegionName'] for region in base_client.describe_regions()['Regions']]

        # find VPC with existing resources
        vpcs_with_resources = []
        for region in active_regions:
            # Get all VPCs in the region
            client = client_factory.build_client('ec2', region=region)
            vpcs = client.describe_vpcs()['Vpcs']
            for vpc in vpcs:
                vpc_id = vpc['VpcId']

                # Check for EC2 instances
                instances = base_client.describe_instances(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
                if instances['Reservations']:
                    endpoints = client.describe_vpc_endpoints(
                        Filters=[{'Name': 'service-name', 'Values': [f'com.amazonaws.{region}.s3']}])
                    if len(endpoints['VpcEndpoints']) == 0:
                        return [Evaluation(ComplianceType.NON_COMPLIANT,
                                           resourceId=resource_id,
                                           resourceType=resource_type,
                                           annotation=f"S3 VPC endpoint(s) not configured while resources exist")]
        return [Evaluation(ComplianceType.COMPLIANT,
                           resourceId=resource_id,
                           resourceType=resource_type,
                           annotation=f"S3 VPC Endpoint(s) not configured while resources exist")]

    def evaluate_parameters(self, rule_parameters):
        valid_rule_parameters = rule_parameters
        return valid_rule_parameters


################################
# DO NOT MODIFY ANYTHING BELOW #
################################
def lambda_handler(event, context):
    my_rule = WK12_USE_VPC_ENDPOINTS_TO_ACCESS_SUPPORTED_SERVICES()
    evaluator = Evaluator(my_rule)
    return evaluator.handle(event, context)
