from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_logs as log,
    core
)
from .vpc_stack import vpcstack 
from .cdn_stack import cdnstack
from .security import security

class webstack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        
        LatestAmiId = ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2).get_image(self).image_id
        
        CloudFormationLogs = log.CfnLogGroup(self,'cfnlog',retention_in_days=7) 
        
        Webserver1 = ec2.CfnInstance(
            self,id ='Webserver1',
            availability_zone = core.Fn.import_value('PrivateSubnet1az'),
            #vpc.PrivateSubnet1.attr_availability_zone,
            image_id = LatestAmiId,
            instance_type='t3.micro',
            iam_instance_profile = '',
            network_interfaces =[
                {'associatePublicIpAddress':True,
                'deviceIndex' : '0',
                'groupSet': [core.Fn.import_value('WebSecurityGroup')],
                'subnetId': core.Fn.import_value('PrivateSubnet1')}],
            tags=[{'key':'Name',
                'value':'Ex3WebServer'}])
        Webserver1.add_override('Metadata',{'AWS::CloudFormation::Init':{'config': {
          'commands': {
            'test': {
              'command': "echo {core.Aws.STACK_NAME} test",
              'env': {'STACK_NAME': '{core.Aws.STACK_NAME}'}}}}}})

        Webserver2 = ec2.CfnInstance(
            self,id ='Webserver2',
            availability_zone = core.Fn.import_value('PrivateSubnet2az'),
#or availability_zone = PublicSubnet1.ref ?
            image_id = LatestAmiId,
            instance_type='t3.micro',
            key_name= '####',
            network_interfaces =[
                {'associatePublicIpAddress':True,
                'deviceIndex' : '0',
                'groupSet': [core.Fn.import_value('WebSecurityGroup')],
                'subnetId': core.Fn.import_value('PrivateSubnet2')}],
            tags=[{'key':'Name',
                'value':'Ex3WebServer'}])
        Webserver2.add_override('Metadata', 
        {'AWS::CloudFormation::Init':{'config': {
          'commands': {
            'test': {
              'command': "echo {core.Aws.STACK_NAME} test",
              'env': {'STACK_NAME': '{core.Aws.STACK_NAME}'}}}}}})      

        DefaultTargetGroup = elb.CfnTargetGroup(self,'DefaultTargetGroup',
        health_check_enabled=True,health_check_interval_seconds=15, 
        health_check_path='/', 
        health_check_protocol= 'HTTP', 
        health_check_timeout_seconds= 10, 
        healthy_threshold_count= 2, 
        matcher={'httpCode':'200-299'},port= 80, 
        protocol='HTTP',vpc_id=core.Fn.import_value('vpc'),
        target_group_attributes=[{'key':'deregistration_delay.timeout_seconds','value':'30'}],
        targets=[
            {'id':'Webserver1.ref','port':80},
           {'id':'Webserver2.ref','port':80}
        ])
        
        HttpListener = elb.CfnListener(
            self,'HttpListener',
            default_actions =[{
                'type':'forward',
                'targetGroupArn':DefaultTargetGroup.ref
            }],
            load_balancer_arn = core.Fn.import_value('LoadBalancerArn'),
            port=80,
            protocol='HTTP'
        )