import socket
import pmt
d = pmt.make_dict()
d = pmt.dict_add(d, pmt.intern('theta_deg'),  pmt.from_double(20.0))
d = pmt.dict_add(d, pmt.intern('distance_m'), pmt.from_double(20.0))
socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(
    pmt.serialize_str(d), ('127.0.0.1', 52002))
