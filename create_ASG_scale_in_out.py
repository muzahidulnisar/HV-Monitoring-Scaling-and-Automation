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
        return True
    except Exception as e:
        print(f"Error creating Auto Scaling Group: {e}")
        return False

def create_scaling_policy(asg_name, policy_name, scaling_adjustment, policy_type, region):
    asg_client = boto3.client('autoscaling', region_name=region)
    
    try:
        response = asg_client.put_scaling_policy(
            AutoScalingGroupName=asg_name,
            PolicyName=policy_name,
            PolicyType=policy_type,
            AdjustmentType='ChangeInCapacity',
            ScalingAdjustment=scaling_adjustment,
            Cooldown=300
        )
        print(f"Scaling policy created with ARN: {response['PolicyARN']}")
        return response['PolicyARN']
    except Exception as e:
        print(f"Error creating scaling policy: {e}")
        return None

def create_cloudwatch_alarm(alarm_name, metric_name, namespace, threshold, comparison_operator, evaluation_periods, statistic, period, alarm_actions, region):
    cloudwatch_client = boto3.client('cloudwatch', region_name=region)
    
    try:
        response = cloudwatch_client.put_metric_alarm(
            AlarmName=alarm_name,
            MetricName=metric_name,
            Namespace=namespace,
            Threshold=threshold,
            ComparisonOperator=comparison_operator,
            EvaluationPeriods=evaluation_periods,
            Statistic=statistic,
            Period=period,
            AlarmActions=alarm_actions,
            Dimensions=[
                {
                    'Name': 'AutoScalingGroupName',
                    'Value': asg_name
                }
            ]
        )
        print(f"CloudWatch alarm created with name: {alarm_name}")
    except Exception as e:
        print(f"Error creating CloudWatch alarm: {e}")

if __name__ == "__main__":
    template_id = 'lt-0239d999470935bb6'
    asg_name = 'Test-HV-ASG'
    vpc_zone_identifier = 'subnet-026f4fe578c3710b3,subnet-0d1254c10bc81bd4c'
    min_size = 1
    max_size = 2
    desired_capacity = 1
    region = 'ap-south-1'

    tags = [
        {'Key': 'Environment', 'Value': 'EHES', 'PropagateAtLaunch': True}
    ]

    target_group_arns = [
        'arn:aws:elasticloadbalancing:ap-south-1:471112564396:targetgroup/Test-80-TG/94d9b904cdfb8dc2'
    ]

    if create_auto_scaling_group(template_id, asg_name, vpc_zone_identifier, min_size, max_size, desired_capacity, tags, target_group_arns, region):
        # Create scaling policies
        scale_out_policy_arn = create_scaling_policy(asg_name, 'ScaleOutPolicy', 1, 'SimpleScaling', region)
        scale_in_policy_arn = create_scaling_policy(asg_name, 'ScaleInPolicy', -1, 'SimpleScaling', region)
        
        if scale_out_policy_arn and scale_in_policy_arn:
            # Create CloudWatch alarms
            create_cloudwatch_alarm(
                'ScaleOutAlarm',
                'CPUUtilization',
                'AWS/EC2',
                70,
                'GreaterThanThreshold',
                1,
                'Average',
                300,
                [scale_out_policy_arn],
                region
            )
            create_cloudwatch_alarm(
                'ScaleInAlarm',
                'CPUUtilization',
                'AWS/EC2',
                30,
                'LessThanThreshold',
                1,
                'Average',
                300,
                [scale_in_policy_arn],
                region
            )
