import boto3
import create_s3
import create_ec2_web
import create_alb
import register_ec2_alb
import create_launch_template
import create_ASG
import create_ASG_scale_in_out
import create_SNS
import delete_aws_component


# AWS Variables
s3_bucket_name = 'muzahidtestbuckets3'
region = 'ap-south-1'
vpcid = 'vpc-07e6e24c20a77665a'
subnetid = 'subnet-026f4fe578c3710b3'
securitygroupname = 'test-hv-sg'
imageid='ami-0c2af51e265bd5e0e'
instancetype='t2.micro'
keyname='test-hv'
userdata ='''#!/bin/bash
                    apt-get update
                    apt-get install -y python3-pip git nginx
                    git clone https://github.com/alitahir4024/Weather-API-Project.git /var/www/weather-api-project
                    cd /var/www/weather-api-project
                    systemctl stop nginx
                    echo 'server {' > /etc/nginx/sites-enabled/weather-api
                    echo '    listen 80 default_server;' >> /etc/nginx/sites-enabled/weather-api
                    echo '    listen [::]:80 default_server;' >> /etc/nginx/sites-enabled/weather-api
                    echo '    root /var/www/weather-api-project;' >> /etc/nginx/sites-enabled/weather-api
                    echo '    index index.html index.htm index.nginx-debian.html;' >> /etc/nginx/sites-enabled/weather-api
                    echo '    server_name _;' >> /etc/nginx/sites-enabled/weather-api
                    echo '    location / {' >> /etc/nginx/sites-enabled/weather-api
                    echo '        try_files $uri $uri/ =404;' >> /etc/nginx/sites-enabled/weather-api
                    echo '    }' >> /etc/nginx/sites-enabled/weather-api
                    echo '}' >> /etc/nginx/sites-enabled/weather-api
                    cp /etc/nginx/sites-enabled/weather-api /etc/nginx/sites-enabled/default
                    rm /etc/nginx/sites-enabled/weather-api
                    systemctl restart nginx
                    systemctl enable nginx
                    '''
alb_name = 'Test-HV-ALB'
subnet =[
            'subnet-026f4fe578c3710b3',
            'subnet-0d1254c10bc81bd4c'
        ]
securitygroups=['sg-0fccc5cc345e23eef']
lbtype = 'application'
applicationLoadBalancerArn = 'arn:aws:elasticloadbalancing:ap-south-1:471112564396:loadbalancer/app/Test-HV-ALB/156d052f079b6a53'
targetGroupName='Test-80-TG'
targetGroupProtocol='HTTP'
targetGroupPort=80
targetGroupHealthCheckProtocol='HTTP'
targetGroupTargetType='instance'
ec2InstanceId = 'i-0a6830f77a9fbc319'
image_id = 'ami-0a9e94a4a9b7eb553'
template_name = 'Test-HV-LT-1'
template_id = 'lt-0239d999470935bb6'
asg_name = 'Test-HV-ASG'
vpc_zone_identifier = 'subnet-026f4fe578c3710b3,subnet-0d1254c10bc81bd4c'
min_size = 1
max_size = 1
desired_capacity = 1
tags = [
    {'Key': 'Environment', 'Value': 'EHES', 'PropagateAtLaunch': True}
]
target_group_arns = [
    'arn:aws:elasticloadbalancing:ap-south-1:471112564396:targetgroup/Test-80-TG/94d9b904cdfb8dc2'
]

security_group_id = 'sg-0fccc5cc345e23eef'



# create S3 bucket
create_s3.create_s3_bucket(s3_bucket_name, region)


# create ec2 and deploy web service using nginx
create_ec2_web.create_ec2_instance(vpcid, subnetid, securitygroupname, imageid, instancetype, keyname, userdata)


# Create application Load Balancer
alb_arn_response = create_alb.create_application_load_balancer(alb_name, subnet, securitygroups, lbtype)
print("Load Balancer ARN:", alb_arn_response)


