import boto3
def create_s3_bucket(s3_bucket_name, aws_region):
    try:
        s3_client = boto3.client('s3', region_name=aws_region)
        s3_client.create_bucket(Bucket=s3_bucket_name, 
                                CreateBucketConfiguration=
                                {'LocationConstraint': aws_region})
    except Exception as e:
        print(f'Error: {e}')
        return False
    
    return True

create_s3_bucket('muzahidtestbuckets3', 'ap-south-1')