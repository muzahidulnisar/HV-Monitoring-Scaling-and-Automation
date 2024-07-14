import boto3

def get_security_group_id(ec2_client, s_group_name, vpc_id):
    try:
        #check security group
        response = ec2_client.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [s_group_name]},
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )
        security_groups = response['SecurityGroups']
        if security_groups:
            print(f'Security group {s_group_name} already exist. The Security Group Id is {security_groups[0]['GroupId']}')
            return security_groups[0]['GroupId']
        return None
    except Exception as e:
        print(f"Error checking for security group: {e}")
        return None


def create_security_group(ec2_client, s_group_name, vpc_id):
    try:
        # Create a new security group
        security_group = ec2_client.create_security_group(
            GroupName=s_group_name,
            Description='Security group for test-hv instance',
            VpcId=vpc_id
        )
        security_group_id = security_group['GroupId']
        print(f'New security group created successfully. The security group id is {security_group_id}')

        # security group tags
        security_group_tags = [
        {'Key': 'Name', 'Value': 'TestSecurityGroup'},
        {'Key': 'Environment', 'Value': 'EHES'}
        ]

        #Add tags to security group
        ec2_client.create_tags(
            Resources=[security_group_id],
            Tags=security_group_tags
        )

        # Add rules to the security group
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        return security_group_id
    except Exception as e:
        print(e)
        return None


def create_ec2_instance():
    ec2 = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')

    vpc_id = 'vpc-07e6e24c20a77665a'
    subnet_id = 'subnet-026f4fe578c3710b3'
    security_group_name = 'test-hv-sg'

    #check if the security group already exists
    security_group_id = get_security_group_id(ec2_client, security_group_name, vpc_id)
    if not security_group_id:
        #create new security group
        security_group_id = create_security_group(ec2_client, security_group_name, vpc_id)
        if not security_group_id:
            print('Failed to create security group')
            return None

    # Create the EC2 instance
    instances = ec2.create_instances(
        ImageId='ami-0c2af51e265bd5e0e',  # Ubuntu 22.04 AMI ID (Taken from AWS)
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='test-hv',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'Test'
                    },
                    {
                        'Key': 'Environment',
                        'Value': 'EHES'
                    }
                ]
            }
        ],
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'VolumeSize': 30,
                    'VolumeType': 'gp3',
                    'Iops': 3000,
                }
            }
        ],
        NetworkInterfaces=[{
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Ipv6AddressCount': 1,
            'SubnetId': subnet_id,
            'Groups': [security_group_id]
        }],
        UserData='''#!/bin/bash
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
    )

    instance_id = instances[0].id
    return instance_id

instance_id = create_ec2_instance()
print("Created instance with ID:", instance_id)