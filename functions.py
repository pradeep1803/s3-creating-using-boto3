import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import requests
import json

def list_buckets_and_objects(region_name):


  s3 = boto3.client('s3', region_name=region_name)

  try:
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    bucket_objects = {}
    for bucket_name in buckets:
      try:
        objects = []
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
          if 'Contents' in page:
            objects.extend([obj['Key'] for obj in page['Contents']])
        bucket_objects[bucket_name] = objects
      except Exception as e:
        print(f"Error listing objects in bucket '{bucket_name}': {e}")
        bucket_objects[bucket_name] = [] 
    return bucket_objects
  except Exception as e:
    print(f"An error occurred: {e}")
    return {}
  
def scrape_website(website_url):
    """Scrape content from the specified website."""
    response = requests.get(website_url)
    if response.status_code == 200:
        file_name = "index.html"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Website content scraped and saved as '{file_name}'.")
        return file_name
    else:
        print(f"Failed to scrape the website. HTTP Status Code: {response.status_code}")
        return None
    
def create_s3_bucket(s3_client, bucket_name, region):
    """Create an S3 bucket."""
    try:
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Bucket '{bucket_name}' created successfully.")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket '{bucket_name}' already owned by you.")
    except s3_client.exceptions.BucketAlreadyExists:
        print(f"Bucket '{bucket_name}' already exists. Use a unique bucket name.")
        return False
    return True

def disable_block_public_access(s3_client, bucket_name):
    """Disable block public access for the bucket."""
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False
        }
    )
    print("Public access block disabled for the bucket.")

def upload_file_to_s3(s3_client, file_name, bucket_name):
    """Upload a file to the S3 bucket."""
    s3_client.upload_file(
        Filename=file_name,
        Bucket=bucket_name,
        Key="index.html",
        ExtraArgs={"ContentType": "text/html"}
    )
    print(f"File '{file_name}' uploaded to bucket '{bucket_name}'.")

def enable_static_website_hosting(s3_client, bucket_name):
    """Enable static website hosting on the S3 bucket."""
    s3_client.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            'IndexDocument': {'Suffix': 'index.html'},
        }
    )
    print(f"Static website hosting enabled on bucket '{bucket_name}'.")

def set_bucket_policy(s3_client, bucket_name):
    """Set bucket policy for public read access."""
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }
    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )
    print("Bucket policy applied for public read access.")