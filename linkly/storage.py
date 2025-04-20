from whitenoise.storage import CompressedStaticFilesStorage

class CustomWhiteNoiseStorage(CompressedStaticFilesStorage):
    def url(self, name, **kwargs):
        try:
            return super().url(name, **kwargs)
        except ValueError:
            # If the file is a source map that doesn't exist, return an empty string
            if name.endswith('.map'):
                return ''
            raise 