import os

from click import argument
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    # Specify the name of the package and path to xacro file within the package
    pkg_name = 'mobile_manipulator'
    file_subpath = 'kuka_iiwa/model.urdf'


    # Use xacro to process the file
    xacro_file = os.path.join(get_package_share_directory(pkg_name),file_subpath)
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # model_subpath = 'worlds/pine_tree_world.world'
    # world_path = os.path.join(get_package_share_directory(pkg_name),model_subpath)
    # world = LaunchConfiguration('world')

    # Configure the node
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw,
        'use_sim_time': True}] # add other parameters here if required
    )



    # gazebo = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([os.path.join(
    #         get_package_share_directory('gazebo_ros'), 'launch'), '/gazebo.launch.py']), launch_arguments={'world': world}.items(),
    #     )


    # spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
    #                 arguments=['-topic', 'robot_description',
    #                             '-entity', 'my_bot'],
    #                 output='screen')


    # Run the node
    # return LaunchDescription([
    #     gazebo,
    #     node_robot_state_publisher,
    #     spawn_entity
    # ])

    # Set the path to the Gazebo ROS package
    pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')   
    
    # Set the path to this package.
    pkg_share = FindPackageShare(package='mobile_manipulator').find('mobile_manipulator')
    
    # Set the path to the world file
    world_file_name = 'pine_tree_world.world'
    world_path = os.path.join(pkg_share, 'worlds', world_file_name)
   
    # Set the path to the SDF model files.
    #gazebo_models_path = os.path.join(pkg_share, 'models')
    #os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path
    
    ########### YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE ##############  
    # Launch configuration variables specific to simulation
    headless = LaunchConfiguration('headless')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_simulator = LaunchConfiguration('use_simulator')
    world = LaunchConfiguration('world')
 
    declare_simulator_cmd = DeclareLaunchArgument(
        name='headless',
        default_value='False',
        description='Whether to execute gzclient')
        
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')
    
    declare_use_simulator_cmd = DeclareLaunchArgument(
        name='use_simulator',
        default_value='True',
        description='Whether to start the simulator')
    
    declare_world_cmd = DeclareLaunchArgument(
        name='world',
        default_value=world_path,
        description='Full path to the world model file to load')
        
    # Specify the actions
    
    # Start Gazebo server
    start_gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        condition=IfCondition(use_simulator),
        launch_arguments={'world': world}.items())
    
    # Start Gazebo client    
    start_gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')),
        condition=IfCondition(PythonExpression([use_simulator, ' and not ', headless])))
        


    # Create the launch description and populate
    ld = LaunchDescription()
    # Declare the launch options
    ld.add_action(declare_simulator_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_use_simulator_cmd)
    ld.add_action(declare_world_cmd)
    
    # Add any actions
    ld.add_action(start_gazebo_server_cmd)
    ld.add_action(start_gazebo_client_cmd)

    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
            arguments=['-topic', 'robot_description',
                        '-entity', 'my_bot'],
            output='screen')
    ld.add_action(node_robot_state_publisher)
    ld.add_action(spawn_entity)
    
 
    return ld
