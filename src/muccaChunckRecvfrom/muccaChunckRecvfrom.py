"""MuccaChunckRecvfrom."""
import sys
import os


class muccaChunckRecvfrom:
    """Mucca Chunck recvfrom."""

    @staticmethod
    def run(socketServer, chunckSize, logging):
        """Run recvfrom mucca."""
        logging.log_info(
            'Wait [preflight]...',
            os.path.abspath(__file__),
            sys._getframe().f_lineno
            )

        data = socketServer.recv(5)
        totalsize = int(data)
        numberOfChunk = int(data)/chunckSize
        plusChunk = int(data) % chunckSize
        numberOfChunkRecived = 0

        if plusChunk > 0:
            numberOfChunk = int(numberOfChunk + 1.0)

        cp = round(numberOfChunk)
        numberOfChunkInt = round(numberOfChunk)

        completeMsg = ""
        while numberOfChunkInt != 0:
            numberOfChunkInt = numberOfChunkInt-1
            numberOfChunkRecived = numberOfChunkRecived+1

            if numberOfChunkInt == 0:
                chunckSize = totalsize-((cp-1)*chunckSize)
            data = socketServer.recv(chunckSize)
            completeMsg = "{}{}".format(completeMsg, data.decode('utf-8'))
        return completeMsg.encode()
