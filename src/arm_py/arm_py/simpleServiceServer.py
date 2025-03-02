import rclpy
from rclpy.node import Node

class SinpleServiceServer(Node):
    def __init_(self):
        super().__init__('simple_service_server')

        self.service_= self.create_service(
            AddTwoInts, 
            'add_two_ints', 
            self.add_two_ints_callback)