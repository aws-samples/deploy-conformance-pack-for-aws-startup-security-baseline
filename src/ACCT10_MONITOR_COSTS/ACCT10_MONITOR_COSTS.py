from rdklib import Evaluator, Evaluation, ConfigRule, ComplianceType


class ACCT10_MONITOR_COSTS(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        ###############################
        # Add your custom logic here. #
        ###############################

        return [Evaluation(ComplianceType.NOT_APPLICABLE)]

    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        resource_id = event["accountId"]
        resource_type = "AWS::::Account"
        client = client_factory.build_client('budgets')
        budgets = client.describe_budgets(AccountId=resource_id)
        if not 'Budgets' in budgets:
            return [Evaluation(ComplianceType.NON_COMPLIANT,
                               resourceId=resource_id,
                               resourceType=resource_type,
                               annotation="No AWS Budgets set")]
        else:
            return [Evaluation(ComplianceType.COMPLIANT,
                               resourceId=resource_id,
                               resourceType=resource_type,
                               annotation="At least one AWS Budget set")]

    def evaluate_parameters(self, rule_parameters):
        valid_rule_parameters = rule_parameters
        return valid_rule_parameters


################################
# DO NOT MODIFY ANYTHING BELOW #
################################
def lambda_handler(event, context):
    my_rule = ACCT10_MONITOR_COSTS()
    evaluator = Evaluator(my_rule)
    return evaluator.handle(event, context)
