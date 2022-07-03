
class FileIsAlreadyExist(Exception):
    """raise if file exists in storage"""

class RemoveNotYourFile(Exception):
    """raise if user wants to remove another user's file"""
