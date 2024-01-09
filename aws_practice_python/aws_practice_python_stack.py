from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_sns as sns,
)
from constructs import Construct
from aws_cdk import aws_s3_notifications as s3n
from aws_cdk import aws_sns_subscriptions as sns_subscriptions
import aws_cdk.aws_lambda_event_sources as eventsources
from aws_cdk import aws_lambda_destinations as destinations
from aws_cdk import aws_iam as iam
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_logs as logs
from aws_cdk import aws_lambda as triggers

class AwsPracticePythonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket
        bucket = s3.Bucket(self, 
                           "aws-practice-python-bucket", 
                            versioned=False,
                            removal_policy=RemovalPolicy.DESTROY,
                            # auto_delete_objects=True,
                            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                            event_bridge_enabled=True,
                            notifications_handler_role=iam.Role(self,
                                                                "S3NotificationHandlerRole",
                                                                assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                                                                managed_policies=[
                                                                    iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                                                                    iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
                                                                ],
                                                                )                            
                           ) 

        ## IAM role to allow lambda function to access S3 bucket
        role = iam.Role(self, "LambdaExecutionRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("lambda.amazonaws.com"),
                iam.ServicePrincipal("s3.amazonaws.com")
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
            ],
            role_name="LambdaExecutionRole-aws-practice-python",
            inline_policies={
                "lambda_policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            resources=["arn:aws:logs:*:*:*"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:PutBucketNotification",
                                "s3:DeleteObject",
                                "s3:ListBucket",
                                "s3:ListBucketVersions",
                                "s3:ListBucketMultipartUploads",
                                "s3:AbortMultipartUpload"                                
                            ],
                            resources=[bucket.bucket_arn, f"{bucket.bucket_arn}/*"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "sns:Publish"
                            ],
                            resources=["*"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "cloudwatch:*"
                            ],
                            resources=["*"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "lambda:*"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }  
        )
        # create lambda function to send a sns notification when a file is uploaded to the bucket
        topic = sns.Topic(self, 
                           "s3-object-notification",
                            display_name="S3 Object Notification",
                            topic_name="s3-object-notification",
                          )
        function = _lambda.Function(self, 
                                    "aws-practice-python-lambda",
                                    runtime=_lambda.Runtime.PYTHON_3_10,
                                    code=_lambda.Code.from_asset('lambda'), # directory of lambda code
                                    handler="lambda_function.lambda_handler",
                                    
                                    environment={
                                        "LOG_LEVEL": "INFO",
                                        "BUCKET_NAME": bucket.bucket_name
                                    },
                                    events=[
                                        eventsources.S3EventSource(
                                            bucket=bucket,
                                            events=[s3.EventType.OBJECT_CREATED, s3.EventType.OBJECT_REMOVED])
                                    ],
                                    role=role,
                                    on_success=destinations.SnsDestination(topic),
                                    on_failure=destinations.SnsDestination(topic),
                                    log_group=logs.LogGroup(self, "aws-practice-python-log-group",
                                        log_group_name=f"/aws/lambda/{construct_id}",
                                        retention=logs.RetentionDays.ONE_WEEK,
                                        removal_policy=RemovalPolicy.DESTROY
                                    ),
                                    )
        ## create event notification for the bucket
        # bucket.add_event_notification(s3.EventType.OBJECT_CREATED,  s3n.LambdaDestination(function))

        # # grant lambda function read/write permissions to the bucket
        bucket.grant_read_write(function)

        # # grant SNS topic publish permissions by lambda function
        topic.grant_publish(function)

        ## Add email destination to SNS topic
        topic.add_subscription(sns_subscriptions.EmailSubscription("sree7k7@gmail.com"))