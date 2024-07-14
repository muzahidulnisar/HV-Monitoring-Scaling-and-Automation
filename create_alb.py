import boto3

def create_application_load_balancer(alb_name, subnet, securitygroups, lbtype):
    alb_client = boto3.client('elbv2')

    # Create the load balancer
    alb_response = alb_client.create_load_balancer(
        Name=alb_name,
        Subnets=subnet,
        SecurityGroups=securitygroups,
        Scheme='internet-facing',
        Tags=[
            {
                'Key': 'environment',
                'Value': 'EHES'
            }
        ],
        Type=lbtype,
        IpAddressType='ipv4'
    )

    # Get the Load Balancer ARN
    return alb_response['LoadBalancers'][0]['LoadBalancerArn']

alb_name = 'Test-HV-ALB'
subnet =[
            'subnet-026f4fe578c3710b3',
            'subnet-0d1254c10bc81bd4c'
        ]
securitygroups=['sg-0fccc5cc345e23eef']
lbtype = 'application'

alb_arn_response = create_application_load_balancer(alb_name, subnet, securitygroups, lbtype)
print("Load Balancer ARN:", alb_arn_response)