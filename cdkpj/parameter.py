from aws_cdk import (
    aws_ssm as ssm,
    core
    )

class parameter(core.Stack):
    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        param = ssm.StringParameter(self,scope,'param','edx-COGNITO_POOL_ID',
                                    parameter_name='edx-COGNITO_POOL_ID'
                                    )