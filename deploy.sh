#!/bin/bash

yes | cdk deploy iam --require-approval
yes | cdk deploy vpc --require-approval
yes | cdk deploy security --require-approval
yes | cdk deploy dbstack --require-approval
yes | cdk deploy s3 --require-approval
yes | cdk deploy cdn --require-approval
yes | cdk deploy web --require-approval
yes | cdk deploy cloud9 --require-approval
yes | cdk deploy snssqs --require-approval
yes | cdk deploy cognito --require-approval

