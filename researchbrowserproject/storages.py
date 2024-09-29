from storages.backends.s3boto3 import S3Boto3Storage


class MediaStore(S3Boto3Storage):
    """
    Custom storage backend for handling media files in Amazon S3.

    This class extends the S3Boto3Storage to provide specific
    configurations for storing media files. It sets the storage
    location to "media" and prevents overwriting of files with
    the same name.
    """

    location = "media"
    file_overwrite = False
