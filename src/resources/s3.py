from dagster import ConfigurableResource


class S3Resource(ConfigurableResource):
    aws_acces_key_id: str
    aws_secret_acces_key: str
    endpoint_url: str
    bucket_url: str