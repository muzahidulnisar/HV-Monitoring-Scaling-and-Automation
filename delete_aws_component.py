import boto3

# Terminate EC2 Instance
def terminate_instance_and_security_group(instance_id, security_group_id):
    ec2 = boto3.client('ec2')
    ec2.terminate_instances(InstanceIds=[instance_id])
    ec2.get_waiter('instance_terminated').wait(InstanceIds=[instance_id])
    print(f"Terminated EC2 instance: {instance_id}")
    ec2.delete_security_group(GroupId=security_group_id)
    print(f"Deleted Security Group: {security_group_id}")

# Delete AMIs
def delete_ami(ami_id):
    ec2 = boto3.client('ec2')
    ec2.deregister_image(ImageId=ami_id)
    print(f"Deregistered AMI: {ami_id}")

# delete Auto Scaling Group
def delete_auto_scaling_group(asg_name):
    asg = boto3.client('autoscaling')
    ec2 = boto3.client('ec2')
    asg.delete_auto_scaling_group(AutoScalingGroupName=asg_name, ForceDelete=True)
    print(f"Deleted Auto Scaling Group: {asg_name}")
    

# delete Launch Template
def delete_launch_template(launch_template_id):
    ec2 = boto3.client('ec2')
    ec2.delete_launch_template(LaunchTemplateId=launch_template_id)
    print(f"Deleted Launch Template: {launch_template_id}")

# Delete Load Balancer and associated Target group
def delete_load_balancer_and_target_group(load_balancer_arn, target_group_arn):
    elb = boto3.client('elbv2')
    elb.delete_load_balancer(LoadBalancerArn=load_balancer_arn)
    print(f"Deleted Load Balancer: {load_balancer_arn}")
    waiter = elb.get_waiter('load_balancers_deleted')
    waiter.wait(LoadBalancerArns=[load_balancer_arn])
    elb.delete_target_group(TargetGroupArn=target_group_arn)
    print(f"Deleted Target Group: {target_group_arn}")

# delete all SNS topics
def delete_all_sns_topics():
    sns = boto3.client('sns')
    topics = sns.list_topics()
    for topic in topics['Topics']:
        topic_arn = topic['TopicArn']
        sns.delete_topic(TopicArn=topic_arn)
        print(f"Deleted SNS Topic: {topic_arn}")

# Delete all cloudwatch alarms
def delete_all_cloudwatch_alarms():
    cloudwatch = boto3.client('cloudwatch')
    alarms = cloudwatch.describe_alarms()
    alarm_names = [alarm['AlarmName'] for alarm in alarms['MetricAlarms']]
    if alarm_names:
        cloudwatch.delete_alarms(AlarmNames=alarm_names)
        print(f"Deleted CloudWatch Alarms: {', '.join(alarm_names)}")

# AWS variable details
instance_id = 'your_instance_id'
security_group_id = 'your_security_group_id'
ami_id = 'your_ami_id'
asg_name = 'your_auto_scaling_group_name'
launch_template_id = 'your_launch_template_id'
load_balancer_arn = 'your_load_balancer_arn'
target_group_arn = 'your_target_group_arn'

# Execute tasks
terminate_instance_and_security_group(instance_id, security_group_id)
delete_ami(ami_id)
delete_auto_scaling_group(asg_name)
delete_launch_template(launch_template_id)
delete_load_balancer_and_target_group(load_balancer_arn, target_group_arn)
delete_all_sns_topics()
delete_all_cloudwatch_alarms()
