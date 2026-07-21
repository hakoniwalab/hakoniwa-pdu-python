# Auto-generated CDR minimum payload size registry
# Sizes include the 4-byte CDR encapsulation header.
# Variable-length sequences are counted as length 0; strings are counted as empty strings.
PDU_CDR_SIZE = {
    "builtin_interfaces/Duration": 12,
    "builtin_interfaces/Time": 12,
    "geometry_msgs/Quaternion": 36,
    "geometry_msgs/Transform": 60,
    "geometry_msgs/Twist": 52,
    "geometry_msgs/Vector3": 28,
    "std_msgs/Header": 17,
    "trajectory_msgs/JointTrajectory": 28,
    "trajectory_msgs/JointTrajectoryPoint": 28,
    "trajectory_msgs/MultiDOFJointTrajectory": 28,
    "trajectory_msgs/MultiDOFJointTrajectoryPoint": 24,
}

def get_size(type_name: str):
    return PDU_CDR_SIZE.get(type_name)
