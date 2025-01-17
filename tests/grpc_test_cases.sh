#!/bin/bash

if ! command -v grpcurl &>/dev/null; then
    echo "Error: grpcurl is not installed. Please install grpcurl and try again."
    exit 1
fi

GRPC_SERVER="localhost:8000"
PROTO_FILE="../protos/v1/vault.proto"

client_publish_pub_key="ND/VGAu7SjxWvcEH7zSctDqnfEG6YibqBWSXmjbFYFQ="
client_device_id_pub_key="ND/VGAu7SjxWvcEH7zSctDqnfEG6YibqBWSXmjbFYFQ="

read -rp "Enter phone number: " phone_number
read -rsp "Enter password: " password
echo

echo "Testing AuthenticateEntity..."

grpcurl -plaintext \
    -d @ \
    -proto "$PROTO_FILE" \
    "$GRPC_SERVER" "vault.v1.Entity/AuthenticateEntity" <<EOM
{
    "phone_number": "$phone_number",
    "password": "$password",
    "client_publish_pub_key": "$client_publish_pub_key",
    "client_device_id_pub_key": "$client_device_id_pub_key"
}
EOM
