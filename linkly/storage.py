from whitenoise.storage import CompressedManifestStaticFilesStorage

class CustomWhiteNoiseStorage(CompressedManifestStaticFilesStorage):
    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content, filename)
        except ValueError:
            # If the file is missing (like source maps), return the original name
            return name 