import boto3

region = 'ap-south-1'

#Create SNS Topics
def create_sns_topic(topic_name, region):
    sns_client = boto3.client('sns', region_name=region)
    response = sns_client.create_topic(Name=topic_name)
    return response['TopicArn']

health_issues_topic_arn = create_sns_topic('HealthAlerts', region)
scaling_events_topic_arn = create_sns_topic('ScalingEvents', region)
high_traffic_topic_arn = create_sns_topic('HighTrafficAlerts', region)

print("Health Alerts Topic ARN:", health_issues_topic_arn)
print("Scaling Events Topic ARN:", scaling_events_topic_arn)
print("High Traffic Alerts Topic ARN:", high_traffic_topic_arn)

#Subscribe to the topic
def subscribe_to_topic(topic_arn, protocol, endpoint, region):
    sns_client = boto3.client('sns', region_name=region)
    sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol=protocol,
        Endpoint=endpoint
    )

subscribe_to_topic(health_issues_topic_arn, 'email', 'muzahidalig@gmail.com', region)
subscribe_to_topic(scaling_events_topic_arn, 'sms', '+919711183926', region)
subscribe_to_topic(high_traffic_topic_arn, 'email', 'muzahidalig@gmail.com', region)

#Create cloudwatch alarm for different health issues
def create_cloudwatch_alarm(alarm_name, metric_name, namespace, statistic, threshold, comparison_operator, evaluation_periods, sns_topic_arn, region):
    cloudwatch_client = boto3.client('cloudwatch', region_name=region)
    cloudwatch_client.put_metric_alarm(
        AlarmName=alarm_name,
        MetricName=metric_name,
        Namespace=namespace,
        Statistic=statistic,
        Threshold=threshold,
        ComparisonOperator=comparison_operator,
        EvaluationPeriods=evaluation_periods,
        AlarmActions=[sns_topic_arn]
    )

#CPU utilization alarm for EC2 instance health
create_cloudwatch_alarm(
    alarm_name='HighCPUUtilization',
    metric_name='CPUUtilization',
    namespace='AWS/EC2',
    statistic='Average',
    threshold=80.0,
    comparison_operator='GreaterThanThreshold',
    evaluation_periods=1,
    sns_topic_arn=health_issues_topic_arn,
    region=region
)


#ELB high traffic alarm
create_cloudwatch_alarm(
    alarm_name='HighRequestCount',
    metric_name='RequestCount',
    namespace='AWS/ELB',
    statistic='Sum',
    threshold=1000.0,
    comparison_operator='GreaterThanThreshold',
    evaluation_periods=1,
    sns_topic_arn=high_traffic_topic_arn,
    region=region
)

# Auto scaling notification notification 
def create_autoscaling_notification(asg_name, sns_topic_arn, region):
    autoscaling_client = boto3.client('autoscaling', region_name=region)
    autoscaling_client.put_notification_configuration(
        AutoScalingGroupName=asg_name,
        TopicARN=sns_topic_arn,
        NotificationTypes=[
            'autoscaling:EC2_INSTANCE_LAUNCH',
            'autoscaling:EC2_INSTANCE_TERMINATE',
            'autoscaling:EC2_INSTANCE_LAUNCH_ERROR',
            'autoscaling:EC2_INSTANCE_TERMINATE_ERROR'
        ]
    )

# Auto Scaling group Notification
create_autoscaling_notification('Test-HV-ASG', scaling_events_topic_arn, region)
