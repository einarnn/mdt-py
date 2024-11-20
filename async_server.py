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
import ssl
import time
from argparse import ArgumentParser


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
            self.msgs_recvd += 1
            t = Telemetry()
            t.ParseFromString(req.data)

            #
            # Convert telemetry message as a whole into a Python dict
            #
            d = proto_to_dict(t)

            with logging_lock:
                logger.debug('--> CALLBACK START')
                logger.debug('Messages Received = %d', self.msgs_recvd)
                logger.debug('Node Id          = "{}"'.format(t.node_id_str))
                logger.debug('Subscription Id  = "{}"'.format(t.subscription_id_str))
                logger.debug('Encoding Path    = "{}"'.format(t.encoding_path))
                logger.debug('Msg Timestamp    = "{}"'.format(t.msg_timestamp))
                logger.debug('Collection Id    = "{}"'.format(t.collection_id))
                logger.debug('Collection Start = "{}"'.format(t.collection_start_time))
                logger.debug('Collection End   = "{}"'.format(t.collection_end_time))

                if t.collection_end_time > 0:
                    logger.debug('last message for collection_id {}'.format(t.collection_id))

                # json dict of the raw data
                data_gpbkv = d.get('data_gpbkv')
                if data_gpbkv:
                    for l in json.dumps(data_gpbkv, indent=2).splitlines():
                        logger.debug(l)
                
            # retval = mdt_grpc_dialout_pb2.MdtDialoutArgs()
            # retval.ReqId = req.ReqId
            # await stream.send_message(retval)


#
# Really simple gRPC server dor dialout telemetry. No TLS, plain TCP.
#
async def serve(bind_address='0.0.0.0', port=57850, certfile=None, keyfile=None):

    logger.debug('Create gRPC server')
    server = Server([TelemetryReceiver()])
    ssl_options = {}
    if certfile is not None:
        logger.debug(f"Running with TLS, certfile {certfile} and keyfile {keyfile}")
        ssl_ctx = ssl.SSLContext()
        ssl_ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)
        ssl_ctx.set_alpn_protocols(['h2'])
        ssl_options = {"ssl": ssl_ctx}

    with graceful_exit([server]):
        await server.start(bind_address, port, **ssl_options)
        logger.debug('serving on %s:%d', bind_address, port)
        await server.wait_closed()


if __name__ == "__main__":

    #
    # parse arguments
    #
    parser = ArgumentParser(description='Options:')
    parser.add_argument(
        '-b', '--bind-address', type=str,
        default='0.0.0.0',
        help="Specify bind address (default=0.0.0.0)")
    parser.add_argument(
        '-p', '--port', type=int,
        default=57850,
        help="Specify telemetry listening port (default=57850)")
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help="Exceedingly verbose logging to the console")
    parser.add_argument(
        '-c', '--cert',
        help="Specify certificate chain file (will use TLS; requires -k)")
    parser.add_argument(
        '-k', '--key',
        help="Specify key file (will use TLS; requires -c)")
    args = parser.parse_args()

    if args.cert is not None:
        assert args.key is not None, "Key must be specified if certificate is specified"

    if args.key is not None:
        assert args.cert is not None, "Certificate must be specified if key is specified"

    #
    # setup logging to have a wauy to see what's happening
    #
    if args.verbose:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    #
    # run the server
    #
    asyncio.run(serve(bind_address=args.bind_address,
                      port=args.port,
                      certfile=args.cert,
                      keyfile=args.key))
