#!/usr/bin/env python3

from aws_cdk import core

from cdkpj.iam_stack import IAMStack
from cdkpj.s3_stack import s3tack
from cdkpj.web_stack import webstack
from cdkpj.vpc_stack import vpcstack
from cdkpj.cdn_stack import cdnstack
from cdkpj.newcloud9 import cdkproject_cloud9
from cdkpj.db_stack import dbstack
from cdkpj.snssqs import snssqs
from cdkpj.security import security
from cdkpj.cognitostack import CognitoStack

app = core.App()

IAMStack(app,"iam",env={'region': 'us-east-1'})
vpcstack(app,'vpc',env={'region': 'us-east-1'})
security(app,'security',env={'region': 'us-east-1'})
dbstack(app,'dbstack',env={'region': 'us-east-1'})
s3tack(app,'s3',env={'region': 'us-east-1'})
webstack(app,'web',env={'region': 'us-east-1'})
cdnstack(app,'cdn',env={'region': 'us-east-1'})
cdkproject_cloud9(app,'cloud9',env={'region': 'us-east-1'})
snssqs(app,'snssqs',env={'region': 'us-east-1'})
CognitoStack(app,'cognito',env={'region': 'us-east-1'})

app.synth()