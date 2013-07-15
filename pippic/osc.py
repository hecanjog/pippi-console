import liblo
import time

class Client:
    def __init__(self, hostname, port=9000):
        """ Set time to now & create Address reference to OSC server

            If server cannot be found liblo.AddressError exception will
            be thrown. Best to wrap in try / except on creation.
            """
        self.server_address = liblo.Address(hostname, port)
        self.now()

    def now(self):
        """ Reset time to now.

            Messages will apply time offsets to 
            this timestamp.

            Client.group() calls this automatically 
            just before sending a group of messages.
        """
        self.time = time.time()
        self.elapsed = 0.0

    def rtsend(self, path, *args):
        message = liblo.Message(path)
        message.add(*args)
        liblo.send(self.server_address, message)

    def send(self, path, timestamp, *args):
        """ Send a timestamped OSC message.

            Be sure to call now() before 
            sending a message, otherwise 
            messages will be timestamped from 
            when the class was instantiated.
            """

        message = liblo.Message(path)
        message.add(*args)
        #bundle = liblo.Bundle(self.time + self.elapsed + offset, message)
        bundle = liblo.Bundle(timestamp, message)
        liblo.send(self.server_address, bundle)
        #self.elapsed += offset

    def group(self, messages):
        """ Send a group of timestamped messages to OSC path

            Data format:
                message = [path, offset_in_seconds, id, value]
            """

        now = liblo.time()
        elapsed = 0.0
        offset = 0.0
        for message in messages:
            elapsed += offset
            path = message[0]
            self.send(path, now + elapsed, *tuple(message[2:]))
            offset = float(message[1])

        #print elapsed, now
