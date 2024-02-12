#!/home/cubert/venv_3.9/bin/python3

### Change the shebang to match the Python distribution

# Python imports
import os
import time
import numpy as np
from datetime import timedelta

# Custom imports
import cuvis

# ROS imports
import rclpy
import std_msgs
import ament_index_python
from rclpy.node import Node
from cuvis_ros.msg import DataCube
#import ros2_numpy as rnp
from std_msgs.msg import String
from time import sleep

class CameraDriver(Node):
    def __init__(self):
        super().__init__('camera_driver', allow_undeclared_parameters=True)
        # Initialize configuration directories
        self.declare_parameter('camera_timeout', 2500)
        self.declare_parameter('integration_time', 30)
        self.declare_parameter('loop_rate', 1)

        # Initialize logging
        self.get_logger().set_level(rclpy.logging.LoggingSeverity.DEBUG)

        # Retrieve a parameter with a default value if not set
        self.timeout = self.get_parameter('camera_timeout').get_parameter_value().integer_value
        self.exposure = self.get_parameter('integration_time').get_parameter_value().integer_value
        self.rate = self.get_parameter('loop_rate').get_parameter_value().integer_value
        self.r = self.create_rate(self.rate)

        package_path = ament_index_python.get_package_prefix('cuvis_ros')
        self.default_dir = os.path.join(package_path,'lib', 'cuvis_ros')
        cuvis_factory_dir_in_docker_container = "/colcon_ws/src/cuvis.ros/cuvis_factory"
        self.declare_parameter('data_dir', cuvis_factory_dir_in_docker_container)
        self.declare_parameter('factory_dir', cuvis_factory_dir_in_docker_container) 
        dataDir = self.get_parameter('data_dir').get_parameter_value().string_value
        factoryDir = self.get_parameter('factory_dir').get_parameter_value().string_value
        userSettingsDir = dataDir

        self.get_logger().info("loading calibration, processing and acquisition context (factory)...")
        calibration = cuvis.Calibration(factoryDir)

        self.get_logger().info("loading user settings...")
        settings = cuvis.General(userSettingsDir)
        settings.set_log_level("info")
        self.processingContext = cuvis.ProcessingContext(calibration)
        self.acquisitionContext = cuvis.AcquisitionContext(calibration)
        init_rate = self.create_rate(1)
        while self.acquisitionContext.state == cuvis.HardwareState.Offline:
            self.acquisitionContext = cuvis.AcquisitionContext(calibration)
            print(f"camera is online: {self.acquisitionContext.state == cuvis.HardwareState.Online}")
            print(f"camera is offline {self.acquisitionContext.state == cuvis.HardwareState.Offline}")
            print(f"camera is partially online: {self.acquisitionContext.state == cuvis.HardwareState.PartiallyOnline}")
            print(f"{self.acquisitionContext.state}camera could not connect, retrying...")
            sleep(1)
        self.get_logger().info("Camera is online")
        self.acquisitionContext.operation_mode = cuvis.OperationMode.Software
        self.acquisitionContext.integration_time = self.exposure
        print('creating publisher for datacube msg') 
        # Publisher for the raw hyperspectral image
        self.hypercube_pub = self.create_publisher(String, 'hyperspectral/raw_img', 10)
        
    def record_img(self):
        '''
        Record raw hyperspectral image
        '''
        print("attempting to capture frame and publish")
        am = self.acquisitionContext.capture()
        mesu, res = am.get(timedelta(milliseconds=self.timeout))

        if mesu is not None:
            self.processingContext.apply(mesu)
            raw_img = mesu.data.get('cube').array
        # print("attempting to create custom msg")
        # msg = DataCube()
        # h = std_msgs.msg.Header()
        # h.stamp = self.get_clock().now().to_msg()
        # msg.header = h
        # msg.height, msg.width, msg.lam = list(raw_img.shape)
        # data = np.ravel(raw_img).astype(np.int16).tolist()
        # msg.data = data
        # msg.integration_time = int(mesu.integration_time)
        # print(f'Got frame! Shape:{raw_img.shape}')
        # self.hypercube_pub.publish(msg)
        str_msg = String()
        str_msg.data = np.array2string(np.ravel(raw_img).astype(np.int16), precision=6, separator=',', suppress_small=True)
        print(f"str msg data: {str_msg.data}")
        self.hypercube_pub.publish(str_msg)
        print('publsihed raw img')

def main(args=None):
    rclpy.init(args=args)
    camDriver = CameraDriver()
    while rclpy.ok():
        camDriver.record_img()
        sleep(1)
    camDriver.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
