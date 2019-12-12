from aws_cdk import (
    aws_ec2 as ec2,
    core
)


class vpcstack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        VPC = ec2.CfnVPC(self,'VPC',
        cidr_block='10.1.0.0/16',
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags=[core.CfnTag(key='Name',value='edx-build-aws-vpc')])
        
        InternetGateway = ec2.CfnInternetGateway(self,'InternetGateway',
        tags=[core.CfnTag(key='Name',value='edx-igw')])
             
        AttachGateway = ec2.CfnVPCGatewayAttachment(self,'AttachGateway',vpc_id= VPC.ref,
        internet_gateway_id = InternetGateway.ref)
        
        EIP1 = ec2.CfnEIP(self, 'EIP1',domain='vpc')
        alloc_id = EIP1.get_att('AllocationId').to_string()
        EIP1.add_depends_on(AttachGateway)
        
        PrivateSubnet1 = ec2.CfnSubnet(
            self,'PrivateSubnet1',
            vpc_id=VPC.ref,
            cidr_block='10.1.3.0/24',
            availability_zone = core.Fn.select(0,core.Fn.get_azs(core.Aws.REGION)),
            tags=[{'key':'name','value':'edx-subnet-private-a'}])
        
        PublicSubnet1 = ec2.CfnSubnet(self,'PublicSubnet1',
        availability_zone = core.Fn.select(0,core.Fn.get_azs(core.Aws.REGION)),
        cidr_block = '10.1.1.0/24',
        vpc_id = VPC.ref,
        map_public_ip_on_launch = True,
        tags = [{
            'key':'Name',
            'value':'edx-subnet-public-a'
        }])
        
        NAT1 = ec2.CfnNatGateway(self, 'NAT1',subnet_id=PublicSubnet1.ref, allocation_id=alloc_id)
        NAT1.add_depends_on(AttachGateway)
        NAT1.node.add_dependency(EIP1)
        
        PrivateRouteTable1 = ec2.CfnRouteTable(
            self,'PrivateRouteTable1',
            vpc_id=VPC.ref,
            tags=[{
                'key':'Name',
                'value':'edx-routetable-private1'
            }])
            
#PrivateRoute1: Type: AWS::EC2::Route Properties:RouteTableId: Ref: PrivateRouteTable1 DestinationCidrBlock: 0.0.0.0/0 NatGatewayId: Ref: NAT1
        PrivateRoute1 = ec2.CfnRoute(
            self,'PrivateRoute1',
            route_table_id=PrivateRouteTable1.ref,
            destination_cidr_block='0.0.0.0/0',
            nat_gateway_id=NAT1.ref
            )
            
        PrivateRouteAssociation1 = ec2.CfnSubnetRouteTableAssociation(
            self,'PrivateRouteAssociation1',
            route_table_id=PrivateRouteTable1.ref,
            subnet_id=PrivateSubnet1.ref
            )
            
#PublicRouteTable: Type: 'AWS::EC2::RouteTable'
#Properties: VpcId: !Ref VPC Tags: - Key: Name Value: edx-routetable-public
        PublicRouteTable = ec2.CfnRouteTable(
            self,'PublicRouteTable',
            vpc_id=VPC.ref,
            tags=[{
                'key':'Name','value':'edx-routetable-public'
            }])
            
#PublicDefaultRoute: Type: 'AWS::EC2::Route' DependsOn: AttachGateway
#Properties: DestinationCidrBlock: 0.0.0.0/0 GatewayId: !Ref InternetGateway RouteTableId: !Ref PublicRouteTable
        PublicDefaultRoute = ec2.CfnRoute(
            self, 'PublicDefaultRoute',
            route_table_id=PublicRouteTable.ref,
            destination_cidr_block='0.0.0.0/0',
            gateway_id=InternetGateway.ref
        )
        
#PublicRouteAssociation1:Type: 'AWS::EC2::SubnetRouteTableAssociation'
#Properties:RouteTableId: !Ref PublicRouteTable SubnetId: !Ref PublicSubnet1
        PublicRouteAssociation1 = ec2.CfnSubnetRouteTableAssociation(
            self, 'PublicRouteAssociation1',
            route_table_id=PublicRouteTable.ref,
            subnet_id=PublicSubnet1.ref
        )


