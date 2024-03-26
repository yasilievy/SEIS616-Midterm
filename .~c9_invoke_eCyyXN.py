#!/usr/bin/env python
from constructs import Construct

from cdktf import (
    App,
    Token,
    TerraformStack,
    TerraformOutput,
)
from imports.aws.provider import AwsProvider
from imports.aws.s3_bucket import S3Bucket
from imports.aws.s3_bucket_acl import S3BucketAcl
from imports.aws.s3_bucket_policy import S3BucketPolicy
from imports.aws.s3_bucket_ownership_controls import S3BucketOwnershipControls
from imports.aws.s3_bucket_ownership_controls import S3BucketOwnershipControlsRule
from imports.aws.s3_bucket_public_access_block import S3BucketPublicAccessBlock
from imports.aws.s3_bucket_website_configuration import *
from imports.aws.data_aws_iam_policy_document import *


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AwsProvider(self, "AWS", region="us-west-2")

        # Defines the s3 bucket to be used for static website hosting
        aws_s3_bucket = S3Bucket(self, "s3_bucket_static_website",
            bucket="tutorial-static_website_s3",
        )
        
        # Defines the ownership control
        aws_s3_bucket_ownership_controls_example = S3BucketOwnershipControls(self, "s3_bucket_ownership",
            bucket=aws_s3_bucket.id,
            rule=S3BucketOwnershipControlsRule(
            object_ownership="BucketOwnerPreferred"
            )
        )
        
        # Defines the public access block and sets the block public
        aws_s3_bucket_public_access_block_example = S3BucketPublicAccessBlock(self, "s3_bucket_public_access",
            block_public_acls=False,
            block_public_policy=False,
            bucket=aws_s3_bucket.id,
            ignore_public_acls=False,
            restrict_public_buckets=False
        )
        
        # Defines the bucket acl and sets acl to public read. also references:
        # aws_s3_bucket_ownership_controls_example
        # aws_s3_bucket_public_access_block_example
        aws_s3_bucket_acl_example = S3BucketAcl(self, "s3_bucket_acl",
            acl="public-read",
            bucket=aws_s3_bucket.id,
            depends_on=[aws_s3_bucket_ownership_controls_example,aws_s3_bucket_public_access_block_example]
        )
        
        # Defines the bucket website configuration and sets the error/index htmls
        aws_s3_configuration = S3BucketWebsiteConfiguration(self, "s3_configuration",
            bucket=aws_s3_bucket.id,
            error_document=S3BucketWebsiteConfigurationErrorDocument(
                key="error.html"
            ),
            index_document=S3BucketWebsiteConfigurationIndexDocument(
                suffix="index.html"
            ),
        )
        
        # Defines more access with data IAM policies and allows actions for all users
        allow_access_from_another_account = DataAwsIamPolicyDocument(self, "allow_access_from_another_account",
            statement=[DataAwsIamPolicyDocumentStatement(
                actions=["s3:GetObject"],
                principals=[DataAwsIamPolicyDocumentStatementPrincipals(
                    identifiers=["123456789012"],
                    type="*"
                    )
                ],
                resources=[aws_s3_bucket.arn, "${" + aws_s3_bucket.arn + "}/*"]
                )
            ]
        )
        
        # Defines a second set of bucket policy
        aws_s3_bucket_policy_allow_access_from_another_account = S3BucketPolicy(self, "allow_access_from_another_account_2",
            bucket=aws_s3_bucket.id,
            policy=Token.as_string(allow_access_from_another_account.json)
        )
        
        # Defines the terraform output
        TerraformOutput(self, "arn", value=aws_s3_bucket.arn)
        TerraformOutput(self, "bucket_domain_name", value=aws_s3_bucket.bucket_domain_name)
        TerraformOutput(self, "bucket_regional_domain_name", value=aws_s3_bucket.bucket_regional_domain_name)

app = App()
stack = MyStack(app, "static-website-s3")
app.synth()
