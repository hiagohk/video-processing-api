from .base import AppError


class VideoError(AppError):
    error_code = "video_error"
    http_status = 400


class InvalidVideoURLError(VideoError):
    error_code = "invalid_video_url"
    message = "The provided video URL is invalid"


class VideoNotFoundError(VideoError):
    error_code = "video_not_found"
    http_status = 404
    message = "Video request not found"


class VideoProcessingError(VideoError):
    error_code = "video_processing_failed"
    http_status = 500
    message = "Video processing failed"


class VideoDownloadError(VideoProcessingError):
    error_code = "video_download_failed"
    message = "Failed to download video metadata"