import boto3


# Create the target group
def create_alb_target_group(applicationLoadBalancerArn, targetGroupName, targetGroupProtocol,
                        targetGroupPort, targetGroupVpcId, targetGroupHealthCheckProtocol,
                        targetGroupTargetType, ec2InstanceId):
    alb_client = boto3.client('elbv2')
    
    alb_arn = applicationLoadBalancerArn

    tg_response = alb_client.create_target_group(
        Name=targetGroupName,
        Protocol=targetGroupProtocol,
        Port=targetGroupPort,
        VpcId=targetGroupVpcId,
        HealthCheckProtocol=targetGroupHealthCheckProtocol,
        HealthCheckPath='/',
        TargetType=targetGroupTargetType,
        IpAddressType='ipv4',
        Tags=[
            {
                'Key': 'environment',
                'Value': 'EHES'
            }
        ]
    )

    # Get the Target Group ARN
    tg_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
    print("Target Group ARN:", tg_arn)

    # Register the instance with the target group
    alb_client.register_targets(
        TargetGroupArn=tg_arn,
        Targets=[
            {
                'Id': ec2InstanceId,
                'Port': targetGroupPort
            }
        ]
    )

    # Create the listener
    listener_response = alb_client.create_listener(
        LoadBalancerArn=alb_arn,
        Protocol=targetGroupProtocol,
        Port=targetGroupPort,
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': tg_arn
            }
        ]
    )

    print("Listener ARN:", listener_response['Listeners'][0]['ListenerArn'])
    return (tg_arn, listener_response['Listeners'][0]['ListenerArn'])

applicationLoadBalancerArn = 'arn:aws:elasticloadbalancing:ap-south-1:471112564396:loadbalancer/app/Test-HV-ALB/156d052f079b6a53'
targetGroupName='Test-80-TG'
targetGroupProtocol='HTTP'
targetGroupPort=80
targetGroupVpcId='vpc-07e6e24c20a77665a'
targetGroupHealthCheckProtocol='HTTP'
targetGroupTargetType='instance'
ec2InstanceId = 'i-0a6830f77a9fbc319'

create_alb_target_group(applicationLoadBalancerArn, targetGroupName, targetGroupProtocol,
                        targetGroupPort, targetGroupVpcId, targetGroupHealthCheckProtocol, targetGroupTargetType,
                        ec2InstanceId)