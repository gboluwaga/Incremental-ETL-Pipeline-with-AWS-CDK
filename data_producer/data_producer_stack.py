from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    Duration,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct
from decouple import config

LAMBDA_RUNTIME = _lambda.Runtime.PYTHON_3_9
LAMBDA_PRODUCER_NAME = config("LAMBDA_PRODUCER_NAME")

ENVIRONMENT = {
    "API_KEY": config("API_KEY"),
    "INTRADAY_STREAM_NAME": config("INTRADAY_STREAM_NAME"),
}

CRYPTO_CONVERSIONS = [("BTC", "USD"), ("ETC", "USD"), ("DOGE", "USD")]


class DataProducerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonKinesisFullAccess"
                ),
            ],
        )

        alpha_vantage_layer = _lambda.LayerVersion(
            self,
            "AlphaVantageLayer",
            code=_lambda.AssetCode("layers/alpha_vantage_layer"),
        )

        crypo_data_producer = _lambda.Function(
            self,
            "CryptoDataHandler",
            function_name=LAMBDA_PRODUCER_NAME,
            runtime=LAMBDA_RUNTIME,
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(60),
            layers=[alpha_vantage_layer],
            handler="data_producer_lambda.handler",
            environment=ENVIRONMENT,
            role=lambda_role,
        )

        intraday_rule = events.Rule(
            self, "IntradayRule", schedule=events.Schedule.rate(Duration.minutes(1))
        )

        for conversion in CRYPTO_CONVERSIONS:
            intraday_target = targets.LambdaFunction(
                crypo_data_producer,
                event=events.RuleTargetInput.from_object(
                    {"from_currency": conversion[0], "to_currency": conversion[1]}
                ),
            )
            intraday_rule.add_target(intraday_target)
