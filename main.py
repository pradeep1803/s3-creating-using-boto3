# main.py

from functions import (
    list_buckets_and_objects,
    scrape_website,
    create_s3_bucket,
    disable_block_public_access,
    upload_file_to_s3,
    enable_static_website_hosting,
    set_bucket_policy,
)
from variables import *
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Main logic
if __name__ == "__main__":
    print("\n--- Static Website Hosting with S3 ---\n")
    
    bucket_objects = list_buckets_and_objects(region_name)
    for bucket_name, objects in bucket_objects.items():
        print(f"Bucket: {bucket_name}")
        if objects:
            print(f"  Objects:")

            for obj in objects:
                print(f"    - {obj}")
        else:
            print("  No objects found.")
        print()
    s3=boto3.client('s3')
    response=s3.list_buckets()
    if not response['Buckets']:
        bucket_name = input("Enter your unique bucket name: ").strip()  # Your unique bucket name
        if not bucket_name or not website_url.startswith("http"):
            print("Error: Please provide a valid bucket name and website URL.")
        else:
            try:
                # 1. Scrape website content
                file_name = scrape_website(website_url)
                if not file_name:
                    exit()

                # 2. Initialize S3 client
                s3_client = boto3.client('s3', region_name=region)

                # 3. Create S3 bucket
                if not create_s3_bucket(s3_client, bucket_name, region):
                    exit()

                # 4. Disable block public access
                disable_block_public_access(s3_client, bucket_name)

                # 5. Upload index.html to the bucket
                upload_file_to_s3(s3_client, file_name, bucket_name)

                # 6. Enable static website hosting
                enable_static_website_hosting(s3_client, bucket_name)

                # 7. Set bucket policy for public read access
                set_bucket_policy(s3_client, bucket_name)

                # 8. Get the static website endpoint
                website_endpoint = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
                print(f"Your website is hosted at: {website_endpoint}")

            except (NoCredentialsError, PartialCredentialsError):
                print("Error: AWS credentials not found or incomplete. Please configure them using AWS CLI or environment variables.")
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")

    else:
        
        try:
            # 1. Scrape website content
            file_name = scrape_website(website_url)
            if not file_name:
                exit()

                # 2. Initialize S3 client
            s3_client = boto3.client('s3', region_name=region)

                # 4. Disable block public access
            disable_block_public_access(s3_client, bucket_name)

                # 5. Upload index.html to the bucket
            upload_file_to_s3(s3_client, file_name, bucket_name)

                # 6. Enable static website hosting
            enable_static_website_hosting(s3_client, bucket_name)

                # 7. Set bucket policy for public read access
            set_bucket_policy(s3_client, bucket_name)

                # 8. Get the static website endpoint
            website_endpoint = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
            print(f"Your website is hosted at: {website_endpoint}")

        except (NoCredentialsError, PartialCredentialsError):
            print("Error: AWS credentials not found or incomplete. Please configure them using AWS CLI or environment variables.")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")