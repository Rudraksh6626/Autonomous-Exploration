from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from pathlib import Path

def generate_launch_description():
    # Adjust paths as needed; users should pass config via ROS params or remap
    output_dir = '/tmp/autogen'
    config_file = str(Path(get_package_share_directory('autonomous_exploration')) / 'config' / 'default_config.yaml') if True else ''

    # If you have a generated world, point gzserver at it via the 'world' argument
    world_file = str(Path(output_dir) / 'environment.world')

    return LaunchDescription([
        # Start Gazebo server with the generated world (if exists). If the world file is missing gzserver will error.
        ExecuteProcess(
            cmd=['gzserver', '--verbose', world_file],
            output='screen'
        ),
        # Run the world generator node (it will generate and publish status)
        Node(
            package='autonomous_exploration',
            executable='world_generator_node',
            name='world_generator_node',
            parameters=[{'config': '', 'output_dir': output_dir, 'generate_on_start': True}],
        ),
    ])
