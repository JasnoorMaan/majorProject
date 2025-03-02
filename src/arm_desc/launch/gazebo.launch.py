from launch import LaunchDescription
from pathlib import Path
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration
import os
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    arm_desc = get_package_share_directory("arm_desc")

    model_arg = DeclareLaunchArgument(
        name="model", 
        default_value=os.path.join(
                    arm_desc, "urdf", "arm.urdf.xacro"
                    ),
        description="Absolute path of the robot URDF file"
    )

    gazebo_resource_path =SetEnvironmentVariable(
        name = "GZ_SIM_RESOURCE_PATH",
        value=[
            str(Path(arm_desc).parent.resolve())
        ]
    )
    
    ros_distro= os.environ["ROS_DISTRO"]
    is_ignition = "True" if ros_distro == "humble" else "False"
    physics_engine = "" if ros_distro=="humble" else "--physics-engine gz-physics-bullet-featherstone-plugin"
    
    
    arm_desc = ParameterValue(Command([
            "xacro ", 
            LaunchConfiguration("model"),
            " is_ignition:=",
            is_ignition
            ]), 
            value_type=str)

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": arm_desc, "use_sim_time": True}]
    )
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory("ros_gz_sim"), "launch"), "/gz_sim.launch.py"]),
                launch_arguments=[
                    ("gz_args", [" -v 4 -r empty.sdf "]
                    )
                ]
             )

    gz_spawn_entity= Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-topic", "robot_description", "-name", "arm"]
    )

    gz_ros2_bridge= Node(
        package= "ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock]"
        ]
    )
    return LaunchDescription([
        model_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        gazebo,
        gz_spawn_entity,
        gz_ros2_bridge
    ])