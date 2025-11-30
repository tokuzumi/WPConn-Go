class AsyncIteratorToFileLike:
    def __init__(self, iterator):
        self.iterator = iterator
        self.buffer = b""

    async def read(self, n=-1):
        if not self.buffer:
            try:
                self.buffer = await self.iterator.__anext__()
            except StopAsyncIteration:
                return b""
        
        if n == -1 or len(self.buffer) <= n:
            data = self.buffer
            self.buffer = b""
            return data
        else:
            data = self.buffer[:n]
            self.buffer = self.buffer[n:]
            return data
