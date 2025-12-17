import serial
import struct
import time
from typing import List, Optional, Union, Dict, Any

class ModbusRTU:
    """Modbus RTU protocol implementation"""
    
    # Function codes
    READ_COILS = 0x01
    READ_DISCRETE_INPUTS = 0x02
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
    WRITE_SINGLE_COIL = 0x05
    WRITE_SINGLE_REGISTER = 0x06
    WRITE_MULTIPLE_COILS = 0x0F
    WRITE_MULTIPLE_REGISTERS = 0x10
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        
    def connect(self) -> bool:
        """Connect to Modbus RTU device"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_EVEN,  # or PARITY_EVEN for some devices
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            print(f"✅ Connected to Modbus RTU on {self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
            
    def _calculate_crc(self, data: bytes) -> int:
        """Calculate Modbus RTU CRC16"""
        crc = 0xFFFF
        
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
                    
        return crc
        
    def _build_frame(self, slave_id: int, function_code: int, data: bytes) -> bytes:
        """Build Modbus RTU frame with CRC"""
        frame = struct.pack('BB', slave_id, function_code) + data
        crc = self._calculate_crc(frame)
        frame += struct.pack('<H', crc)  # Little-endian CRC
        return frame
        
    def _validate_frame(self, frame: bytes) -> bool:
        """Validate received frame CRC"""
        if len(frame) < 4:
            return False
            
        data = frame[:-2]
        received_crc = struct.unpack('<H', frame[-2:])[0]
        calculated_crc = self._calculate_crc(data)
        
        return received_crc == calculated_crc
        
    def _send_frame(self, frame: bytes) -> Optional[bytes]:
        """Send frame and receive response"""
        if not self.serial:
            return None
            
        try:
            # Clear input buffer
            self.serial.reset_input_buffer()
            
            # Send frame
            self.serial.write(frame)
            self.serial.flush()
            
            # Wait for response (minimum 3.5 character times)
            char_time = 11 / self.baudrate  # 11 bits per character
            min_delay = 3.5 * char_time
            time.sleep(max(min_delay, 0.001))
            
            # Read response
            response = self.serial.read(1000)  # Read available data
            
            return response
            
        except Exception as e:
            print(f"Communication error: {e}")
            return None
            
    def _parse_response(self, response: bytes, expected_function: int) -> Optional[bytes]:
        """Parse and validate response"""
        if not response or len(response) < 4:
            return None
            
        # Validate CRC
        if not self._validate_frame(response):
            print("❌ CRC validation failed")
            return None
            
        slave_id = response[0]
        function_code = response[1]
        
        # Check for exception response
        if function_code & 0x80:
            exception_code = response[2] if len(response) > 2 else 0
            print(f"❌ Modbus exception: {self._get_exception_message(exception_code)}")
            return None
            
        # Validate function code
        if function_code != expected_function:
            print(f"❌ Unexpected function code: {function_code}")
            return None
            
        # Return data portion (excluding slave_id, function_code, and CRC)
        return response[2:-2]
        
    def _get_exception_message(self, code: int) -> str:
        """Get Modbus exception message"""
        exceptions = {
            0x01: "Illegal Function",
            0x02: "Illegal Data Address", 
            0x03: "Illegal Data Value",
            0x04: "Slave Device Failure",
            0x05: "Acknowledge",
            0x06: "Slave Device Busy",
            0x08: "Memory Parity Error",
            0x0A: "Gateway Path Unavailable",
            0x0B: "Gateway Target Device Failed to Respond"
        }
        return exceptions.get(code, f"Unknown Exception ({code})")
# Example Modbus frame structure
#print("Modbus RTU Frame Structure:")
#print("┌─────────────┬──────────────┬─────────────┬─────────────┐")
#print("│  Slave ID   │ Function Code│    Data     │    CRC16    │")
#print("│   1 byte    │    1 byte    │  0-252 bytes│   2 bytes   │")
#print("└─────────────┴──────────────┴─────────────┴─────────────┘")
#print("\nExample: Read 3 holding registers starting at address 0x0001")
#print("Request:  [0x01] [0x03] [0x00 0x01] [0x00 0x03] [CRC16]")
#print("Response: [0x01] [0x03] [0x06] [data1] [data2] [data3] [CRC16]")

class ModbusMaster(ModbusRTU):
    """Complete Modbus RTU Master implementation"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        super().__init__(port, baudrate, timeout)
        self.statistics = {
            'requests_sent': 0,
            'responses_received': 0,
            'timeouts': 0,
            'crc_errors': 0,
            'exceptions': 0
        }
        
    def read_coils(self, slave_id: int, start_address: int, count: int) -> Optional[List[bool]]:
        """Read coils (discrete outputs)"""
        if count < 1 or count > 2000:
            print("❌ Invalid count: must be 1-2000")
            return None
            
        # Build request frame
        data = struct.pack('>HH', start_address, count)
        frame = self._build_frame(slave_id, self.READ_COILS, data)
        
        # Send request and get response
        response = self._send_frame(frame)
        self.statistics['requests_sent'] += 1
        
        if not response:
            self.statistics['timeouts'] += 1
            return None
            
        # Parse response
        data = self._parse_response(response, self.READ_COILS)
        if data is None:
            return None
            
        self.statistics['responses_received'] += 1
        
        # Extract coil values
        if len(data) < 1:
            return None
            
        byte_count = data[0]
        coil_bytes = data[1:1+byte_count]
        
        coils = []
        for byte_idx, byte_val in enumerate(coil_bytes):
            for bit_idx in range(8):
                if len(coils) >= count:
                    break
                coils.append(bool(byte_val & (1 << bit_idx)))
                
        return coils[:count]
        
    def read_discrete_inputs(self, slave_id: int, start_address: int, count: int) -> Optional[List[bool]]:
        """Read discrete inputs"""
        if count < 1 or count > 2000:
            print("❌ Invalid count: must be 1-2000")
            return None
            
        data = struct.pack('>HH', start_address, count)
        frame = self._build_frame(slave_id, self.READ_DISCRETE_INPUTS, data)
        
        response = self._send_frame(frame)
        self.statistics['requests_sent'] += 1
        
        if not response:
            self.statistics['timeouts'] += 1
            return None
            
        data = self._parse_response(response, self.READ_DISCRETE_INPUTS)
        if data is None:
            return None
            
        self.statistics['responses_received'] += 1
        
        byte_count = data[0]
        input_bytes = data[1:1+byte_count]
        
        inputs = []
        for byte_idx, byte_val in enumerate(input_bytes):
            for bit_idx in range(8):
                if len(inputs) >= count:
                    break
                inputs.append(bool(byte_val & (1 << bit_idx)))
                
        return inputs[:count]
        
    def read_holding_registers(self, slave_id: int, start_address: int, count: int) -> Optional[List[int]]:
        """Read holding registers"""
        if count < 1 or count > 125:
            print("❌ Invalid count: must be 1-125")
            return None
            
        data = struct.pack('>HH', start_address, count)
        frame = self._build_frame(slave_id, self.READ_HOLDING_REGISTERS, data)
        
        response = self._send_frame(frame)
        self.statistics['requests_sent'] += 1
        
        if not response:
            self.statistics['timeouts'] += 1
            return None
            
        data = self._parse_response(response, self.READ_HOLDING_REGISTERS)
        if data is None:
            return None
            
        self.statistics['responses_received'] += 1
        
        byte_count = data[0]
        register_bytes = data[1:1+byte_count]
        
        registers = []
        for i in range(0, len(register_bytes), 2):
            if i + 1 < len(register_bytes):
                value = struct.unpack('>H', register_bytes[i:i+2])[0]
                registers.append(value)
                
        return registers
        
    def read_input_registers(self, slave_id: int, start_address: int, count: int) -> Optional[List[int]]:
        """Read input registers"""
        if count < 1 or count > 125:
            print("❌ Invalid count: must be 1-125")
            return None
            
        data = struct.pack('>HH', start_address, count)
        frame = self._build_frame(slave_id, self.READ_INPUT_REGISTERS, data)
        
        response = self._send_frame(frame)
        self.statistics['requests_sent'] += 1
        
        if not response:
            self.statistics['timeouts'] += 1
            return None
            
        data = self._parse_response(response, self.READ_INPUT_REGISTERS)
        if data is None:
            return None
            
        self.statistics['responses_received'] += 1
        
        byte_count = data[0]
        register_bytes = data[1:1+byte_count]
        
        registers = []
        for i in range(0, len(register_bytes), 2):
            if i + 1 < len(register_bytes):
                value = struct.unpack('>H', register_bytes[i:i+2])[0]
                registers.append(value)
                
        return registers
        
    def write_single_coil(self, slave_id: int, address: int, value: bool) -> bool:
        """Write single coil"""
        coil_value = 0xFF00 if value else 0x0000
        data = struct.pack('>HH', address, coil_value)
        frame = self._build_frame(slave_id, self.WRITE_SINGLE_COIL, data)
        
        response = self._send_frame(frame)
        self.statistics['requests_sent'] += 1
        
        if not response:
            self.statistics['timeouts'] += 1
            return False
            
        data = self._parse_response(response, self.WRITE_SINGLE_COIL)
        if data is None:
            return False
            
        self.statistics['responses_received'] += 1
        
        # Validate echo response
        if len(data) >= 4:
            echo_addr, echo_value = struct.unpack('>HH', data[:4])
            return echo_addr == address and echo_value == coil_value
            
        return False
        
    def write_single_register(self, slave_id: int, address: int, value: int) -> bool:
        """Write single holding register"""
        if value < 0 or value > 65535:
            print("❌ Invalid value: must be 0-65535")
            return False
            
        data = struct.pack('>HH', address, value)
        frame = self._build_frame(slave_id, self.WRITE_SINGLE_REGISTER, data)
        
        response = self._send_frame(frame)
        self.statistics['requests_sent'] += 1
        
        if not response:
            self.statistics['timeouts'] += 1
            return False
            
        data = self._parse_response(response, self.WRITE_SINGLE_REGISTER)
        if data is None:
            return False
            
        self.statistics['responses_received'] += 1
        
        # Validate echo response
        if len(data) >= 4:
            echo_addr, echo_value = struct.unpack('>HH', data[:4])
            return echo_addr == address and echo_value == value
            
        return False
        
    def write_multiple_coils(self, slave_id: int, start_address: int, values: List[bool]) -> bool:
        """Write multiple coils"""
        if len(values) < 1 or len(values) > 1968:
            print("❌ Invalid count: must be 1-1968")
            return False
            
        # Pack coil values into bytes
        byte_count = (len(values) + 7) // 8
        coil_bytes = bytearray(byte_count)
        
        for i, value in enumerate(values):
            if value:
                byte_idx = i // 8
                bit_idx = i % 8
                coil_bytes[byte_idx] |= (1 << bit_idx)
                
        data = struct.pack('>HHB', start_address, len(values), byte_count) + coil_bytes
        frame = self._build_frame(slave_id, self.WRITE_MULTIPLE_COILS, data)
        
        response = self._send_frame(frame)
        self.statistics['requests_sent'] += 1
        
        if not response:
            self.statistics['timeouts'] += 1
            return False
            
        data = self._parse_response(response, self.WRITE_MULTIPLE_COILS)
        if data is None:
            return False
            
        self.statistics['responses_received'] += 1
        
        # Validate response
        if len(data) >= 4:
            echo_addr, echo_count = struct.unpack('>HH', data[:4])
            return echo_addr == start_address and echo_count == len(values)
            
        return False
        
    def write_multiple_registers(self, slave_id: int, start_address: int, values: List[int]) -> bool:
        """Write multiple holding registers"""
        if len(values) < 1 or len(values) > 123:
            print("❌ Invalid count: must be 1-123")
            return False
            
        # Validate values
        for value in values:
            if value < 0 or value > 65535:
                print(f"❌ Invalid value {value}: must be 0-65535")
                return False
                
        byte_count = len(values) * 2
        register_bytes = b''.join(struct.pack('>H', value) for value in values)
        
        data = struct.pack('>HHB', start_address, len(values), byte_count) + register_bytes
        frame = self._build_frame(slave_id, self.WRITE_MULTIPLE_REGISTERS, data)
        
        response = self._send_frame(frame)
        self.statistics['requests_sent'] += 1
        
        if not response:
            self.statistics['timeouts'] += 1
            return False
            
        data = self._parse_response(response, self.WRITE_MULTIPLE_REGISTERS)
        if data is None:
            return False
            
        self.statistics['responses_received'] += 1
        
        # Validate response
        if len(data) >= 4:
            echo_addr, echo_count = struct.unpack('>HH', data[:4])
            return echo_addr == start_address and echo_count == len(values)
            
        return False
        
    def scan_slaves(self, max_slave_id: int = 247) -> List[int]:
        """Scan for active Modbus slaves"""
        print(f"Scanning for Modbus slaves (1-{max_slave_id})...")
        
        active_slaves = []
        
        for slave_id in range(1, max_slave_id + 1):
            # Try to read a single input register (commonly supported)
            result = self.read_input_registers(slave_id, 0, 1)
            
            if result is not None:
                active_slaves.append(slave_id)
                print(f"✅ Found slave at ID {slave_id}")
            else:
                print(f"   No response from ID {slave_id}", end='\r')
                
            time.sleep(0.1)  # Small delay between scans
            
        print(f"\nScan complete. Found {len(active_slaves)} active slaves: {active_slaves}")
        return active_slaves
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get communication statistics"""
        stats = self.statistics.copy()
        
        if stats['requests_sent'] > 0:
            stats['success_rate'] = (stats['responses_received'] / stats['requests_sent']) * 100
        else:
            stats['success_rate'] = 0
            
        return stats
        
    def reset_statistics(self):
        """Reset communication statistics"""
        for key in self.statistics:
            self.statistics[key] = 0
            
    def close(self):
        """Close Modbus connection"""
        if self.serial:
            self.serial.close()
            print("Modbus connection closed")

# Example usage
#modbus = ModbusMaster('/dev/ttyUSB0', 9600)

#if modbus.connect():
    # Read holding registers
    #slave_id = 1
    #registers = modbus.read_holding_registers(slave_id, 0, 5)
    #if registers:
        #print(f"📊 Holding registers 0-4: {registers}")
        
    # Write single register
    #success = modbus.write_single_register(slave_id, 0, 1234)
    #print(f"📝 Write register: {'Success' if success else 'Failed'}")
    
    # Read coils
    #coils = modbus.read_coils(slave_id, 0, 8)
    #if coils:
        #print(f"🔌 Coils 0-7: {coils}")
        
    # Write multiple coils
    #new_coils = [True, False, True, False, False, True, False, True]
    #success = modbus.write_multiple_coils(slave_id, 0, new_coils)
    #print(f"🔌 Write coils: {'Success' if success else 'Failed'}")
    
    # Show statistics
    #stats = modbus.get_statistics()
    #print(f"\n📈 Statistics: {stats}")
    
    #modbus.close()