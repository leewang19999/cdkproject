from aws_cdk import (
    aws_rds as rds,
    aws_ec2 as ec2,
    core
    )

from .vpc_stack import vpcstack


class dbstack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        DBPassword=core.CfnParameter(self,'DBPassword',
        no_echo=True,
        type='String',
        description = 'New account and RDS password',
        constraint_description='the password must be between 1 and 41 characters', 
        max_length=41,min_length=1,
        default = 'Password')
        
        MyDBSubnetGroup = rds.CfnDBSubnetGroup(self,'dbsubnet',
        db_subnet_group_description = 'MyDBSubnetGroup',
        subnet_ids = [core.Fn.import_value('PrivateSubnet1'),core.Fn.import_value('PrivateSubnet2')])
        
        #dbsg = ec2.CfnSecurityGroup(self,'DBSecurityGroup',
        #group_description = 'DB traffic',
        #group_name ='SecurityGroup for DB',
        #vpc_id = core.Fn.import_value('vpcoutput'),
        #security_group_ingress = [{'IpProtocol':'tcp','FromPort':3306,'ToPort':3306,
        #'SourceSecurityGroupId':core.Fn.import_value('WebSecurityGroupoutput')}],
        #security_group_egress =[{'CidrIp':'0.0.0.0/0','FromPort':0,'ToPort':65535,'ipProtocol':'tcp'}]
        #)
        #dbsg = ec2.SecurityGroup(self,'DBSecurityGroup',vpc=core.Fn.import_value('vpcoutput'),
        #description='DB traffic',security_group_name='SecurityGroupforDB',allow_all_outbound=True)
        #dbsg.add_ingress_rule(peer=core.Fn.import_value('WebSecurityGroupoutput'),connection=ec2.Port.tcp(3306),remote_rule=True)
        
        
        RDSCluster = rds.CfnDBCluster(self,'RDSCluster',
        engine = 'aurora',
        database_name='Photos',
        db_cluster_identifier='edx-photos-db',
        db_subnet_group_name= MyDBSubnetGroup.db_subnet_group_name, 
        engine_mode='serverless', 
        master_username='master', master_user_password=DBPassword.value_as_string,
        scaling_configuration={'autoPause':True ,'maxCapacity':4,'minCapacity':2},
        vpc_security_group_ids=[core.Fn.import_value('DBSG')])
        
        
        core.CfnOutput(self, 'dbendpoint',
            value = RDSCluster.attr_endpoint_port,
            description = "MyDB Endpoint",
            export_name = "DBEndpoint"
        )
        core.CfnOutput(self, 'dbname',
            value = RDSCluster.database_name,
            description = "MyDB name",
            export_name = "DBname"
        )        
        core.CfnOutput(self,'dbpassword',
        value=DBPassword.value_as_string,
        description='dbpassword',
        export_name='dbpassword')
        
'''
        security_group_ingress = [{'ipProtocol':'tcp','fromPort':3306,'toPort':3306,
        'sourceSecurityGroupId':core.Fn.import_value('WebSecurityGroupoutput')}],
        security_group_egress =[{'cidrIp':'0.0.0.0','fromPort':0,'toPort':65535,'ipProtocol':'tcp'}])
'''