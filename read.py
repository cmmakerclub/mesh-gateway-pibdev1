import serial, sys, time, commands, re, os
import logging
import paho.mqtt.client as paho
import time
import serial.tools.list_ports
import json

#reload(sys)
#sys.setdefaultencoding('utf8')
CONFIG = {
    'NAME': os.environ.get('MQTT_NAME', ''),
    'USER': os.environ.get('MQTT_USER', ''),
    'PASSWORD': os.environ.get('MQTT_PASSWORD', ''),
    'HOST': os.environ.get('MQTT_HOST', 'beta.cmmc.io'),
    'PORT': os.environ.get('MQTT_PORT', 51883),
    'PUB_TOPIC': os.environ.get('MQTT_PUB_TOPIC', 'MARU/data/status'),
    'SERIAL_PORT_PATTERN': os.environ.get('SERIAL_PORT_PATTERN', 'usbserial*'),
    'SERIAL_BAUD_RATE': os.environ.get('SERIAL_BAUD_RATE', 57600),
}


def on_publish(client, userdata, mid):
    print("published mid: "+str(mid))
    # print userdata
    pass

client = paho.Client()
client.on_publish = on_publish
client.connect(CONFIG['HOST'], CONFIG['PORT'])
client.loop_start()

device = None

if not device:
    matched_ports = serial.tools.list_ports.grep(CONFIG['SERIAL_PORT_PATTERN'])
    if matched_ports: 
        device = [x[0] for x in matched_ports][0]
        print "Success: matched device = %s"% device
    else:
        print "Fatal: Can't find usb serial device."
        sys.exit(0);

try: 
    ser = serial.Serial(
        port=device,
        baudrate=CONFIG['SERIAL_BAUD_RATE'],
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS)
except Exception, e:
    print str(e)
    exit()

#https://stackoverflow.com/a/27628622
def readline(a_serial, eol=b'\r\n'):
    leneol = len(eol)
    line = bytearray()
    while True:
        c = a_serial.read(1)
        # print c
        if c:
            line += c
            if line[-leneol:] == eol:
                break
        else:
            break
    return (line)

def str2hexstr(line):
  return " ".join(hex(ord(n)) for n in line)

print "reading..."
while True:
    try:
        line = readline(ser)
        line_str = bytes(line)
        line_hex = str2hexstr(line_str)
        print ">>> " + str2hexstr(line_str)
        print ">>> type = %d " %line[2]
        print ">>> len = %d " %line[3]

        if line[3] > 0:
            json_string = line[4:4+line[3]]
            print ">>> text = %s " %json_string 
            if line[2] == 0x03: 
                print 'pubtopic = %s' %CONFIG['PUB_TOPIC']
                (rc, mid) = client.publish(CONFIG['PUB_TOPIC'], json_string, qos=0, retain=True)
    except Exception as e:
        print e
    except KeyboardInterrupt:
        print "closing serial port..."
        ser.close()
        sys.exit()
    finally:
        pass
