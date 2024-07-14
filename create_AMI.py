import boto3

def create_ami_with_tags(instance_id, ami_name, region):
    ec2_client = boto3.client('ec2', region_name=region)

    try:
        # Create AMI
        response = ec2_client.create_image(
            InstanceId=instance_id,
            Name=ami_name,
            NoReboot=True
        )
        ami_id = response['ImageId']
        print(f"AMI created with ID: {ami_id}")

        #create Tags for AMI
        tags = [
        {'Key': 'Name', 'Value': 'Test-HV'},
        {'Key': 'Environment', 'Value': 'EHES'}
        ]

        # Add tags to the created AMI
        ec2_client.create_tags(
            Resources=[ami_id],
            Tags=tags
        )
        print(f"Tags added to AMI: {ami_id}")

        return ami_id
    except Exception as e:
        print(f"Error creating AMI: {e}")
        return None

if __name__ == "__main__":
    instance_id = 'i-0a6830f77a9fbc319'
    ami_name = 'Test-HV'
    region = 'ap-south-1'

    ami_id = create_ami_with_tags(instance_id, ami_name, region)
    if ami_id:
        print(f"Successfully created AMI: {ami_id}")
    else:
        print("Failed to create AMI")
