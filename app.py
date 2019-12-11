#!/usr/bin/env python3

from aws_cdk import core

from cdkpj.cdkpj_stack import CdkpjStack


app = core.App()
CdkpjStack(app, "cdkpj", env={'region': 'us-west-2'})

app.synth()
