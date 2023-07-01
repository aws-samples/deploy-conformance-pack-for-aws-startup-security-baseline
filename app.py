#!/usr/bin/env python3
import boto3
import aws_cdk as cdk
from aws_cdk import Aspects
from conformance_pack.rules import Rules
from conformance_pack.pack import Pack
import conformance_pack.lib.prepare as prepare
import os
from cdk_nag import AwsSolutionsChecks
import sys


if os.environ.get('CI_TRUE'):
    lambda_layer_arn = 'arn::aws:CI_TEST_ARN'
else:
    AWS_PROFILE=os.environ.get('AWS_PROFILE')
    lambda_layer_arn = prepare.get_lambda_layer_version(AWS_PROFILE)

lambda_functions = prepare.build_lambda()

app = cdk.App()
rules_stack = Rules(app, "StartupSecurityAccountRules",
                lambda_functions=lambda_functions,
                lambda_layer_arn=lambda_layer_arn,
                description="Custom account security rule for the Startup Security Baseline (uksb-1tupbocl2)")

pack_stack = Pack(app, "StartupSecurityAccountPack", description="Startup Security Baseline Account Conformance Pack (uksb-1tupbocl2)").add_dependency(rules_stack)

app.synth()
Aspects.of(app).add(AwsSolutionsChecks(verbose=True))