from firebase_admin import credentials, firestore, initialize_app
from discord import File, Member
from google.cloud import storage
from utils import *
from uuid import uuid4
import io
import tempfile
import zipfile
import requests
import datetime
from google.oauth2 import service_account
from constants import *
import asyncio


class FireBaseApi:
    def __init__(self):
        initialize_app(credentials.Certificate(CREDENTIALS_DICT))
        self.db = firestore.client()
        credentialss = service_account.Credentials.from_service_account_info(
            CREDENTIALS_DICT)
        self.storage_client = storage.Client(
            project="twitterbot-e7ab0", credentials=credentialss)

    def getElementFromCollection(self, collectionName: str, documentName: str) -> dict | None:
        collection = self.db.collection(collectionName)
        requestedDocument = collection.document(documentName)
        return requestedDocument.get().to_dict()

    def insertElementInCollectionWithDefault(self, collectionName: str, documentName: str, data: dict) -> bool:
        try:
            if not self.documentExistsInCollection(collectionName, documentName):
                self.db.collection(collectionName).document(
                    documentName).set(data)
            else:
                self.db.collection(collectionName).document(
                    documentName).update(data)
            return True
        except:
            return False

    def removeDocumentFromCollection(self, collectionName: str, documentName: str) -> bool:
        try:
            self.db.collection(collectionName).document(documentName).delete()
            return True
        except:
            return False

    def documentExistsInCollection(self, collectionName: str, documentName: str) -> bool:
        try:
            collection = self.db.collection(collectionName)
            requestedDocument = collection.document(documentName)
            return requestedDocument.get().exists
        except:
            return False

    async def deleteAudioFile(self, audioFileName: str) -> bool:
        try:
            bucket = self.storage_client.get_bucket(BUCKET_NAME)
            blob = bucket.get_blob(blob_name=f"voicelines/{audioFileName}")
            blob.delete()
            return True, audioFileName
        except:
            return False, audioFileName

    async def getAudioFile(self, audioFileName: str) -> str | None:
        bucket = self.storage_client.get_bucket(BUCKET_NAME)
        blob = bucket.get_blob(blob_name=f"voicelines/{audioFileName}")
        if blob is None:
            return None, ""

        return blob.generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=15), method="GET"), audioFileName

    async def uploadMassZip(self, member_voice_lines: list[str], zip_file: File, member: Member) -> tuple[bool, list[str]]:
        try:
            results = []
            zip_file_content = await zip_file.read()
            zf = zipfile.ZipFile(file=io.BytesIO(zip_file_content))
            filesToUpload = set()
            for file in zf.namelist():
                if file.split(".")[-1] not in ["mp3", 'm4a']:
                    results.append({"file": file, "success": False,
                                    "error_message": "file must be an mp3 or mp4 file!"})
                elif file in member_voice_lines:
                    results.append(
                        {"file": file, "success": False, "error_message": f"voiceline with the title {file} already exists for {member.name}"})
                else:
                    filesToUpload.add(file)

            uploadResults = await asyncio.gather(
                *[self.uploadAudioFileWithoutDownloading(
                    zf, file) for file in filesToUpload])

            for success, url, file in uploadResults:
                results.append(
                    {"file": file, "success": success, "error_message": url if not success else "", "url": url})

            return True, results
        except:
            return False, []

    async def uploadAudioFileWithoutDownloading(self, zf: zipfile.ZipFile, fileName: str) -> tuple[bool, str]:
        try:
            with zf.open(fileName) as f:
                token = uuid4()
                bucket = self.storage_client.get_bucket(BUCKET_NAME)
                metadata = {"firebaseStorageDownloadTokens": token}
                blob = bucket.blob(blob_name=f"voicelines/{fileName}")
                blob.metadata = metadata
                blob.upload_from_file(
                    f, rewind=True, content_type="audio/mpeg")
                return True, blob.generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=20), method="GET"), fileName
        except Exception as e:
            return False, e, fileName

    def uploadAudioFile(self, audioFileName: str, downloadUrl: str) -> tuple[bool, str]:
        try:
            bucket = self.storage_client.get_bucket(BUCKET_NAME)
            blob = bucket.blob(blob_name=f"voicelines/{audioFileName}")
            req = requests.get(downloadUrl)
            content = req.content
            token = uuid4()
            metadata = {"firebaseStorageDownloadTokens": token}
            temp_file = tempfile.TemporaryFile()
            temp_file.write(content)
            blob.metadata = metadata
            blob.upload_from_file(temp_file, rewind=True,
                                  content_type="audio/mpeg")
            temp_file.close()
            return True, blob.generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=20), method="GET")
        except:
            return False, ""
