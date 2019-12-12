from aws_cdk import (
    aws_sns as sns,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_ec2 as ec2,
    core
)
from .vpc_stack import vpcstack as vpc
from . s3_stack import s3tack
class security(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
    # WebServerRole
        web_server_role = iam.CfnRole(self, "WebServerRole",
          role_name= "ec2-webserver-role",
          assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Service": [
                  "ec2.amazonaws.com"
                ]
              },
              "Action": [
                "sts:AssumeRole"
              ]
            }]
          },
          managed_policy_arns = [
            "arn:aws:iam::aws:policy/AmazonS3FullAccess",
            "arn:aws:iam::aws:policy/AmazonRekognitionReadOnlyAccess",
            "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM",
            "arn:aws:iam::aws:policy/AmazonPollyReadOnlyAccess",
            "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
          ],
          path = "/",
          policies = [
            {
              "policyName" : "SystemsManagerParameters",
              "policyDocument" : {
                "Version":"2012-10-17",
                "Statement" : [
                {
                  "Effect": "Allow",
                  "Action" : [
                    "ssm:DescribeParameters"
                  ],
                    "Resource": "*"
                },
                {
                  "Effect" : "Allow",
                  "Action" : [
                    "ssm:GetParameters"
                  ],
                  "Resource": {"Fn::Sub" : "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/edx-*"}
                }]
              }
            },
            {
              "policyName" : "LogRolePolicy",
              "policyDocument" : {
                "Version":"2012-10-17",
                "Statement" : [
                {
                  "Effect" : "Allow",
                  "Action" : [
                  'logs:CreateLogGroup',
                  'logs:CreateLogStream',
                  'logs:PutLogEvents',
                  'logs:DescribeLogStreams'
                ],
                  "Resource": {"Fn::Sub" : "arn:aws:logs::${AWS::Region}:*:*"}
                }]
              }
            }
          ]
        )
        
        lambdasecuritygroup = ec2.CfnSecurityGroup(
            self,"lambdasecuritygroup",
            vpc_id=core.Fn.import_value("vpc"),
            group_name="labels-lambda-sg",
            group_description="HTTP traffic",
            security_group_egress=[{
                "ipProtocol":"tcp",
                "fromPort":0,
                "toPort":65535,
                "cidrIp":"0.0.0.0/0"
                }]
            )
        #Create Security group for ec2
        web_security_group = ec2.CfnSecurityGroup(self, "WebSecurityGroup",
            group_name = "web-server-sg",
            group_description =  "HTTP traffic",
            vpc_id = core.Fn.import_value("vpc"),
            security_group_ingress = [
                {
                    "ipProtocol" : "tcp",
                    "fromPort" : 80,
                    "toPort" : 80,
                    "cidrIp" : "0.0.0.0/0"
                }
            ],
            security_group_egress = [
                {
                    "ipProtocol" : "tcp",
                    "fromPort" : 0,
                    "toPort" : 65535,
                    "cidrIp" : "0.0.0.0/0"
                }
            ],
        )
        
        DBSG = ec2.CfnSecurityGroup(
            self,"DBSG",
            group_name="DB-Security-Group",
            group_description="DB_traffic",
            vpc_id=core.Fn.import_value("vpc"),
            security_group_ingress=[
                {
                    "ipProtocol" : "tcp",
                    "fromPort" : 3306,
                    "toPort" : 3306,
                    "cidrIp":"0.0.0.0/0"
#                    "sourceSecurityGroupId" : web_security_group.value_as_string
                }],
                security_group_egress = [{
                    "ipProtocol" : "tcp",
                    "fromPort" : 0,
                    "toPort" : 65535,
                    "cidrIp" : "0.0.0.0/0"
                }]
                
            )
        

# Output
        core.CfnOutput(self, "dbsg",
        value = DBSG.ref,
             description = "DB traffic",
             export_name = "DBSG"
         )
        
        core.CfnOutput(self, "WebSecurityGroupoutput",
            value = web_security_group.ref,
            description = "WebSecurityGroup",
            export_name = "WebSecurityGroup"
        )
            
        core.CfnOutput(self, "lambdasecuritygroup_output",
            value = lambdasecuritygroup.ref,
            description = "lambdasecuritygroup",
            export_name = "lambdasecuritygroup"
        )
                
