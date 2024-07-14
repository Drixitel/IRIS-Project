import struct


dat_path = "C:\\Users\\Sevak\\Documents\\GitHub\\IRIS-Project\\analysis\\scripts\\data\\2024-07-13___18-36-23.283361.dat"
conv_path = "C:\\Users\\Sevak\\Documents\\GitHub\\IRIS-Project\\analysis\\scripts\\data\\converted.txt"

conv_data = []
with open(dat_path, "rb") as dat:
    for _ in range(20000):
        data = dat.read(16)
        values = struct.unpack('<4I', data)
        conv_data.append(f"{','.join(map(str, values))}" + "\n")
            
with open(conv_path, "w") as conv:
    conv.writelines(conv_data)