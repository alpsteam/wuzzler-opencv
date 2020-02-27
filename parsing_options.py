import argparse

def parseInputArgs():
	parser = argparse.ArgumentParser(description="Wuzzler ball tracking options")
	# parser.add_argument("-i", "--input", type=str, help="Path to the bag file")
	parser.add_argument("--disable_oci_stream", help="Disable streaming to OCI", action="store_true", default=False)
	# parser.add_argument("-c", "--compartment", type=str, help="OCI compartment OCID", default="ocid1.compartment.oc1..aaaaaaaadiw65ysvdvpcgfeijvcne7uadbfbnnrqyg7j4vaaadmeh6setz2a")
	# parser.add_argument("-s", "--stream_oci", type=str, help="OCI stream name", default="acw-stream")
	args = parser.parse_args()
	# Safety if no parameter have been given
	# if not args.input:
	#     print("No input paramater have been given. Will attempt to use camera live stream.")
	#     print("For help type --help")
	# # Check if the given file have bag extension
	# if args.input and os.path.splitext(args.input)[1] != ".bag":
	#     print("The given file is not of correct file format.")
	#     print("Only .bag files are accepted")
	#     exit()

	return args