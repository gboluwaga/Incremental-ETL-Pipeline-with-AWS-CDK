#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import Tags

from kinesis_stream.kinesis_stream_stack import kinesisStreamStack
from data_consumer.data_consumer_stack import DataConsumerStack
from data_producer.data_producer_stack import DataProducerStack
from s3_bucket.s3_bucket_stack import S3BucketStack

env_EU = cdk.Environment(account="792399197691", region="eu-west-1")


app = cdk.App()
kinesis_stream = kinesisStreamStack(app, "kinesisStreamStack", env=env_EU)
data_consumer = DataConsumerStack(app, "DataConsumerStack", env=env_EU)
data_producer = DataProducerStack(app, "DataProducerStack", env=env_EU)
s3_bucket = S3BucketStack(app, "S3BucketStack", env=env_EU)

Tags.of(app).add("ProjectOwner","Gboluwaga")
Tags.of(app).add("ProjectName","crypto-incremental-pipeline")

app.synth()
