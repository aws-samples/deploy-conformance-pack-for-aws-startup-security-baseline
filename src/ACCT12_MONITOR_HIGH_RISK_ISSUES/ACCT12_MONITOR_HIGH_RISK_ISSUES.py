from rdklib import Evaluator, Evaluation, ConfigRule, ComplianceType
import botocore


class ACCT12_MONITOR_HIGH_RISK_ISSUES(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        ###############################
        # Add your custom logic here. #
        ###############################

        return [Evaluation(ComplianceType.NOT_APPLICABLE)]

    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        resource_id = event["accountId"]
        resource_type = "AWS::::Account"
        client = client_factory.build_client('support', region='us-east-1')
        try:
            ta_checks = client.describe_trusted_advisor_checks(language='en')
            ta_check_ids = [x['id'] for x in ta_checks['checks']]
            client.describe_trusted_advisor_check_refresh_statuses(checkIds=ta_check_ids)
            check_summaries = client.describe_trusted_advisor_check_summaries(checkIds=ta_check_ids)
            errors = [x for x in check_summaries['summaries'] if x['status'] == 'error']
        except botocore.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "SubscriptionRequiredException":
                errors = None
        if errors:
            return [Evaluation(ComplianceType.NON_COMPLIANT,
                               resourceId=resource_id,
                               resourceType=resource_type,
                               annotation="Check Trusted Advisor")]
        elif errors is None:
            return [Evaluation(ComplianceType.NOT_APPLICABLE,
                               resourceId=resource_id,
                               resourceType=resource_type,
                               annotation="AWS Premium Support Subscription required")]
        else:
            return [Evaluation(ComplianceType.COMPLIANT,
                               resourceId=resource_id,
                               resourceType=resource_type,
                               annotation="No Trusted Advisor issues")]

    def evaluate_parameters(self, rule_parameters):
        valid_rule_parameters = rule_parameters
        return valid_rule_parameters


################################
# DO NOT MODIFY ANYTHING BELOW #
################################
def lambda_handler(event, context):
    my_rule = ACCT12_MONITOR_HIGH_RISK_ISSUES()
    evaluator = Evaluator(my_rule)
    return evaluator.handle(event, context)
