from firebase_admin import credentials, firestore, initialize_app
from google.cloud import storage
from utils import *
from uuid import uuid4
import tempfile
import requests
import datetime
from google.oauth2 import service_account
from constants import *



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
    
    def insertElementInCollectionWithDefault(self, collectionName: str, documentName: str, data:dict) -> bool: 
        try: 
            if not self.documentExistsInCollection(collectionName, documentName): 
                self.db.collection(collectionName).document(documentName).set(data)
            else: 
                self.db.collection(collectionName).document(documentName).update(data)    
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
        
    def getAudioFile(self, audioFileName: str) -> str | None:
        blobs = self.storage_client.list_blobs(BUCKET_NAME)
        potentialBlob = list(filter(lambda e: audioFileName ==
                             e.name.replace("voicelines/", ""), blobs))
        if len(potentialBlob) == 0:
            return None

        return potentialBlob[0].generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=15), method="GET")

    def uploadAudioFile(self, audioFileName:str, downloadUrl: str)-> tuple[bool, str]:  
        try: 
            bucket = self.storage_client.get_bucket(BUCKET_NAME)
            blob = bucket.blob(blob_name=f"voicelines/{audioFileName}")
            req = requests.get(downloadUrl)
            content = req.content
            token = uuid4()
            metadata = {"firebaseStorageDownloadTokens": token}
            temp_file= tempfile.TemporaryFile()
            temp_file.write(content)
            blob.metadata = metadata
            blob.upload_from_file(temp_file, rewind=True, content_type="audio/mpeg")
            temp_file.close()
            return True, blob.generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=20), method="GET")
        except:
            return False, ""