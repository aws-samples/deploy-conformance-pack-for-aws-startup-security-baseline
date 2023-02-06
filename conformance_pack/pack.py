from aws_cdk import Aspects, Stack
from aws_cdk import aws_config as config
from constructs import Construct
from conformance_pack.lib.helper import render_template
from cdk_nag import AwsSolutionsChecks
import yaml

class Pack(Stack):

    def __init__(self, scope: Construct, construct_id: str,  
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open(f'conformance_pack/rules/account_rules.yaml') as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)

        conformance_pack = config.CfnConformancePack(self, data['conformance_pack']['name'],
            conformance_pack_name=data['conformance_pack']['name'],
            template_body=render_template(data)
        )
        
        Aspects.of(self).add(AwsSolutionsChecks(verbose=True))