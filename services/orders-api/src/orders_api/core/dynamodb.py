from typing import Any

import boto3

from orders_api.core.config import settings


def get_dynamodb_resource() -> Any:
    """Cria a conexão com o DynamoDB, a partir da configuração."""
    return boto3.resource(
        "dynamodb",
        region_name=settings.aws_region,
        endpoint_url=settings.dynamodb_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
