from aws_cdk import (
    aws_ec2 as ec2,
    aws_cloud9 as cloud9,
    aws_lambda as lam,
    aws_iam as iam,
    aws_cloudformation as cfn,
    core
)

from .vpc_stack import vpcstack as vpc
from .iam_stack import IAMStack
class cdkproject_cloud9 (core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        

        newcloud9 = cloud9.CfnEnvironmentEC2(self,'newcloud9',
                                            instance_type="t2.micro",
                                            automatic_stop_time_minutes=30,
                                            name="BuildingOnAWS%s"%(core.Stack.stack_name),
                                            description="Building On AWS Cloud9"  ,
                                            owner_arn= core.Fn.import_value("edXProjectUser"),
                                            subnet_id= core.Fn.import_value('PrivateSubnet1output')
                                                )
        
        LambdaExecutionRole = iam.CfnRole(
            self,'LambdaExecutionRole',
            assume_role_policy_document = {
                'Version':'2012-10-17',
            'Statement':{
                'Effect':'Allow',
                'Principal':{'Service':'lambda.amazonaws.com'},
                'Action':'sts:AssumeRole'},
            'Path':'/',
            'Policies':{
                'PolicyName':'root',
                'PolicyDocument':{
                    'Version':'2012-10-17',
                    'Statement':[{
                        'Effect':'Allow',
                        'Action':
                            ['logs:CreateLogGroup',
                            'logs:CreateLogStream',
                            'logs:PutLogEvents'],
                    'Resource':'arn:aws:logs:*:*:*'},
                    {'Effect':'Allow',
                    'Action':'ec2:Describe*',
                    'Resource':'*'}]}}})
                    
        CustomFunction = lam.Function(
            self,'lambdafunction',
            code = lam.Code.asset('./cdkpj/cloud9'),
            runtime = lam.Runtime.NODEJS_8_10,
            handler='index.handler',
            role= iam.Role.from_role_arn(self, "role",LambdaExecutionRole.attr_arn),
            timeout= core.Duration.seconds(30)
            )
        
        # CustomResource = cfn.CustomResource(self,'CustomResource',
        # resource_type = 'Custom::CustomResource',properties={'service_token':CustomFunction.function_arn,
        #     'EdxProjectCloud9':newcloud9.ref
        # }
        # )
        # CustomResource = cfn.CfnCustomResource(self,'CustomResource', service_token = CustomFunction.function_arn)
        # CustomResource.add_override('Properties.CustomResource.EdxProjectCloud9',newcloud9.ref)
        
        CustomResource = core.CfnResource(self,'CustomResource',
            type = 'Custom::CustomResource',
            properties = {'service_token':CustomFunction.function_arn,
            'EdxProjectCloud9':newcloud9.ref
            })
        
        core.CfnOutput(self, "newcloud9output",
            value = newcloud9.attr_arn,
            description = "newcloud9",
            export_name = "newcloud9"
        )        
        core.CfnOutput(self, "LambdaExecutionRoleoutput",
            value = LambdaExecutionRole.attr_arn,
            description = "LambdaExecutionRole arn",
            export_name = "LambdaExecutionRolearn"
        )
