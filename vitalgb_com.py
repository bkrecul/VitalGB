class Bluetooth:
    def __init__(self, device_name):
        self.device_name = device_name

    def get_socket_stream(self):
        from jnius import autoclass
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        InputStreamReader = autoclass('java.io.InputStreamReader')
        BufferedReader = autoclass('java.io.BufferedReader')
        UUID = autoclass('java.util.UUID')

        paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        socket = None
        for device in paired_devices:
            if device.getName() == self.device_name:
                socket = device.createInsecureRfcommSocketToServiceRecord(
                    UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                # socket = device.createRfcommSocketToServiceRecord(
                #     UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                reader = InputStreamReader(socket.getInputStream(), 'US-ASCII')
                self.recv_stream = BufferedReader(reader)
                # recv_stream = socket.getInputStream()
                self.send_stream = socket.getOutputStream()
                break
        socket.connect()
        return self.recv_stream, self.send_stream

    def enviar_byte(self):
        i = [27, 64]  # ASCII escape integer and at sign integer
        pre = bytearray(i)
        cmd = f'{1}\n'.encode('UTF-8')
        pre.extend(cmd)
        self.send_stream.write(cmd)
        self.send_stream.flush()





