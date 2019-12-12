from aws_cdk import (
    aws_s3 as s3,
    core
    )

class s3tack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        new_bucket = s3.Bucket(self,'cdkprojectbucket',bucket_name="vtccdkbucket3")
        
        core.CfnOutput(self,'sourcebucket',
        value=new_bucket.bucket_name,
        description='sourcebucket name',
        export_name='sourcebucket')