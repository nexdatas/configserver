import PyTango


new_device_info_writer = PyTango.DbDevInfo()
new_device_info_writer._class = "NXSConfigServer"
new_device_info_writer.server = "NXSConfigServer/MCS1"
new_device_info_writer.name = "p09/mcs/r228"

db = PyTango.Database()
db.add_device(new_device_info_writer)
db.add_server(new_device_info_writer.server, new_device_info_writer)
