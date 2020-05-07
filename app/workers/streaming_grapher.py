# h/t: https://dev.to/sethmlarson/python-data-streaming-to-google-cloud-storage-with-resumable-uploads-458h

from google.auth.transport.requests import AuthorizedSession
from google.resumable_media import requests, common
from google.cloud import storage

class GraphStreamer(object):
    def __init__(self, client, bucket_name, blob_name, chunk_size=(256 * 1024)):
        self.client = client
        self.bucket = self.client.bucket(bucket_name)
        self.blob = self.bucket.blob(blob_name)

        self.buffer = b''
        self.buffer_size = 0
        self.chunk_size = chunk_size
        self.read = 0

        self.transport = AuthorizedSession(credentials=self.client._credentials)
        self.request = None  # type: requests.ResumableUpload

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, *_):
        if exc_type is None:
            self.stop()

    def start(self):
        url = (
            f'https://www.googleapis.com/upload/storage/v1/b/'
            f'{self.bucket.name}/o?uploadType=resumable'
        )
        self.request = requests.ResumableUpload(
            upload_url=url, chunk_size=self.chunk_size
        )
        self.request.initiate(
            transport=self.transport,
            content_type='application/octet-stream',
            stream=self,
            stream_final=False,
            metadata={'name': self.blob.name},
        )

    def stop(self):
        self.request.transmit_next_chunk(self.transport)

    def write(self, data: bytes) -> int:
        data_len = len(data)
        self.buffer_size += data_len
        self.buffer += data
        del data
        while self.buffer_size >= self.chunk_size:
            try:
                self.request.transmit_next_chunk(self.transport)
            except common.InvalidResponse:
                self.request.recover(self.transport)
        return data_len

    def read(self, chunk_size: int) -> bytes:
        # I'm not good with efficient no-copy buffering so if this is
        # wrong or there's a better way to do this let me know! :-)
        to_read = min(chunk_size, self.buffer_size)
        memview = memoryview(self.buffer)
        self.buffer = memview[to_read:].tobytes()
        self.read += to_read
        self.buffer_size -= to_read
        return memview[:to_read].tobytes()

    def tell(self) -> int:
        return self.read


if __name__ == "__main__":

    client = storage.Client()

    with GraphStreamer(client=client, bucket='test-bucket', blob='test-blob') as streamer:
        for _ in range(1024):
            streamer.write(b'x' * 1024)