#EIP2:Type: AWS::EC2::EIP Properties:Domain: vpc
        EIP2 = ec2.CfnEIP(self, 'EIP2',domain='vpc')
        alloc_id = EIP2.get_att('AllocationId').to_string()
        EIP2.add_depends_on(AttachGateway)


# PrivateSubnet2:Type: 'AWS::EC2::Subnet'
# Properties: AvailabilityZone: !Select  - '1' - !GetAZs ''
# CidrBlock: 10.1.4.0/24 VpcId: !Ref VPC Tags: - Key: Name Value: edx-subnet-private-b
        PrivateSubnet2 = ec2.CfnSubnet(
            self,'PrivateSubnet2',
            vpc_id=VPC.ref,
            cidr_block='10.1.4.0/24',
            availability_zone = core.Fn.select(1,core.Fn.get_azs(core.Aws.REGION)),
            tags=[{
                'key':'Name',
                'value':'edx-subnet-private-b'
                }])
                
#PublicSubnet2:Type: 'AWS::EC2::Subnet'
#Properties: AvailabilityZone: !Select  - '1' - !GetAZs ''
#CidrBlock: 10.1.2.0/24 VpcId: !Ref VPC MapPublicIpOnLaunch: 'true' Tags: Key: Name Value: edx-subnet-public-b
        PublicSubnet2 = ec2.CfnSubnet(self,'PublicSubnet2',
        availability_zone = core.Fn.select(1,core.Fn.get_azs(core.Aws.REGION)),
        cidr_block = '10.1.2.0/24',
        vpc_id = VPC.ref,
        map_public_ip_on_launch = True,
        tags = [{
            'key':'Name',
            'value':'edx-subnet-public-b'
        }])
        
        NAT2 = ec2.CfnNatGateway(self, 'NAT2',subnet_id=PublicSubnet2.ref, allocation_id=alloc_id)
        NAT2.add_depends_on(AttachGateway)
        NAT2.node.add_dependency(EIP2)

        PrivateRouteTable2 = ec2.CfnRouteTable(
            self,'PrivateRouteTable2',
            vpc_id=VPC.ref,
            tags=[{
                'key':'Name',
                'value':'edx-routetable-private2'
            }])
            
        PrivateRoute2 = ec2.CfnRoute(
            self,'PrivateRoute2',
            route_table_id=PrivateRouteTable2.ref,
            destination_cidr_block='0.0.0.0/0',
            nat_gateway_id=NAT2.ref
            )
            
        PrivateRouteAssociation2 = ec2.CfnSubnetRouteTableAssociation(
            self,'PrivateRouteAssociation2',
            route_table_id=PrivateRouteTable2.ref,
            subnet_id=PrivateSubnet2.ref
            )
    
#PublicRouteAssociation2:Type: 'AWS::EC2::SubnetRouteTableAssociation'
#Properties:RouteTableId: !Ref PublicRouteTable SubnetId: !Ref PublicSubnet1
        PublicRouteAssociation2 = ec2.CfnSubnetRouteTableAssociation(
            self, 'PublicRouteAssociation2',
            route_table_id=PublicRouteTable.ref,
            subnet_id=PublicSubnet2.ref
        )


        core.CfnOutput(self, 'vpcoutput',
            value = VPC.ref,
            description = 'VPC',
            export_name = 'vpc'
        )
        core.CfnOutput(self, 'PublicSubnet1output',
            value = PublicSubnet1.ref,
            description = 'Public Subnet 1',
            export_name = 'PublicSubnet1'
        )
        core.CfnOutput(self, 'PublicSubnet2output',
            value = PublicSubnet2.ref,
            description = 'Public Subnet 2',
            export_name = 'PublicSubnet2'
        )
        core.CfnOutput(self, 'PrivateSubnet1output',
            value = PrivateSubnet1.ref,
            description = 'Private Subnet 1',
            export_name = 'PrivateSubnet1'
        )

        core.CfnOutput(self, 'PrivateSubnet2output',
            value = PrivateSubnet2.ref,
            description = 'Private Subnet 2',
            export_name = 'PrivateSubnet2'
        )
        
        
        core.CfnOutput(self, 'Private1az',
            value = PrivateSubnet1.attr_availability_zone,
            description = 'PrivateSubnet1 az',
            export_name = 'PrivateSubnet1az'
        )
        
        core.CfnOutput(self, 'Private2az',
            value = PrivateSubnet2.attr_availability_zone,
            description = 'PrivateSubnet2 az',
            export_name = 'PrivateSubnet2az'
        )
        