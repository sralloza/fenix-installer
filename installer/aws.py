import tempfile
from json import dumps, loads
from typing import List

import boto3
from botocore.exceptions import ClientError

from .cli.exceptions import TryAgainError
from .models import Service

S3_BUCKET_NAME = "fenix-secrets"


def get_secrets(service: Service) -> List[str]:
    s3 = boto3.client("s3")
    with tempfile.TemporaryFile() as fp:
        try:
            s3.download_fileobj(S3_BUCKET_NAME, service.name, fp)
        except Exception as exc:
            if "404" in str(exc):
                return []
            raise

        fp.seek(0)
        return loads(fp.read().decode("utf8"))


def set_secrets(service: Service, env_vars: List[str]):
    env_vars = list(set(env_vars))
    file_content = dumps(env_vars)
    s3 = boto3.client("s3")
    with tempfile.TemporaryFile() as fp:
        fp.write(file_content.encode("utf8"))
        fp.seek(0)
        try:
            s3.upload_fileobj(fp, S3_BUCKET_NAME, service.name)
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchBucket":
                create_bucket()
                raise TryAgainError("Bucket created, run command again")
            raise


def create_bucket():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket=S3_BUCKET_NAME)
