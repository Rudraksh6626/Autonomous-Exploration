import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from pathlib import Path

# Import project internals
from core.config import ConfigManager
from core.world_generation_pipeline import WorldGenerationPipeline

class WorldGeneratorNode(Node):
    def __init__(self):
        super().__init__('world_generator_node')
        self.declare_parameter('config', '')
        self.declare_parameter('output_dir', '/tmp/autogen')
        self.declare_parameter('generate_on_start', True)

        qos_depth = 10
        self.pub = self.create_publisher(String, '/world_generation_status', qos_depth)

        gen_on_start = self.get_parameter('generate_on_start').get_parameter_value().bool_value
        if gen_on_start:
            # run generation in a new thread or immediately (blocking); keep simple and run once then exit
            try:
                self.generate_world()
            except Exception as e:
                self.get_logger().error(f"Generation failed: {e}")

    def generate_world(self):
        config_path = self.get_parameter('config').get_parameter_value().string_value
        output_dir = Path(self.get_parameter('output_dir').get_parameter_value().string_value)

        if not config_path:
            self.get_logger().error('No config provided; skipping generation.')
            return

        output_dir.mkdir(parents=True, exist_ok=True)

        self.get_logger().info(f'Loading configuration from: {config_path}')
        cm = ConfigManager()
        config = cm.load_config(config_path)

        pipeline = WorldGenerationPipeline()
        pipeline.initialize(config)

        self.get_logger().info('Starting pipeline (terrain/noise/composition/obstacles)')
        pipeline.generate_procedural_terrain()
        pipeline.generate_procedural_noise()
        pipeline.compose_terrain()
        pipeline.generate_obstacles()
        pipeline.analyze_terrain_difficulty()

        heightmap_path = output_dir / 'terrain_heightmap.png'
        self.get_logger().info(f'Exporting heightmap to {heightmap_path}')
        pipeline.export_heightmap(str(heightmap_path))

        gazebo_world_path = output_dir / 'environment.world'
        self.get_logger().info(f'Exporting Gazebo world to {gazebo_world_path}')
        pipeline.export_gazebo_world(str(gazebo_world_path))

        msg = String()
        msg.data = f'world_generated:{gazebo_world_path.as_posix()}'
        self.pub.publish(msg)
        self.get_logger().info('World generation completed and status published.')


def main():
    rclpy.init()
    node = WorldGeneratorNode()
    # Node performed generation on init; keep node alive for a short time to ensure publish
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
