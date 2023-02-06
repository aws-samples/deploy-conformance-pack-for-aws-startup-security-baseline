from aws_cdk import Aspects, Aws, Stack
from aws_cdk import aws_config as config
from aws_cdk import aws_lambda as lambda_, Duration
from aws_cdk import aws_iam as iam
from constructs import Construct
import yaml
from cdk_nag import AwsSolutionsChecks, NagSuppressions, NagPackSuppression

class Rules(Stack):

    def __init__(self, scope: Construct, construct_id: str, 
                 lambda_layer_arn: str,
                 lambda_functions: list, 
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        rdklib_layer = lambda_.LayerVersion.from_layer_version_attributes(self, 
                                "rdklib_layer", 
                                layer_version_arn=lambda_layer_arn)
        
        config_role = iam.Role.from_role_name(self,'config-role', role_name='config-role')
        
        trusted_advisor_policy = iam.Policy(self, "trusted_advisor_policy",
                                         policy_name="read_only_trusted_advisor_support_policy",
                                         statements=[iam.PolicyStatement(
                                            resources=["*"],
                                            actions=["support:DescribeTrustedAdvisorChecks",
                                                    "support:DescribeTrustedAdvisorCheckSummaries",
                                                    "support:DescribeTrustedAdvisorCheckRefreshStatuses"],
                                            effect=iam.Effect.ALLOW
                                         )])
        config_role.attach_inline_policy(trusted_advisor_policy)
        
        NagSuppressions.add_resource_suppressions(
            construct= trusted_advisor_policy,
            suppressions= [
                NagPackSuppression(
                    id = 'AwsSolutions-IAM5',
                    reason = """
                         AWS Support does not support specifying a resource ARN in the Resource 
                         element of an IAM policy statement. To allow access to AWS Support, 
                         specify "Resource": "*" in your policy.
                         https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssupport.html#awssupport-resources-for-iam-policies
                    """
                )
            ]
        )
            
        # Create Execution Role for Confirmance Pack custom lambdas
        for function in lambda_functions:
            execution_role = iam.Role(self, f"{function}-lambda-execution-role",
                role_name=f"{function}-lambda-execution-role",
                assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
            )
            basic_lambda_execution = iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
            execution_role.add_managed_policy(basic_lambda_execution)
            execution_role.add_to_policy(iam.PolicyStatement(
                resources=[f"arn:aws:iam::{Aws.ACCOUNT_ID}:role/rdk/config-role"],
                actions=["sts:AssumeRole"],
                effect=iam.Effect.ALLOW
            ))
            NagSuppressions.add_resource_suppressions(
                construct= execution_role,
                suppressions= [
                    NagPackSuppression(
                        id = 'AwsSolutions-IAM4',
                        reason = """
                            Each Lambda function uses the service-linked AWS managed policy for basic Lambda execution.
                            This managed policy only provides permission for log group logging of the 
                            Lambda executions.
                        """
                    )
                ]
            )

            handler = lambda_.Function(self, function,
                        function_name=function,
                        runtime=lambda_.Runtime.PYTHON_3_9,
                        code=lambda_.Code.from_asset(f"out/{function}.zip"),
                        handler=f"{function}.lambda_handler",
                        layers=[rdklib_layer],
                        role=execution_role,
                        timeout=Duration.seconds(30)
            )

            rule = config.CustomRule(self, f"{function}-rule",
                config_rule_name=function,
                lambda_function=handler,
                configuration_changes=False,
                periodic=True,
                maximum_execution_frequency=config.MaximumExecutionFrequency.TWENTY_FOUR_HOURS,
            )
            
            Aspects.of(self).add(AwsSolutionsChecks(verbose=True))
