# Remade by Andrew Yegiayan and Michelle Picardo
# repo: https://github.com/IRIS-Digital-Dosimeter/IRIS-Project/blob/serial_log_binary/analysis/scripts/import_serial_binary.py
# Originally by Aidan Zinn
# repo: https://github.com/aidanzinn/Adafruit_Constant_Log/blob/master/import_serial_binary.py

# REQUIRES TWO ADDITIONAL DIRECTORIES IN SCRIPT'S PARENT DIRECTORY: 'data' and 'timestamps'


import os
import serial.tools.list_ports
from datetime import datetime
import json

FILE_LINES = 20000
SCHEMA_BYTES = 16
TIMESTAMP_SAMPLES = 100
BUFF_SIZE = SCHEMA_BYTES * TIMESTAMP_SAMPLES

def create_new_file(name: str): # returns the file created
    filename = f'{name}.dat'
    try:
        return open('data/'+ filename, 'wb', buffering=BUFF_SIZE)  # Open in binary write mode and increase buffer size
    except FileNotFoundError:
        print('\nNot Found: "data/"')
        print('Create "data" directory then run this program again')
        return None

def get_formatted_time():
    return datetime.now().strftime("%Y-%m-%d___%H-%M-%S.%f")



# retrieve the list of available ports
ports = serial.tools.list_ports.comports()  

# print out enumerated list of available ports
print("Available Ports:")
portsList = {}
for num, port in enumerate(ports, start=1):               # loop through ports list and save them to the port list
    portsList[num] = port                                 # Save the ports to the dict
    print(f'{num}: {portsList[num].description}')         # Print them in a descriptive format

# get user input for port selection
val = input("\nSelect Port by number: ")  # Ask the user to declare which Port to use based on the dict above
selectedPort = portsList[int(val)]        # Save the selected port to a variable

# get user input for baud rate
baud = int(input("\nSet baud rate (9600,115200): "))  

# open the port with the selected baud rate
ser = serial.Serial(port=selectedPort.device, baudrate=baud)  

# Open serial
ser.reset_input_buffer()  
ser.flushInput()

# create dict for storing the timestamps in a JSON


print()
print("Starting the logging process...")

while True: # each iteration is a new file
    try:
        line_count = 0
        time_dict = {"sample_timestamps": {}}
        
        TIMESTAMP = get_formatted_time() # year-month-day___hour-minute-second.microsecond
        with create_new_file(TIMESTAMP) as file:  # Open a new file with a new timestamp
            if file is None: 
                break # Exit the loop if file creation failed

            
            while line_count < FILE_LINES: # each iteration is a new line in the file/buffer
                buffer = b''  # Initialize buffer to store data
                while len(buffer) < BUFF_SIZE:
                    buffer += ser.read(SCHEMA_BYTES)
                    line_count += 1
                
                # write the buffer to the file
                file.write(buffer)
                time_dict["sample_timestamps"][str(line_count)] = get_formatted_time()
            
                
            json_path = os.path.join('timestamps', f'{os.path.basename(file.name)}.json')
            with open(json_path, 'w') as json_file:
                time_dict["JSON_timestamp"] = get_formatted_time()
                json_file.write(json.dumps(time_dict, indent=4))

    except KeyboardInterrupt:
        print("\n\nKeyboard Interrupt: Exiting...")
        break
    except Exception as e:
        print("\n\nError:", e)
        break

# close the serial connection just in case
ser.close()
