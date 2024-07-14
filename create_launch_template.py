import boto3

def create_launch_template(instance_id, image_id, template_name, region):
    ec2_client = boto3.client('ec2', region_name=region)
    try:
        # Describe the instance to get its configuration
        instance_details = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = instance_details['Reservations'][0]['Instances'][0]
        
        # Filter out unsupported attributes from block device mappings
        block_device_mappings = []
        for mapping in instance['BlockDeviceMappings']:
            ebs = mapping.get('Ebs', {})
            filtered_ebs = {key: ebs[key] for key in ebs if key in ['Encrypted', 'DeleteOnTermination', 'Iops', 'KmsKeyId', 'SnapshotId', 'VolumeSize', 'VolumeType', 'Throughput']}
            block_device_mappings.append({
                'DeviceName': mapping['DeviceName'],
                'Ebs': filtered_ebs
            })

        # Create launch template data
        launch_template_data = {
            'ImageId': image_id,
            'InstanceType': instance['InstanceType'],
            'KeyName': instance.get('KeyName'),
            'SecurityGroupIds': [sg['GroupId'] for sg in instance['SecurityGroups']],
            #'IamInstanceProfile': instance.get('IamInstanceProfile', {}).get('Arn'),
            'BlockDeviceMappings': block_device_mappings,
            #'UserData': instance.get('UserData', ''),
            #'InstanceMarketOptions': instance.get('InstanceMarketOptions')
        }
        
        # Create the launch template
        response = ec2_client.create_launch_template(
            LaunchTemplateName=template_name,
            LaunchTemplateData=launch_template_data
        )
        print(f"Launch Template created with ID: {response['LaunchTemplate']['LaunchTemplateId']}")

        # create Tags for launch Template
        tags = [
        {'Key': 'Name', 'Value': 'Test-HV-LT-1'},
        {'Key': 'Environment', 'Value': 'EHES'}
        ]

        #Add Tags to the launch template
        ec2_client.create_tags(
            Resources=[response['LaunchTemplate']['LaunchTemplateId']],
            Tags=tags
        )

        return response['LaunchTemplate']['LaunchTemplateId']
    except Exception as e:
        print(f"Error creating Launch Template: {e}")
        return None

if __name__ == "__main__":
    instance_id = 'i-0a6830f77a9fbc319'
    image_id = 'ami-0a9e94a4a9b7eb553'
    template_name = 'Test-HV-LT-1'
    region = 'ap-south-1'

    template_id = create_launch_template(instance_id, image_id, template_name, region)
    if template_id:
        print(f"Successfully created Launch Template: {template_id}")
    else:
        print("Failed to create Launch Template")
