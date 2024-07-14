import boto3

alb_client = boto3.client('elbv2')

alb_arn = 'arn:aws:elasticloadbalancing:ap-south-1:471112564396:loadbalancer/app/Test-HV-ALB/156d052f079b6a53'

# Create the target group
tg_response = alb_client.create_target_group(
    Name='Test-80-TG',
    Protocol='HTTP',
    Port=80,
    VpcId='vpc-07e6e24c20a77665a',
    HealthCheckProtocol='HTTP',
    HealthCheckPath='/',
    TargetType='instance',
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

# Register the instance with the target group
alb_client.register_targets(
    TargetGroupArn=tg_arn,
    Targets=[
        {
            'Id': 'i-0a6830f77a9fbc319',
            'Port': 80
        }
    ]
)
print("Target Group ARN:", tg_arn)

# Create the listener
listener_response = alb_client.create_listener(
    LoadBalancerArn=alb_arn,
    Protocol='HTTP',
    Port=80,
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn': tg_arn
        }
    ]
)
print("Listener ARN:", listener_response['Listeners'][0]['ListenerArn'])
