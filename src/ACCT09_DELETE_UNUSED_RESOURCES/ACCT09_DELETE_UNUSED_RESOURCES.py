from rdklib import Evaluator, Evaluation, ConfigRule, ComplianceType


class ACCT09_DELETE_UNUSED_RESOURCES(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        ###############################
        # Add your custom logic here. #
        ###############################

        return [Evaluation(ComplianceType.NOT_APPLICABLE)]

    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        resource_id = event["accountId"]
        resource_type = "AWS::::Account"
        base_client = client_factory.build_client('ec2')
        vpc_with_default = list()
        regions = [x['RegionName'] for x in base_client.describe_regions()['Regions']]
        for region in regions:
            client = client_factory.build_client('ec2', region=region)
            vpcs = client.describe_vpcs()
            for vpc in vpcs['Vpcs']:
                if vpc['IsDefault']:
                    vpc_with_default.append(region)
        if vpc_with_default:
            return [Evaluation(ComplianceType.NON_COMPLIANT,
                               resourceId=resource_id,
                               resourceType=resource_type,
                               annotation=f"Default VPCs active in account")]
        else:
            return [Evaluation(ComplianceType.COMPLIANT,
                               resourceId=resource_id,
                               resourceType=resource_type,
                               annotation=f"No Default VPCs active")]

    def evaluate_parameters(self, rule_parameters):
        valid_rule_parameters = rule_parameters
        return valid_rule_parameters


################################
# DO NOT MODIFY ANYTHING BELOW #
################################
def lambda_handler(event, context):
    my_rule = ACCT09_DELETE_UNUSED_RESOURCES()
    evaluator = Evaluator(my_rule)
    return evaluator.handle(event, context)
