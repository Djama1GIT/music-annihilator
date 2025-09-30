from src.server.errors import CustomError


class S3Error(CustomError):
    pass


class S3InitializingError(S3Error):
    pass


class S3FileNotFound(S3Error):
    pass


class BotoError(S3Error):
    pass


class BucketError(BotoError):
    pass

