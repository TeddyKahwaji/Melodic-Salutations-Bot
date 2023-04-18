import os
from firebase_admin import credentials, firestore, initialize_app
from google.cloud import storage
from utils import *
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

    def getAudioFile(self, audioFileName: str) -> str | None:
        blobs = self.storage_client.list_blobs(BUCKET_NAME)
        potentialBlob = list(filter(lambda e: audioFileName ==
                             e.name.replace("voicelines/", ""), blobs))
        if len(potentialBlob) == 0:
            return None

        return potentialBlob[0].generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=15), method="GET")
