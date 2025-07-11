from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb_,
    aws_iam as iam,
    Duration,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
    aws_kinesis as kinesis,
    aws_lambda_event_sources,
)
from constructs import Construct
from decouple import config

LAMBDA_RUNTIME = _lambda.Runtime.PYTHON_3_9
LAMBDA_CONSUMER_NAME = config("LAMBDA_CONSUMER_NAME")
DYNAMO_TABLE_NAME = config("DYNAMO_TABLE_NAME")
INTRADAY_STREAM_NAME = config("INTRADAY_STREAM_NAME")
STREAM_ARN = "arn:aws:kinesis:eu-west-1:792399197691:stream/" + INTRADAY_STREAM_NAME

ENVIRONMENT = {"DYNAMO_TABLE_NAME": DYNAMO_TABLE_NAME}


class DataConsumerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dynamodb_table = dynamodb_.Table(
            self,
            id="DynamoDBIntradayTable",
            table_name=DYNAMO_TABLE_NAME,
            partition_key=dynamodb_.Attribute(
                name="ticker", type=dynamodb_.AttributeType.STRING
            ),
            sort_key=dynamodb_.Attribute(
                name="last_refreshed", type=dynamodb_.AttributeType.STRING
            ),
        )

        lambda_consumer_role = iam.Role(
            self,
            "LambdaConsumerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonKinesisFullAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonDynamoDBFullAccess"
                ),
            ],
        )

        crypo_data_consumer = _lambda.Function(
            self,
            "DataConsumerHandler",
            function_name=LAMBDA_CONSUMER_NAME,
            runtime=LAMBDA_RUNTIME,
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(20),
            handler="data_consumer_lambda.handler",
            environment=ENVIRONMENT,
            role=lambda_consumer_role,
        )

        stream = kinesis.Stream.from_stream_arn(
            self, "IntradayStream", stream_arn=STREAM_ARN
        )

        crypo_data_consumer.add_event_source(
            aws_lambda_event_sources.KinesisEventSource(
                stream,
                batch_size=100,
                starting_position=_lambda.StartingPosition.LATEST,
            )
        )
