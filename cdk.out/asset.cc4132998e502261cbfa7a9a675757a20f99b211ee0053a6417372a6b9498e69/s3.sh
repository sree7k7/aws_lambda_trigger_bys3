#!/bin/bash

# This script is used to create a bucket in S3 and upload a file to it.

# Set the region and bucket name
region="eu-central-1"
bucket="sran-test-619831221558"
aws s3 mb s3://$bucket --region $region