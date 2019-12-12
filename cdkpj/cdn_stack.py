from aws_cdk import (
    aws_ec2 as ec2,
    aws_cloudfront as cloudfront,
    aws_elasticloadbalancingv2 as elb,
    aws_iam as iam,
    aws_apigateway as apig,
    core
)


class cdnstack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        Api = apig.CfnRestApi(
            self,'Api',
            name = 'WebProxyApi',
            binary_media_types= ['*/*']
            )
        
        WebpageCDN = cloudfront.CfnDistribution(self,'WebpageCDN',
        distribution_config = {
            'DefaultCacheBehavior':{
                'AllowedMethods':['DELETE','GET','HEAD','OPTIONS','PATCH','POST','PUT'],
                'MaxTTL':0,
                'MinTTL':0,
                'DefaultTTL':0,
                'ForwardedValues':{
                    'QueryString':True,
                    'Cookies':{'Forward':'all'},
                    'Headers':['Accept','Referer','Athorization','Content-Type']},
                'TargetOriginId':'website',
                'ViewerProtocolPolicy':'redirect-to-https'},
                'enabled':True,
                'Origins':[{
                    'DominName': '%s.execute-api.%s.amazonaws.com' % (Api.ref,core.Aws.REGION),
#core.Fn.sub('${Api}.execute-api.${AWS::Region}.amazonaws.com')
                    'Id':'website',
                    'OriginPath':'/Prod',
                    'CustomOriginConfig':{'OriginProtocolPolicy':'https-only'}
                }],
                'PriceClass':'PriceClass_All'
        })
                
        LoadBalancer = elb.CfnLoadBalancer(self,'LoadBalancer',
        subnets=[core.Fn.import_value('PublicSubnet1output'),core.Fn.import_value('PublicSubnet2output')],
        load_balancer_attributes =[{'key':'idle_timeout.timeout_seconds','value':'50'}],
        security_groups = [core.Fn.import_value('WebSecurityGroupoutput')])
        
        CloudWatchRole = iam.CfnRole(
            self,'CloudWatchRole',
            assume_role_policy_document={
                'Version':'2012-10-17',
                'Statement':{
                    'Effect':'Allow',
                    'Principal':{'Service':'apigateway.amazonaws.com'},
                    'Action':'sts:AssumeRole'}},
            path = '/',
            managed_policy_arns =[
                'arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs',
                'arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess']
            )
            
        Account = apig.CfnAccount(
            self,'Account',
            cloud_watch_role_arn = CloudWatchRole.attr_arn)
        
        Resource = apig.CfnResource(
            self,'ApiResource',
            parent_id = Api.attr_root_resource_id,
            rest_api_id = Api.ref,
            path_part = '{proxy+}')
            
        RootMethod = apig.CfnMethod(
            self,'rootmethod',
            http_method = 'ANY',
            resource_id = Api.attr_root_resource_id,
            rest_api_id = Api.ref,
            authorization_type = None,
            integration = {
                'indentationError':'ANY',
                'type': 'HTTP_PROXY',
                'uri' : 'http://'+LoadBalancer.attr_dns_name,
                'passthroughBehavior':'WHEN_NO_MATCH',
                'integrationResponses':[{'statusCode':'200'}]
                })
                
        ProxyMethod = apig.CfnMethod(
            self,'ProxyMehod',
            http_method='ANY',
            resource_id = Resource.ref,
            rest_api_id = Api.ref,
            authorization_type = None,
            request_parameters = {'method.request.path.proxy': True},
            integration = {
                'cacheKeyParameters':['method.request.path.proxy'],
                'requestParameters':{'integration.request.path.proxy':'method.request.path.prxy'},
                'integrationHttpMethod':'ANY',
                'type':'HTTP_PROXY',
                'uri':'http://'+LoadBalancer.attr_dns_name+'/{proxy}',
                'passthroughBehavior':'WHEN_NO_MATCH',
                'integrationResponses':[{'statusCode':'200'}]
                })
        
        Deployment = apig.CfnDeployment(
            self,'Deployment',
            rest_api_id=Api.ref)
        
        Deployment.add_depends_on(RootMethod)
        Deployment.add_depends_on(ProxyMethod)
        
        ProdStage = apig.CfnStage(
            self,'ProdStage',
            stage_name = 'Prod',
            description = 'Prod Stage',
            rest_api_id = Api.ref,
            deployment_id = Deployment.ref,
            tracing_enabled = True)
            
#OutPut
        core.CfnOutput(
            self,'alb_dns_name',
            value = LoadBalancer.attr_dns_name,
            description = 'ALB DNS NAME')
        
        core.CfnOutput(
            self,'domain_name',
            value = WebpageCDN.attr_domain_name,
            description = 'Webpage CloudFront Domain Name')
            
        core.CfnOutput(
            self,'LoadBalancerArn',
            value = LoadBalancer.ref)