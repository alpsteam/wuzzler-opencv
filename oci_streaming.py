import oci
from base64 import b64encode, b64decode
import json

# define oci streaming -----------------------------------

oci_stream = "acw-stream"
oci_compartment = "ocid1.compartment.oc1..aaaaaaaadiw65ysvdvpcgfeijvcne7uadbfbnnrqyg7j4vaaadmeh6setz2a"
stream_buffer_size = 2
stream_client = None
stream_id = None
    
def initOCIStream():
    global stream_client
    global stream_id
    config = oci.config.from_file(profile_name="DEFAULT")
    # Create a StreamAdminClientCompositeOperations for composite operations.
    stream_admin_client = oci.streaming.StreamAdminClient(config)
    stream_admin_client_composite = oci.streaming.StreamAdminClientCompositeOperations(stream_admin_client)
    stream = get_or_create_stream(stream_admin_client, oci_compartment, oci_stream, 1, stream_admin_client_composite).data
    stream_client = oci.streaming.StreamClient(config, service_endpoint=stream.messages_endpoint)
    stream_id = stream.id

def get_or_create_stream(client, compartment_id, stream_name, partition, sac_composite):

    list_streams = client.list_streams(compartment_id, name=stream_name,
                                       lifecycle_state=oci.streaming.models.StreamSummary.LIFECYCLE_STATE_ACTIVE)
    if list_streams.data:
        # If we find an active stream with the correct name, we'll use it.
        print("An active stream {} has been found".format(stream_name))
        sid = list_streams.data[0].id
        return get_stream(sac_composite.client, sid)

    print(" No Active stream  {} has been found; Creating it now. ".format(stream_name))
    print(" Creating stream {} with {} partitions.".format(stream_name, partition))

    # Create stream_details object that need to be passed while creating stream.
    stream_details = oci.streaming.models.CreateStreamDetails(name=stream_name, partitions=partition,
                                                              compartment_id=oci_compartment, retention_in_hours=24)

    # Since stream creation is asynchronous; we need to wait for the stream to become active.
    response = sac_composite.create_stream_and_wait_for_state(
        stream_details, wait_for_states=[oci.streaming.models.StreamSummary.LIFECYCLE_STATE_ACTIVE])
    return response


def get_stream(admin_client, stream_id):
    return admin_client.get_stream(stream_id)

def build_json_payload(currentCoords, currentVector, currentTimestamp, lastTimestamp):

    payload = {
        "tsstart": currentTimestamp,
        "tsend": lastTimestamp,
        "posx": currentCoords[0],
        "posy": currentCoords[1],
        "dirx": currentVector[0],
        "diry": currentVector[1]
    }
    return json.dumps(payload)

def delete_stream(client, stream_id):
    print(" Deleting Stream {}".format(stream_id))
    # Stream deletion is an asynchronous operation, give it some time to complete.
    client.delete_stream_and_wait_for_state(stream_id, wait_for_states=[
                                            oci.streaming.models.StreamSummary.LIFECYCLE_STATE_DELETED])


def stream_to_oci(currentCoords, currentVector, currentTimestamp, lastTimestamp):
    publish_message("camera", build_json_payload(currentCoords, currentVector, currentTimestamp, lastTimestamp))

message_list = [] 
def publish_message(key, value):

    encoded_key = b64encode(key.encode()).decode()
    encoded_value = b64encode(value.encode()).decode()
    message_list.append(oci.streaming.models.PutMessagesDetailsEntry(key=encoded_key, value=encoded_value))


    if len(message_list) > stream_buffer_size:
        print("Publishing {} messages to the stream {} ".format(len(message_list), stream_id))
        messages = oci.streaming.models.PutMessagesDetails(messages=message_list)
        put_message_result = stream_client.put_messages(stream_id, messages)
        message_list.clear() 

        # The put_message_result can contain some useful metadata for handling failures
        for entry in put_message_result.data.entries:
            if entry.error:
                print("Error ({}) : {}".format(entry.error, entry.error_message))
            else:
                print("Published message to partition {} , offset {}".format(entry.partition, entry.offset))


# -----------------------------------