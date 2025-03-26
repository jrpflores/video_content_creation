from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

class GoogleDriveUploader:
    def __init__(self, credentials_file: str):
        self.scopes = ['https://www.googleapis.com/auth/drive.file']
        self.creds = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=self.scopes
        )
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def upload_file(self, file_path: str, file_name: str, folder_id: str = None) -> str:
        file_metadata = {"name": file_name}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

        print(f"File uploaded successfully! File ID: {file.get('id')}")
        return file.get('id')