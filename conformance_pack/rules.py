from aws_cdk import Aspects, Aws, Stack
from aws_cdk import aws_config as config
from aws_cdk import aws_lambda as lambda_, Duration
from aws_cdk import aws_iam as iam
from constructs import Construct
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

        config_role = iam.Role.from_role_name(self, 'config-role', role_name='config-role')

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
            construct=trusted_advisor_policy,
            suppressions=[
                NagPackSuppression(
                    id='AwsSolutions-IAM5',
                    reason="""
                    AWS Support does not support specifying a resource ARN in the Resource 
                         element of an IAM policy statement. To allow access to AWS Support, 
                         specify "Resource": "*" in your policy.
                         https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssupport.html#awssupport-resources-for-iam-policies
                         """
                )
            ]
        )

        # Create Execution Role for Conformance Pack custom lambdas
        for function in lambda_functions:
            # make sure the role name is less than 64 characters
            if len(function) > 30:
                role_name_prefix = function[:30]

            else:
                role_name_prefix = function
            execution_role = iam.Role(self, f"{role_name_prefix}-lambda-execution-role",
                                      role_name=f"{role_name_prefix}-{Aws.REGION}-lambda-execution-role",
                                      assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
                                      )
            # basic_lambda_execution = iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
            # execution_role.add_managed_policy(basic_lambda_execution)

            # Add minimal CloudWatch Logs permissions to publish to the Lambda function's log group
            push_logs_policy = iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[
                    f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/lambda/{function}:*"
                ]
            )
            execution_role.add_to_policy(push_logs_policy)

            NagSuppressions.add_resource_suppressions(
                construct=execution_role,
                suppressions=[
                    NagPackSuppression(
                        id='AwsSolutions-IAM5',
                        reason="Each Lambda function needs to push logs streams to aws Cloudwatch logs. The logs treams names are dynamic, hence the *"
                    )
                ],
                apply_to_children=True
            )

            # Add minimal CloudWatch Logs permissions to create the log group
            execution_role.add_to_policy(iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/lambda/{function}"]
            ))

            execution_role.add_to_policy(iam.PolicyStatement(
                resources=[f"arn:aws:iam::{Aws.ACCOUNT_ID}:role/rdk/config-role"],
                actions=["sts:AssumeRole"],
                effect=iam.Effect.ALLOW
            ))
            NagSuppressions.add_resource_suppressions(
                construct=execution_role,
                suppressions=[
                    NagPackSuppression(
                        id='AwsSolutions-IAM4',
                        reason="Each Lambda function uses the service-linked AWS managed policy for basic Lambda execution. This managed policy only provides permission for log group logging of the Lambda executions."
                    )
                ]
            )

            lamda_runtime = lambda_.Runtime('python3.12')
            handler = lambda_.Function(self, function,
                                       function_name=function,
                                       runtime=lamda_runtime,
                                       code=lambda_.Code.from_asset(f"out/{function}.zip"),
                                       handler=f"{function}.lambda_handler",
                                       layers=[rdklib_layer],
                                       role=execution_role,
                                       timeout=Duration.seconds(30)
                                       )

            NagSuppressions.add_resource_suppressions(
                construct=handler,
                suppressions=[
                    NagPackSuppression(
                        id='AwsSolutions-L1',
                        reason="at this time, the rdklib-layer only supports the following python versions python3.7, python3.8, python3.9, python3.10, python3.11, python3.12"
                    )
                ]
            )

            rule = config.CustomRule(self, f"{function}-rule",
                                     config_rule_name=function,
                                     lambda_function=handler,
                                     configuration_changes=False,
                                     periodic=True,
                                     maximum_execution_frequency=config.MaximumExecutionFrequency.TWENTY_FOUR_HOURS,
                                     )
            Aspects.of(self).add(AwsSolutionsChecks(verbose=True))