# Create Target group and Listener and then attach to ALB
register_ec2_alb_response = register_ec2_alb.create_alb_target_group(applicationLoadBalancerArn, targetGroupName, targetGroupProtocol, targetGroupPort, 
                                                                     vpcid, targetGroupHealthCheckProtocol, targetGroupTargetType, ec2InstanceId)


# Create Launch Template for auto scaling Group
template_id = create_launch_template.create_launch_templates(ec2InstanceId, image_id, template_name, region)
if template_id:
        print(f"Successfully created Launch Template: {template_id}")
else:
    print("Failed to create Launch Template")


# Create Auto scaling Group using launch template
target_group_arns = [
    'arn:aws:elasticloadbalancing:ap-south-1:471112564396:targetgroup/Test-80-TG/94d9b904cdfb8dc2'
]

create_ASG.create_auto_scaling_group(template_id, asg_name, vpc_zone_identifier, min_size, max_size, desired_capacity, target_group_arns, region)


# Configure scaling policies to scale in/out based on metrics like CPU utilization or network traffic
if create_ASG_scale_in_out.create_auto_scaling_group(template_id, asg_name, vpc_zone_identifier, min_size, max_size, desired_capacity, tags, target_group_arns, region):
    # Create scaling policies
    scale_out_policy_arn = create_ASG_scale_in_out.create_scaling_policy(asg_name, 'ScaleOutPolicy', 1, 'SimpleScaling', region)
    scale_in_policy_arn = create_ASG_scale_in_out.create_scaling_policy(asg_name, 'ScaleInPolicy', -1, 'SimpleScaling', region)
    
    if scale_out_policy_arn and scale_in_policy_arn:
        # Create CloudWatch alarms
        create_ASG_scale_in_out.create_cloudwatch_alarm(
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
        create_ASG_scale_in_out.create_cloudwatch_alarm(
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


# Create SNS topic for Health Aleart, Scaling events and High Traffic Alert
health_issues_topic_arn = create_SNS.create_sns_topic('HealthAlerts', region)
scaling_events_topic_arn = create_SNS.create_sns_topic('ScalingEvents', region)
high_traffic_topic_arn = create_SNS.create_sns_topic('HighTrafficAlerts', region)

print("Health Alerts Topic ARN:", health_issues_topic_arn)
print("Scaling Events Topic ARN:", scaling_events_topic_arn)
print("High Traffic Alerts Topic ARN:", high_traffic_topic_arn)

# subscribe to SNS topic
create_SNS.subscribe_to_topic(health_issues_topic_arn, 'email', 'muzahidalig@gmail.com', region)
create_SNS.subscribe_to_topic(scaling_events_topic_arn, 'sms', '+919711183926', region)
create_SNS.subscribe_to_topic(high_traffic_topic_arn, 'email', 'muzahidalig@gmail.com', region)

#CPU utilization alarm for EC2 instance health
create_SNS.create_cloudwatch_alarm(alarm_name='HighCPUUtilization', metric_name='CPUUtilization', namespace='AWS/EC2',
                                   statistic='Average', threshold=80.0, comparison_operator='GreaterThanThreshold', 
                                   evaluation_periods=1, sns_topic_arn=health_issues_topic_arn, region=region)

#ELB high traffic alarm
create_SNS.create_cloudwatch_alarm(alarm_name='HighRequestCount', metric_name='RequestCount', namespace='AWS/ELB',
                                   statistic='Sum', threshold=1000.0, comparison_operator='GreaterThanThreshold',
                                   evaluation_periods=1, sns_topic_arn=high_traffic_topic_arn, region=region)

# Auto Scaling group notofication
create_SNS.create_autoscaling_notification('YourAutoScalingGroupName', scaling_events_topic_arn, region)


# Delete AWS components created above
delete_aws_component.terminate_instance_and_security_group(ec2InstanceId, security_group_id)
delete_aws_component.delete_ami(image_id)
delete_aws_component.delete_auto_scaling_group(asg_name)
delete_aws_component.delete_launch_template(template_id)
delete_aws_component.delete_load_balancer_and_target_group(applicationLoadBalancerArn, target_group_arns)
delete_aws_component.delete_all_sns_topics()
delete_aws_component.delete_all_cloudwatch_alarms()