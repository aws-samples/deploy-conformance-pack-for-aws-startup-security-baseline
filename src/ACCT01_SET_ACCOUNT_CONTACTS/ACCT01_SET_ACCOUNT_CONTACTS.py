from rdklib import Evaluator, Evaluation, ConfigRule, ComplianceType

class ACCT01_SET_ACCOUNT_CONTACTS(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        ###############################
        # Add your custom logic here. #
        ###############################

        return [Evaluation(ComplianceType.NOT_APPLICABLE)]

    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        resource_id = event["accountId"]
        resource_type = "AWS::::Account"
        client = client_factory.build_client('account')
        contact_types = ['BILLING', 'OPERATIONS', 'SECURITY'] # need to make this configuration 
        result = dict()
        for contact in contact_types:
            try:
                client.get_alternate_contact(AlternateContactType=contact)
                result[contact] = True
            except client.exceptions.ResourceNotFoundException:
                result[contact] = False
        missing_alternative_contacts = [x for x in result if not result[x]]
        if missing_alternative_contacts:
            return [Evaluation(ComplianceType.NON_COMPLIANT, 
                               resourceId=resource_id, 
                               resourceType=resource_type,
                               annotation="Alternative account contacts missing")]
        else:
            return [Evaluation(ComplianceType.COMPLIANT, 
                               resourceId=resource_id, 
                               resourceType=resource_type,
                               annotation="Alternative account contacts configured")]

    def evaluate_parameters(self, rule_parameters):
        valid_rule_parameters = rule_parameters
        return valid_rule_parameters


################################
# DO NOT MODIFY ANYTHING BELOW #
################################
def lambda_handler(event, context):
    my_rule = ACCT01_SET_ACCOUNT_CONTACTS()
    evaluator = Evaluator(my_rule)
    return evaluator.handle(event, context)
