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
The [Startup Security Baseline (AWS SSB)](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/welcome.html) prescriptive guidance was published in 2022 to provide a lightweight set of security controls to enable Startups to secure their AWS accounts and workloads with minimal effort and without impacting their agility.

The purpose of this solution is to further minimise customer effort of adopting AWS SSB by addressing the manual validation of AWS SSB controls. This is achieved through the deployment of AWS Config Conformance Packs scoped to the [Account](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/controls-acct.html) section of the prescriptive guidance.

The Conformance Packs use a combination of AWS Managed Rules and Custom Lambda rules built and deployed with the [AWS Rules Development Kit (rdk)](https://github.com/awslabs/aws-config-rdk).

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
* This sample relies on the [credentials configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) used by the aws-cli. 
* The target AWS account for the Conformance Pack should be [bootstrapped for CDK](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) deployments. 
* **IMPORTANT:** Do NOT run the `cdk bootstrap` process from within the repository directory. This will attempt to deploy the CDK before the account is bootstrapped and will generate errors.
## Install

        rdk init --generate-lambda-layer

This will do the following in the target AWS account:
1. Enable AWS Config
2. Create an IAM role called config-role for use by AWS Config
3. Two S3 buckets, one for uploading rules (used by RDK for development) and one for AWS Config to deliver its results too.
4. Deploy a serverlessrepo application that consists of the RDK lambda layer used by the rules. This will be a Cloudformation stack in your account.

Once completed you can now deploy the CDK application by running the following command locally from the root of the repository:

        cdk deploy --all

**NOTE:** You must deploy the RDK lambda first in order for the CDK application to complete. The CDK application will query Cloudformation and import the Lambda layer ARN into its configuration.

## Supported Rules
| Baseline Item | Description | Managed Rule (Type) | Conformance Pack Rule | Notes |
| ----------- | ----------- | -------------------- | ---------------------- | -- |
| ACCT.01 | Set account-level contacts | CUSTOM_LAMBDA | ACCT01_SET_ACCOUNT_CONTACTS | Checks that 'BILLING', 'OPERATIONS', 'SECURITY' contacts are set | 
| ACCT.02 | Restrict use of the root user | ROOT_ACCOUNT_MFA_ENABLED | ACCT02_RESTRICT_ROOT_USER | |
| ACCT.03 | Configure Console Access | MFA_ENABLED_FOR_IAM_CONSOLE_ACCESS | ACCT03_CONFIGURE_CONSOLE_ACCESS | |
| ACCT.04 | Use IAM user groups | IAM_USER_GROUP_MEMBERSHIP_CHECK | ACCT04_USE_IAM_USER_GROUPS | |
| ACCT.05 | Require MFA | IAM_USER_MFA_ENABLED | ACCT05_REQUIRE_MFA | |
| ACCT.06 | Enforce a password policy | IAM_PASSWORD_POLICY | ACCT06_ENFORCE_A_PASSWORD_POLICY | |
| ACCT.07 | Log events | CLOUDTRAIL_SECURITY_TRAIL_ENABLED | ACCT07_LOG_EVENTS | |
| ACCT.08 | Prevent public access to private S3 buckets | S3_ACCOUNT_LEVEL_PUBLIC_ACCESS_BLOCKS_PERIODIC | ACCT08_PREVENT_PUBLIC_ACCESS_TO_PRIVATE_S3_BUCKETS | |
| ACCT.09 | Delete unused resources	| CUSTOM_LAMBDA | ACC09_DELETE_UNUSED_RESOURCES | This will check for the presence of default VPCs in all available regions in the account |
| ACCT.10 | Monitor costs | CUSTOM_LAMBDA | ACCT10_MONITOR_COSTS |	 Checks for at least one Budget configured |
| ACCT.11 | Enable GuardDuty | GUARDDUTY_ENABLED_CENTRALIZED | ACCT11_ENABLE_GUARDDUTY | |
| ACCT.12 | Monitor high-risk issues | CUSTOM_LAMBDA | ACCT12_MONITOR_HIGH_RISK_ISSUES | Requires Premium Support subscription. Checks Trusted Adivsor for any issues in 'error' state. If Premium Support is not enabled will report as NOT_APPLICABLE and have no status in the Console  |

## Estimated Cost
Assuming the Conformance Pack is deployed in a single account in us-east-1 region, with 25 active IAM users (evaulated in detective mode) and 24 active regions. This would give a total number of configuration items of 50. 1 account, 24 regions and 25 IAM users.
| Cost Definition | Calculation | Cost | 
| ----------- | ----------- | -------------------- |  
| __Cost of configuration items__ | 50 * 0.003 | $0.15 |
| __Cost of AWS Config rules__ |  First 100,000 evaluations at $0.001 each = 1000 * $0.001 | $1 |
| __Cost of conformance packs__ | First 100,000 conformance pack evaluations at $0.001 each | 1,000 * 0.001 =$1 |
| __Estimated Monthly AWS Config Bill__ | $0.15 + $1 + $1 | $2.15 |
