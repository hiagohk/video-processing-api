#!/bin/bash
set -e

echo "Creating SQS queues..."

awslocal sqs create-queue --queue-name video-processing-queue

awslocal sqs create-queue --queue-name video-processing-dlq

echo "Queues created"
