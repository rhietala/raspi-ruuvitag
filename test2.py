data = {u'D7:98:F9:48:88:7A': {'acceleration': 1042.3559852564765, 'pressure': 999.65, 'temperature': 28.8, 'acceleration_y': -11, 'acceleration_x': 52, 'battery': 3211, 'acceleration_z': -1041, 'humidity': 42.5}, u'CC:92:E5:0C:A1:1B': {'acceleration': 985.5607540887573, 'pressure': 999.68, 'temperature': 28.67, 'acceleration_y': -43, 'acceleration_x': 35, 'battery': 3223, 'acceleration_z': -984, 'humidity': 44.5}, u'FB:92:57:F0:2C:54': {'acceleration': 1016.0998966637089, 'pressure': 999.95, 'temperature': 28.82, 'acceleration_y': -53, 'acceleration_x': 227, 'battery': 3235, 'acceleration_z': 989, 'humidity': 37.5}, u'DC:AA:61:EC:A9:5B': {'acceleration': 1025.8698747891956, 'pressure': 999.86, 'temperature': 8.1, 'acceleration_y': -382, 'acceleration_x': -346, 'battery': 3199, 'acceleration_z': 887, 'humidity': 53.5}, u'C7:3C:89:4D:AF:53': {'acceleration': 1051.6097184792466, 'pressure': 999.77, 'temperature': 30.69, 'acceleration_y': 967, 'acceleration_x': -413, 'battery': 3229, 'acceleration_z': -15, 'humidity': 41.5}}

print(data)

for k, v in data.items():
    print k
