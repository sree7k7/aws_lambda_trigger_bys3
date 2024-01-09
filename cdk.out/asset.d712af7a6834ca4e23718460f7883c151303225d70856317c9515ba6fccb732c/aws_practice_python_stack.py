from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
)
from constructs import Construct
from aws_cdk import aws_s3_notifications as s3n

class AwsPracticePythonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket
        bucket = s3.Bucket(self, "aws-practice-python-bucket", versioned=True)  # versioned=True means that the bucket will keep all versions of the files uploaded to it

# create lambda function
        function = _lambda.Function(self, "lambda_function",
                                    runtime=_lambda.Runtime.PROVIDED_AL2,
                                    handler="lambda-handler.main",
                                    code=_lambda.Code.from_asset(
                                        "aws_practice_python"
                                    )
                                    )

        # grant lambda function read/write permissions to the bucket
        # bucket.grant_read_write(lambda_function)

        # # create notification for the bucket
        # notification = s3n.LambdaDestination(lambda_function)

        # # add notification to the bucket
        # bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification)