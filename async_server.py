#!/usr/bin/env python
#
# See also
# https://github.com/grpc/grpc/blob/v1.13.x/examples/python/route_guide/route_guide_server.py
#
from grpclib.server import Server
from grpclib.utils import graceful_exit
from mdt_grpc_dialout_grpc import gRPCMdtDialoutBase
from proto_to_dict import proto_to_dict
from telemetry_pb2 import Telemetry
from threading import Lock
from walk_fields import walk_fields

import asyncio
import json
import logging
import mdt_grpc_dialout_pb2
import time


logger = logging.getLogger(__name__)
logger_grpc = logging.getLogger("grpc._server")
logger_p2d = logging.getLogger("proto_to_dict")

logging_lock = Lock()


class TelemetryReceiver(gRPCMdtDialoutBase):

    msgs_recvd = 0
    
    async def MdtDialout(self, stream):
        while True:
            logger.debug('awaiting telemetry messge...')
            req: MdtDialoutArgs = await stream.recv_message()
            t = Telemetry()
            t.ParseFromString(req.data)

            #
            # Convert telemetry message as a whole into a Python dict
            #
            d = proto_to_dict(t)

            #
            # Walk data_gpbkv fields per YANG Suite code
            #
            # lines = []
            # for gpb in t.data_gpbkv:
            #     lines += self.walk_fields(gpb.fields)
                
            with logging_lock:
                logger.debug('--> CALLBACK START')
                logger.debug('Messages Received = %d', self.msgs_recvd)
                logger.debug('Node Id         = "{}"'.format(t.node_id_str))
                logger.debug('Msg Timestamp   = "{}"'.format(t.msg_timestamp))
                logger.debug('Subscription Id = "{}"'.format(t.subscription_id_str))
                logger.debug('Encoding Path   = "{}"'.format(t.encoding_path))
                
                # yang suite lines
                # for l in lines:
                #     logger.debug(l)

                # json dict
                if d:
                    for l in json.dumps(d, indent=2).splitlines():
                        logger.debug(l)
                
            retval = mdt_grpc_dialout_pb2.MdtDialoutArgs()
            retval.ReqId = req.ReqId
            await stream.send_message(retval)


#
# Really simple gRPC server dor dialout telemetry. No TLS, plain TCP.
#
async def serve(host='0.0.0.0', port=57850):

    logger.debug('Create gRPC server')
    server = Server([TelemetryReceiver()])

    with graceful_exit([server]):
        await server.start(host, port)
        logger.debug('serving on port 57850')
        await server.wait_closed()


if __name__ == "__main__":

    #
    # setup logging to have a wauy to see what's happening
    #
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    #
    # run the server
    #
    asyncio.run(serve())
