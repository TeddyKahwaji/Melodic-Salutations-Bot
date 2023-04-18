
def filterBlobName(blob: str) -> str: 
    words_to_clean = "voicelines/"
    return blob.replace(words_to_clean, "")