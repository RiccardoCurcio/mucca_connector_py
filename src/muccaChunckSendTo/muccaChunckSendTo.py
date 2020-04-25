"""MuccaChunckSendTo."""
import sys
import os


class muccaChunckSendTo:
    """MuccaChunckSendTo."""

    @staticmethod
    def run(socketClient, chunckSize, message, logging):
        """Run."""
        msgSize = len(message)
        logging.log_info(
            'Sending [prefilight]...',
            os.path.abspath(__file__),
            sys._getframe().f_lineno
            )
        prefilightSize = "{:05n}".format(msgSize)

        sent = socketClient.sendall(bytes(prefilightSize.encode()))

        numberOfChunk = int(msgSize)/chunckSize
        plusChunk = int(msgSize) % chunckSize

        if plusChunk > 0:
            numberOfChunk = int(numberOfChunk + 1.0)
        numberOfChunk = round(numberOfChunk)
        i = 0
        for i in range(0, int(numberOfChunk)):
            chunkedMsg = ""
            if i == numberOfChunk-1 and plusChunk > 0:
                chunkedMsg = message[len(message)-plusChunk:]
            else:
                chunkedMsg = message[
                    (chunckSize)*i: ((chunckSize)*i)+chunckSize
                ]
            sent = socketClient.sendall(
                bytes(
                    str(chunkedMsg).encode()
                )
                )
