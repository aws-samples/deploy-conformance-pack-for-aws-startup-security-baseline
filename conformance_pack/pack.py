from aws_cdk import Aspects, Stack
from aws_cdk import aws_config as config
from constructs import Construct
from conformance_pack.lib.helper import render_template
from conformance_pack.lib.helper import localise_rules_stack
from cdk_nag import AwsSolutionsChecks
import yaml


class Pack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load account rules
        with open(f'conformance_pack/rules/account_rules.yaml') as f:
            account_data = yaml.load(f, Loader=yaml.SafeLoader)
        # Load workload rules
        with open(f'conformance_pack/rules/workload_rules.yaml') as f:
            workload_data = yaml.load(f, Loader=yaml.SafeLoader)

        # create a single conformance pack config for workload and account rules
        data = account_data
        # Add the resources from workload_data
        data['conformance_pack']['rules'] += workload_data['conformance_pack']['rules']
        # for i in workload_data['conformance_pack']['rules']:
        #     data['conformance_pack']['rules'].update({i: workload_data['conformance_pack']['rules'][i]})
        conformance_pack_name = data['conformance_pack']['name']
        localized_data = localise_rules_stack(data)
        template_body = render_template(localized_data)

        conformance_pack = config.CfnConformancePack(self, data['conformance_pack']['name'],
                                                     conformance_pack_name=conformance_pack_name,
                                                     template_body=template_body
                                                     )

        Aspects.of(self).add(AwsSolutionsChecks(verbose=True))
