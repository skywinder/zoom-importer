from b2sdk.v1 import InMemoryAccountInfo
from b2sdk.v1 import B2Api
from environs import Env
import inquirer

def authenticate_and_get_bucket():
    # Initialize the B2 SDK
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)

    # Initialize the environment variables
    env = Env()
    env.read_env()

    # Check if the required environment variables are set
    if not env('B2_KEY_ID') or not env('B2_KEY') or not env('BUCKET'):
        print("Please set the B2_KEY_ID, B2_KEY, and BUCKET environment variables.")
        return None, None

    # Authenticate with Backblaze
    application_key_id = env('B2_KEY_ID')
    application_key = env('B2_KEY')
    try:
        b2_api.authorize_account('production', application_key_id, application_key)
    except Exception as e:
        print(f"Failed to authenticate with Backblaze: {e}")
        return None, None

    # Get the bucket
    bucket_name = env('BUCKET')
    try:
        bucket = b2_api.get_bucket_by_name(bucket_name)
    except Exception as e:
        print(f"Failed to get bucket: {e}")
        return None, None

    return b2_api, bucket

def create_shared_link(b2_api, bucket, file_name):
    # Generate a download authorization token
    valid_duration_in_seconds = 86400  # 1 day
    download_auth_token = bucket.get_download_authorization(file_name, valid_duration_in_seconds)

    # Create the shared link
    # shared_link = f"https://f002.backblazeb2.com/file/{bucket.name}/{file_name}?Authorization={download_auth_token}"
    # shared_link = f"https://s3.us-east-005.backblazeb2.com/file/{bucket.name}/{file_name}?Authorization={download_auth_token}"


    # Get the download URL for the file
    download_url = b2_api.get_download_url_for_file_name(bucket.name, file_name)

    # Create the shared link
    shared_link = f"{download_url}?Authorization={download_auth_token}"

    return shared_link

def list_files_in_bucket(b2_api, bucket):
    # List all files in the bucket
    files = [file_info.file_name for file_info, folder_name in bucket.ls(show_versions=False)]

    # Ask the user to choose a file
    questions = [
        inquirer.List('file',
                      message="Which file do you want to download?",
                      choices=files,
                      ),
    ]
    answers = inquirer.prompt(questions)

    # Create a shared link for the chosen file
    shared_link = create_shared_link(b2_api, bucket, answers['file'])
    print(shared_link)

if __name__ == "__main__":
    b2_api, bucket = authenticate_and_get_bucket()
    if b2_api and bucket:
        list_files_in_bucket(b2_api, bucket)