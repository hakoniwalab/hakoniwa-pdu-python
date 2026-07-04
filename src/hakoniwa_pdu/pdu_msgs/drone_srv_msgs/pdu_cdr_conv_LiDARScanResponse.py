from .pdu_pytype_LiDARScanResponse import LiDARScanResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..sensor_msgs.pdu_cdr_conv_PointCloud2 import *
from ..sensor_msgs.pdu_cdr_conv_PointField import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_LiDARScanResponse(writer: CdrWriter, src: LiDARScanResponse):
    writer.write_bool(src.ok)
    py_to_cdr_body_PointCloud2(writer, src.point_cloud)
    py_to_cdr_body_Pose(writer, src.lidar_pose)
    writer.write_string(src.message)


def cdr_body_to_py_LiDARScanResponse(reader: CdrReader, dst: LiDARScanResponse):
    dst.ok = reader.read_bool()
    cdr_body_to_py_PointCloud2(reader, dst.point_cloud)
    cdr_body_to_py_Pose(reader, dst.lidar_pose)
    dst.message = reader.read_string()
    return dst


def py_to_cdr_LiDARScanResponse(src: LiDARScanResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_LiDARScanResponse(writer, src)
    return writer.bytes()


def cdr_to_py_LiDARScanResponse(cdr_payload) -> LiDARScanResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = LiDARScanResponse()
    return cdr_body_to_py_LiDARScanResponse(reader, dst)
