"""
Simple CCSDS Packet Generator
"""

from flask import Flask, render_template, request, jsonify
import struct
from crccheck.crc import Crc16CcittFalse as crc16
app = Flask(__name__)


# ============================================================================
# APID DEFINITIONS - Customize these for your spacecraft
# ============================================================================
def get_apid_definitions():
    """
    Define your APIDs and their required fields
    Each APID has a specific command structure
    """
    return {
        '0x01': {
            'name': 'Reboot',
            'fields': [
                {'name': 'device_id', 'type': 'uint8'},
                {'name': 'state', 'type': 'uint8'},  # 0=OFF, 1=ON
            ]
        },
        '0x02': {
            'name': 'Shutdown',
            'fields': [
                {'name': 'telemetry_id', 'type': 'uint16'},
                {'name': 'rate_hz', 'type': 'uint8'},
            ]
        },
        '0xC2': {
            'name': 'Enable Time',
            'fields': [
                {'name': 'mode', 'type': 'uint8'},
                {'name': 'timeout_sec', 'type': 'uint16'},
            ]
        },
        '0x5E': {
            'name': 'Emergency Revert',
            'fields': []
        },
        '0x67': {
            'name': 'Execute File',
            'fields': []
        },
        '0xFE': {
            'name': 'List Files',
            'fields': [{'name':'Directory Path'}]
        },
        '0xAB': {
            'name': 'Auto Downlink File',
            'fields': []
        },
        '0xAF': {
            'name': 'Zip Downlink File',
            'fields': []
        },
        '0xAC': {
            'name': 'Zip Downlink PAT Data',
            'fields': []
        },
        '0x15':{
            'name': 'Disasaemble File',
            'fields': []
        },
        '0x16': {
            'name':'Request File',
            'fields': [
                {'name':'Transfer ID'},
                {'name': 'Transfer Flag'},
                {'name': 'Chunk Index'},
                {'name': 'Number of Chunks to Transfer (if flag != 0xFF)'}
            ]
        },
        '0xCD': {
            'name': 'Uplink File',
            'fields': []
        },
        '0x39': {
            'name': 'Assemble File',
            'fields': []
        },
        '0x40': {
            'name': 'Validate File',
            'fields':[]
        },
        '0x41': {
            'name':'Move File',
            'fields': []
        },
        '0x42': {
            'name':'Delete File',
            'fields':[
                {'name':'Directory Flag'},

                {'name':'File/Directory Name'}
            ]
        },
        '0x43': {
            'name':'Unzip File',
            'fields':[
                {'name':'ZipFile Name'},
                {'name': 'Destination Directory Path'}
            ]
        },
        '0xCC': {
            'name':'Auto Assemble File',
            'fields':[]
        },
        '0x2A':{
            'name':'Update Options',
            'fields':[]
        },
        '0xB3':{
            'name':'Set PAT Mode',
            'fields':[]
        },
        '0xB4':{
            'name':'Update PAT Offset Params',
            'fields':[]
        },
        '0xF1': {
            'name':'Single Capture',
            'fields':[]
        },
        '0x28':{
            'name':'FSM Test',
            'fields':[]
        },
        '0x32':{
            'name':'Run Calibration',
            'fields':[]
        },
        '0x35':{
            'name':'Test ADCs Feedback',
            'fields':[]
        },
        '0x86': {
            'name':'Update Acquisition Params',
            'fields': []
        },
        '0x87': {
            'name':'TX Align',
            'fields':[]
        },
        '0x88': {
            'name':'Update TX Offsets',
            'fields':[]
        },
        '0x89': {
            'name':'Update FSM Angles',
            'fields':[]
        },
        '0x90': {
            'name':'Enter PAT Main',
            'fields':[]
        },
        '0x91': {
            'name':'Exit PAT Main',
            'fields': []
        },
        '0x92':{
            'name':'End PAT Process',
            'fields':[]
        },
        '0x54': {
            'name':'Set FPGA',
            'fields':[]
        },
        '0x0E':{
            'name':'Get FPGA',
            'fields':[]
        },
        '0x97':{
            'name':'Set HK',
            'fields':[]
        },
        '0x3D': {
            'name':'Echo',
            'fields':[]
        },
        '0x5B':{
            'name':'NOOP',
            'fields':[]
        },
        '0x80':{
            'name':'Selftest',
            'fields':[]
        },
        '0xE0':{
            'name':'Downlink Mode',
            'fields':[]
        },
        '0xD0':{
            'name':'Debug Mode',
            'fields':[]
        }
    }


