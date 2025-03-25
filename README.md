Startup Security Baseline Account Conformance Pack
==========================================

Table of Contents
-----------------

1. [Purpose](#purpose)
2. [Architecture](#architecture)
3. [Pre-requisites](#pre-requisites)
4. [Install](#install)
5. [Supported Rules](#supported-rules)

## Purpose

The [Startup Security Baseline (AWS SSB)](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/welcome.html)
prescriptive guidance was published in 2022 to provide a lightweight set of security controls to enable Startups to
secure their AWS accounts and workloads with minimal effort and without impacting their agility.

The purpose of this solution is to further minimise customer effort of adopting AWS SSB by addressing the manual
validation of AWS SSB controls. This is achieved through the deployment of AWS Config Conformance Packs scoped to
the [Account](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/controls-acct.html)
section of the prescriptive guidance.

The Conformance Packs use a combination of AWS Managed Rules and Custom Lambda rules built and deployed with
the [AWS Rules Development Kit (rdk)](https://github.com/awslabs/aws-config-rdk).

![Compliance View](/images/config1.png "Compliance View")
![Rules View](/images/config2.png "Rules View")

## Architecture

![Architecture](/images/ssb_conformance_pack_diagram.png "Architecture")

## Pre-requisites

* [AWS Cloud Development Kit](https://docs.aws.amazon.com/cdk/v2/guide/home.html) version 2.50 or higher.
* All required libraries installed using python pip.

        pip install -r requirements.txt

This command is run locally from the root of the repository. It will install the following:

* [AWS Config Rule Development Kit](https://github.com/awslabs/aws-config-rdk)
* [AWS Config Rules Development Kit Library Addition](https://github.com/awslabs/aws-config-rdklib)
* [Jinja2 Templating library](https://jinja.palletsprojects.com/en/3.1.x/)

### Additional Requirements

* This sample relies on
  the [credentials configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) used by the
  aws-cli.
* The target AWS account for the Conformance Pack should
  be [bootstrapped for CDK](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) deployments.
* **IMPORTANT:** Do NOT run the `cdk bootstrap` process from within the repository directory. This will attempt to
  deploy the CDK Conformance pack before the account is bootstrapped for CDK and will generate errors.

## Install

        rdk init --generate-lambda-layer

This will do the following in the target AWS account:

1. Enable AWS Config
2. Create an IAM role called config-role for use by AWS Config
3. Two S3 buckets, one for uploading rules (used by RDK for development) and one for AWS Config to deliver its results
   too.
4. Deploy a serverlessrepo application that consists of the RDK lambda layer used by the rules. This will be a
   Cloudformation stack in your account.

Once completed you can now deploy the CDK application by running the following command locally from the root of the
repository:

        cdk deploy --all

**NOTE:** You must deploy the RDK lambda first in order for the CDK application to complete. The CDK application will
query Cloudformation and import the Lambda layer ARN into its configuration.

## Supported Rules
| SSB Conformance Pack Rule | AWS Config Rule |
|  :-------------------- | :---------------------- |
| [ACCT01_SET_ACCOUNT_CONTACTS](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-01.html) | [CUSTOM_LAMBDA](https://github.com/aws-samples/deploy-conformance-pack-for-aws-startup-security-baseline/tree/main/src/ACCT01_SET_ACCOUNT_CONTACTS) | 
| [ACCT02_RESTRICT_ROOT_USER](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-02.html) | [ROOT_ACCOUNT_MFA_ENABLED](https://docs.aws.amazon.com/config/latest/developerguide/root-account-mfa-enabled.html)] | 
| [ACCT03_CONFIGURE_CONSOLE_ACCESS](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-03.html) | [MFA_ENABLED_FOR_IAM_CONSOLE_ACCESS](https://docs.aws.amazon.com/config/latest/developerguide/mfa-enabled-for-iam-console-access.html) |  
| [ACCT04_USE_IAM_USER_GROUPS](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-04.html) | [IAM_USER_GROUP_MEMBERSHIP_CHECK](https://docs.aws.amazon.com/config/latest/developerguide/iam-user-group-membership-check.html) | 
| [ACCT05_REQUIRE_MFA](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-05.html) | [IAM_USER_MFA_ENABLED](https://docs.aws.amazon.com/config/latest/developerguide/iam-user-mfa-enabled.html) | 
| [ACCT06_ENFORCE_A_PASSWORD_POLICY](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-06.html) | [IAM_PASSWORD_POLICY](https://docs.aws.amazon.com/config/latest/developerguide/iam-password-policy.html) | 
| [ACCT07_LOG_EVENTS](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-07.html) | [CLOUDTRAIL_SECURITY_TRAIL_ENABLED](https://docs.aws.amazon.com/config/latest/developerguide/cloudtrail-security-trail-enabled.html) | 
| [ACCT08_PREVENT_PUBLIC_ACCESS_TO_PRIVATE_S3_BUCKETS](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-08.html) | [S3_ACCOUNT_LEVEL_PUBLIC_ACCESS_BLOCKS_PERIODIC](https://docs.aws.amazon.com/config/latest/developerguide/s3-account-level-public-access-blocks-periodic.html) | 
| [ACC09_DELETE_UNUSED_RESOURCES](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-09.html)  | [CUSTOM_LAMBDA](https://github.com/aws-samples/deploy-conformance-pack-for-aws-startup-security-baseline/tree/main/src/ACCT09_DELETE_UNUSED_RESOURCES) |
| [ACCT10_MONITOR_COSTS](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-10.html) | [CUSTOM_LAMBDA](https://github.com/aws-samples/deploy-conformance-pack-for-aws-startup-security-baseline/tree/main/src/ACCT10_MONITOR_COSTS) |
| [ACCT11_ENABLE_GUARDDUTY](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-11.html) | [GUARDDUTY_ENABLED_CENTRALIZED](https://docs.aws.amazon.com/config/latest/developerguide/guardduty-enabled-centralized.html) |
| [ACCT12_MONITOR_HIGH_RISK_ISSUES](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/acct-12.html) | [CUSTOM_LAMBDA](https://github.com/aws-samples/deploy-conformance-pack-for-aws-startup-security-baseline/tree/main/src/ACCT12_MONITOR_HIGH_RISK_ISSUES) | 
| [WKL01_USE_IAM_ROLES_FOR_COMPUTE_ENVIRONMENT_PERMISSIONS](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/wkld-01.html) | [EC2_INSTANCE_PROFILE_ATTACHED](https://docs.aws.amazon.com/config/latest/developerguide/ec2-instance-profile-attached.html) | 
| [WKL02_RESTRICT_CREDENTIAL_USAGE_SCOPE_WITH_RESOURCE_BASED_POLICIES_PERMISSIONS](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/wkld-02.html) | [S3_BUCKET_POLICY_GRANTEE_CHECK](https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-policy-grantee-check.html) | 
| [WKL03_USE_EPHEMERAL_SECRETS_OR_A_SECRETS_MANAGEMENT_SERVICE](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/wkld-03.html) | [CUSTOM_LAMBDA]() |
| [WKL06_USE_SYSTEMS_MANAGER_INSTEAD_OF_SSH_OR_RDP](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/wkld-06.html) | [CUSTOM_LAMBDA]() | 
| [WKL07_LOG_DATA_EVENTS_FOR_S3_BUCKETS_WITH_SENSITIVE_DATA](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/wkld-07.html) | [CLOUDTRAIL_S3_BUCKET_ACCESS_LOGGING](https://docs.aws.amazon.com/config/latest/developerguide/cloudtrail-s3-bucket-access-logging.html) | 
| [WKL08_ENCRYPT_AMAZON_EBS_VOLUMES](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/wkld-08.html) | [EC2_EBS_ENCRYPTION_BY_DEFAULT](https://docs.aws.amazon.com/config/latest/developerguide/ec2-ebs-encryption-by-default.html) | 
| [WKL09_ENCRYPT_AMAZON_RDS_DATABASES](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/wkld-09.html) | [RDS_STORAGE_ENCRYPTED](https://docs.aws.amazon.com/config/latest/developerguide/rds-storage-encrypted.html) | 
| [WKL10_DEPLOY_PRIVATE_RESOURCES_INTO_PRIVATE_SUBNETS](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/wkld-10.html) | [RDS_INSTANCE_PUBLIC_ACCESS_CHECK](https://docs.aws.amazon.com/config/latest/developerguide/rds-instance-public-access-check.html) | 
| [WKL11_RESTRICT_NETWORK_ACCESS_BY_USING_SECURITY_GROUPS](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/wkld-11.html) | [INCOMING_SSH_DISABLED](https://docs.aws.amazon.com/config/latest/developerguide/restricted-ssh.html) | 
| [WKL12_USE_VPC_ENDPOINTS_TO_ACCESS_SUPPORTED_SERVICES](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/wkld-12.html) | [CUSTOM_LAMBDA]() | 


## Estimated Cost

Assuming the Conformance Pack is deployed in a single account in us-east-1 region, with 25 active IAM users (evaluated
in detective mode) and 24 active regions. This would give a total number of configuration items of 50. 1 account, 24
regions and 25 IAM users.
| Cost Definition | Calculation | Cost |
| ----------- | ----------- | -------------------- |  
| __Cost of configuration items__ | 50 * 0.003 | $0.15 |
| __Cost of AWS Config rules__ | First 100,000 evaluations at $0.001 each = 1000 * $0.001 | $1 |
| __Cost of conformance packs__ | First 100,000 conformance pack evaluations at $0.001 each | 1,000 * 0.001 =$1 |
| __Estimated Monthly AWS Config Bill__ | $0.15 + $1 + $1 | $2.15 |
