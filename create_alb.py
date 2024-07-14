import boto3

alb_client = boto3.client('elbv2')

# Create the load balancer
alb_response = alb_client.create_load_balancer(
    Name='Test-HV-ALB',
    Subnets=[
        'subnet-026f4fe578c3710b3',
        'subnet-0d1254c10bc81bd4c'
    ],
    SecurityGroups=[
        'sg-0fccc5cc345e23eef'
    ],
    Scheme='internet-facing',
    Tags=[
        {
            'Key': 'environment',
            'Value': 'EHES'
        }
    ],
    Type='application',
    IpAddressType='ipv4'
)

# Get the Load Balancer ARN
alb_arn = alb_response['LoadBalancers'][0]['LoadBalancerArn']

print("Load Balancer ARN:", alb_arn)