# ============================================================================
# ROUTES
# ============================================================================
@app.route('/')
def index():
    apids = get_apid_definitions()
    return render_template('index.html', apids=apids)


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    apid = data.get('apid')
    fields = data.get('fields')
    
    # Generate packet bytes
    packet_bytes = create_packet(apid, fields)
    
    # Convert to hex string
    hex_output = str(([int(b) for b in packet_bytes]))
    
    return jsonify({
        'hex': hex_output,
        'bytes': list(packet_bytes)
    })


# ============================================================================
# PACKET GENERATION
# ============================================================================
def create_packet(apid, fields):
    """Create packet data field from APID and field values"""
    apid_defs = get_apid_definitions()
    apid_def = apid_defs[apid]
    print(apid_def)
    sync = 0x352EF853

    data = 0xDEADBEEF
    data = struct.pack('>I', data)
    # Pack each field according to its type
    # for field_def in apid_def['fields']:
    #     field_name = field_def['name']
    #     field_type = field_def['type']
    #     value = int(fields[field_name])
        
    #     # Pack using struct (same as unpacking)
    #     if field_type == 'uint8':
    #         packet.extend(struct.pack('B', value))
    #     elif field_type == 'uint16':
    #         packet.extend(struct.pack('>H', value))
    #     elif field_type == 'uint32':
    #         packet.extend(struct.pack('>I', value))
    if apid_def['name'] == 'Delete File':
        name = fields['File/Directory Name'].encode('utf-8')
        name_len = len(name)
        name = struct.pack('%ds' % (name_len), name)
        dflag = struct.pack('B', int(fields['Directory Flag'], 16))
        name_len = struct.pack('>H', name_len)
        data = dflag + name_len + name
    elif apid_def['name'] == 'List Files':
        name = fields['Directory Path'].encode('utf-8')
        name_len = len(name)
        data = struct.pack('>H%ds' % (name_len), name_len, name)
    elif apid_def['name'] == 'Unzip File':
        zip_name = fields['ZipFile Name'].encode('utf-8')
        dest_name = fields['Destination Directory Path'].encode('utf-8')
        zip_len = len(zip_name)
        dest_len = len(dest_name)
        data = struct.pack('>HH%ds' % (zip_len+dest_len), zip_len, dest_len, zip_name+dest_name)
    elif apid_def['name'] == 'Request File':
        id = int(fields['Transfer ID'])
        flag = int(fields['Transfer Flag'])
        idx = int(fields['Chunk Index'])
        if flag == 255:
            num_chunks = 0
        else: 
            num_chunks = int(fields['Number of Chunks to Transfer (if flag != 0xFF)'])
        data = struct.pack('>HBHH', id, flag, idx, num_chunks)

    #data field completed
    apid_int = int(apid, 16)
    print(apid_int)
    apid_bytes = struct.pack('B', apid_int)
    apid_bytes = 0b0010000000000000 + apid_int
    print(apid_bytes)
    sequence_bytes = int(0xC000)
    primary = struct.pack('>HHH', apid_bytes, sequence_bytes, len(data) +1)

    pck = primary + data
    crc = crc16.calc(pck)
    pck =  struct.pack('>I',sync) + pck + struct.pack('>H',crc)
    return pck

if __name__ == '__main__':
    app.run(debug=True, port=5000)
