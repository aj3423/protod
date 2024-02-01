import chardet
import charset_normalizer


# try to detect the encoding of an string
# return (
#   decoded bytes: bytes
#   encoding name: str
#   decoding succeeded: bool
# )
def detect_multi_charset(view) -> tuple[bytes, str, bool]:
    view_bytes = view.tobytes()
    try:
        # `chardet` is way more accurate, but very slow with large bytes(4 seconds on 50k bytes)
        # `charset_normalizer` shows wrong result with small bytes, but very performant with long bytes
        if len(view_bytes) <= 200:
            detected = chardet.detect(view_bytes)
        else:
            detected = charset_normalizer.detect(view_bytes)

        if detected["confidence"] < 0.9:
            raise Exception()

        encoding = detected["encoding"]

        decoded = view_bytes.decode(encoding)

        return decoded, encoding, True
    except:
        pass

    return view_bytes, "", False
