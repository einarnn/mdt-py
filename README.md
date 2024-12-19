# Instructions

## Prepare a Python virtualenv

Create a virtualenv and then `pip install -r requirements.txt`.

## Generate Python Code From Protos

Run the script `gen_from_proto.sh`. This assumes a couple of things:

- The protobuf files from `bigmuddy-network-telemetry-proto` are available locally in a git clone. These can be cloned from [here](https://github.com/cisco/bigmuddy-network-telemetry-proto.git). They are available under the path `/opt/git-repos/bigmuddy-network-telemetry-proto`. If not, the environment variable `PROTO_ARCHIVE` in [`gen_from_proto.sh`](gen_from_proto.sh) should be edited to reflect location.
- The Google proto tools are installed (preferably in a virtualenv!), the module `grpcio-tools`

Running this script should look something like:

```
$ ls
README.md         proto_to_dict.py  server.py
gen_from_proto.sh requirements.txt  walk_fields.py
$ ./gen_from_proto.sh
$ ls
README.md                     proto_to_dict.py    telemetry_pb2_grpc.py
gen_from_proto.sh             requirements.txt    walk_fields.py
mdt_grpc_dialout_pb2.py	      server.py
mdt_grpc_dialout_pb2_grpc.py  telemetry_pb2.py
```

## Run The Sample Server

The sample server to receive telemetry is in the file `async_server.py`, and success looks like:

```
$ ./async_server.py -v
2018-07-22 21:44:41,391:__main__:DEBUG:Create gRPC server
2018-07-22 21:44:41,398:__main__:DEBUG:serving on 0.0.0.0:57850
```

By default, the server runs on port `57850`, bound to `0.0.0.0`.

## TLS

A server key and certificate (in PEM format) can be specified with the `-k` and `-c` options, respectively. This will automatically enable TLS on the connection.  Adding the option `--client-ca` will also enable client authentication using the provided CA certificate.

Example:

```
$ ./async_server.py -c ./keys/server.crt -k ./keys/server.key --client-ca ./keys/ca.crt -v
2024-12-19 11:01:42,528:__main__:DEBUG:Create gRPC server
2024-12-19 11:01:42,663:__main__:DEBUG:Running with TLS, certfile ./keys/server.crt and keyfile ./keys/server.key
2024-12-19 11:01:42,666:__main__:DEBUG:serving on 0.0.0.0:57850
```
