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
class snssqs(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        #LambdaSQSRole = iam.CfnRole(self,'lambdaexr',
        #managed_policy_arns=[
        #"arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
        #"arn:aws:iam::aws:policy/AmazonRekognitionReadOnlyAccess",
        #"arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
        #"arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess"    
        #],
        #assume_role_policy_document = {'Version':'2012-10-17',
            # 'Statement':{
            #     'Effect':'Allow',
            #     'Principal':{'Service':'lambda.amazonaws.com'},
            #     'Action':'sts:AssumeRole'},
            # 'Path':'/',
            # 'Policies':{
            #     'policyName':'root',
            #     'policyDocument':{
            #         'Version':'2012-10-17',
            #         'Statement':[{
            #             'Effect':'Allow',
            #             'Action':
            #                 ['logs:*'],
            #         'Resource':'arn:aws:logs:*:*:*'},
            #         ]}}})
        
        labelslambda=_lambda.CfnFunction(
            self,'labelslambda',
            handler='lambda_function.lambda_handler',
            role=core.Fn.import_value('LambdaExecutionRolearn'),
            #role = LambdaSQSRole.attr_arn
            code={
                'S3Bucket':core.Fn.import_value('sourcebucket'),
                'S3Key':'lambda.zip'
            },
            runtime='python3.6',
            timeout=120,
            tracing_config={'mode':'Active'},
            vpc_config={
                'securityGroupIds':[core.Fn.import_value('lambdasecuritygroup')],
                'subnetIds':[core.Fn.import_value('PrivateSubnet1output'),core.Fn.import_value('PrivateSubnet2output')],
                
            },
            environment={'variables':{
                'DATABASE_HOST':core.Fn.import_value('dbendpoint'),
                'DATABASE_USER':'web_user',
                'DATABASE_PASSWORD':core.Fn.import_value('dbpassword'),
                'DATABASE_DB_NAME':core.Fn.import_value('DBname')
            }}
            )
        uploadsqs=sqs.CfnQueue(self,'uploadsqs',queue_name='uploads-queue')
        #  uploadsqs=sqs.CfnQueue(
        #     self,'uploadsqs',
        #     queue_name='uploads-queue')        

        uploadsnstopic=sns.CfnTopic(
            self,'uploadsnstopic',
            display_name='uploads-topic',
            subscription= [{
                "endpoint" : uploadsqs.attr_arn,
                "protocol" : "sqs"
            },
            {
                "endpoint" : labelslambda.attr_arn,
                "protocol" : "lambda"
            }],
        )

        images3bucket=s3.CfnBucket(
            self,'images3bucket',
            bucket_name='imagebucketsns${AWS::AccountId}',
            notification_configuration={'TopicConfigurations':[
                {
                    'event':'s3:ObjectCreated:*',
                    'topic':uploadsnstopic.ref
                }]}
            )

        

        
        labelslambdaarn=labelslambda.attr_arn
        images3bucketpermission=_lambda.CfnPermission(
            self,'images3bucketpermission',
            action='lambda:InvokeFunction',
            function_name=labelslambdaarn,
            principal='sns.amazonaws.com',
            source_arn=uploadsnstopic.ref)

        
        
        uploadtopicpolicy=sns.CfnTopicPolicy(
            self,'uploadtopicpolicy',
            policy_document={
                'Version':'2012-10-17',
                'Id':'QueuePolicy',
                'Statement':[
                    {
                        'Sid':'Allow-S3-Publish',
                        'Effect':'Allow',
                        'Principal':[{'AWS':'*'}],
                        'Action':'SNS:Publish',
                        'Resource':uploadsnstopic.ref,
                        'Condition':{
                            'ArnLike':{
                                'aws:SourceArn':['arn:aws:s3:::imagebucketsns%s'%(core.Aws.ACCOUNT_ID)]
                                }
                            }
                        },
                    ]
            },
            
            topics=[uploadsnstopic.ref])
            

        queuepolicy=sqs.CfnQueuePolicy(
            self,'queuepolicy',
            queues=[uploadsqs.ref],
            policy_document={
                'Version':'2012-10-17',
                'Id':'QueuePolicy',
                'Statement':[
                    {
                        'Sid':'Allow-SendMessage-To-Queues-From-SNS-Topic',
                        'Effect':'Allow',
                        'Principal':[{'AWS':'*'}],
                        'Action':'SQS:SendMessage',
                        'Resource':'*',
                        'Condition':{
                            'ArnEquals':{'aws:SourceArn':uploadsnstopic.ref}
                        }
                    }]
            })
        # queuepolicy=sns.CfnQueuePolicy(
        #     self,'queuepolicy',
        #     policy_document={
        #         'Version':'2012-10-17',
        #         'Id':'QueuePolicy',
        #         'Statement':[
        #             {
        #                 'Sid':'Allow-SendMessage-To-Queues-From-SNS-Topic',
        #                 'Effect':'Allow',
        #                 'Principal':[{'AWS':'*'}],
        #                 'Action':'SQS:SendMessage',
        #                 'Resource':'*',
        #                 'Condition':{
        #                     'ArnLike':{
        #                         'aws:SourceArn':[uploadsnstopic.attr_arn]
        #                         }
        #                     }
        #                 },
        #             ]
        #     },)