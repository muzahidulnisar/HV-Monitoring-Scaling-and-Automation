import boto3

def create_auto_scaling_group(template_id, asg_name, vpc_zone_identifier, min_size, max_size, desired_capacity, tags, target_group_arns, region):
    asg_client = boto3.client('autoscaling', region_name=region)
    
    try:
        response = asg_client.create_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            LaunchTemplate={
                'LaunchTemplateId': template_id
            },
            MinSize=min_size,
            MaxSize=max_size,
            DesiredCapacity=desired_capacity,
            VPCZoneIdentifier=vpc_zone_identifier,
            TargetGroupARNs=target_group_arns,
            Tags=tags
        )
        print(f"Auto Scaling Group created with name: {asg_name}")
    except Exception as e:
        print(f"Error creating Auto Scaling Group: {e}")

if __name__ == "__main__":
    template_id = 'lt-0239d999470935bb6'
    asg_name = 'Test-HV-ASG'
    vpc_zone_identifier = 'subnet-026f4fe578c3710b3,subnet-0d1254c10bc81bd4c'
    min_size = 1
    max_size = 1
    desired_capacity = 1
    region = 'ap-south-1'

    tags = [
        {'Key': 'Environment', 'Value': 'EHES', 'PropagateAtLaunch': True}
    ]

    target_group_arns = [
        'arn:aws:elasticloadbalancing:ap-south-1:471112564396:targetgroup/Test-80-TG/94d9b904cdfb8dc2'
    ]

    create_auto_scaling_group(template_id, asg_name, vpc_zone_identifier, min_size, max_size, desired_capacity, tags, target_group_arns, region)

