import parsing_options
import perspective_transform
import ball_tracking
import stream_visualization
import oci_streaming

import pyrealsense2 as rs
import numpy as np

wuzzler_options = parsing_options.parseInputArgs()

# initialize OCI stream connection
if not wuzzler_options.disable_oci_stream:
	oci_streaming.initOCIStream()

try:
	pipeline = rs.pipeline()
	config = rs.config()

	# Use this config to play from camera stream directly
	config.enable_stream(rs.stream.color, 848, 480, rs.format.rgb8, 60)
	# config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 90)

	# Use this config to play from bag file
	# if wuzzler_options.input:
	#     rs.config.enable_device_from_file(config, wuzzler_options.input)

	# Start streaming
	pipeline.start(config)

	try:
		while True:

			# Wait for a coherent pair of frames: depth and color
			frames = pipeline.wait_for_frames()
			depth_frame = frames.get_depth_frame()
			color_frame = frames.get_color_frame()
			if not depth_frame or not color_frame:
				continue

			# Convert images to numpy arrays
			color_image = np.asanyarray(color_frame.get_data())
			# depth_image = np.asanyarray(depth_frame.get_data())
			
			# normalize and scale picture
			normalized_pic = perspective_transform.normalizePicture(color_image)

			# track ball
			ball_tracking.trackBall(normalized_pic, wuzzler_options.disable_oci_stream)

			stream_visualization.visualize_stream(normalized_pic)

	finally:
		pipeline.stop()
		
finally:
	pass