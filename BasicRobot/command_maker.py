# command_maker.py
class RobotCommandMaker:
    def __init__(self):
        pass

    def calculate_checksum(self, data_id, data0, data1):
        """Calculate checksum based on data_id, data0, and data1."""
        return (data_id + data0 + data1) % 256

    def create_command(self, sender_id, receiver_id, data_id, data0, data1):
        """
        Create a 6-byte command packet.

        :param sender_id: 1 byte sender ID (0-255)
        :param receiver_id: 1 byte receiver ID (0-255)
        :param data_id: 1 byte data ID (0-255)
        :param data0: 1 byte data0 (0-255)
        :param data1: 1 byte data1 (0-255)
        :return: bytes object representing the command packet
        """
        if not all(0 <= x <= 255 for x in [sender_id, receiver_id, data_id, data0, data1]):
            raise ValueError("All values must be in the range 0-255")

        # Calculate checksum
        cs = self.calculate_checksum(data_id, data0, data1)
        
        # Create the packet
        packet = bytearray([
            sender_id,
            receiver_id,
            data_id,
            data0,
            data1,
            cs
        ])
        
        return bytes(packet)

    def create_drive_command(self, sender_id, receiver_id, left_speed, right_speed):
        """
        Create a drive command packet.

        :param sender_id: 1 byte sender ID (0-255)
        :param receiver_id: 1 byte receiver ID (0-255)
        :param left_speed: 1 byte left motor speed (0-255)
        :param right_speed: 1 byte right motor speed (0-255)
        :return: bytes object representing the drive command packet
        """
        data_id = 1  # Define a unique data_id for drive commands
        data0 = left_speed
        data1 = right_speed

        return self.create_command(sender_id, receiver_id, data_id, data0, data1)

    def parse_command(self, command):
        """
        Parse a 6-byte command packet.

        :param command: bytes object representing the command packet
        :return: tuple (sender_id, receiver_id, data_id, data0, data1, checksum)
        """
        if len(command) != 6:
            raise ValueError("Command must be exactly 6 bytes long")

        sender_id, receiver_id, data_id, data0, data1, checksum = command

        # Validate checksum
        expected_checksum = self.calculate_checksum(data_id, data0, data1)
        if checksum != expected_checksum:
            raise ValueError("Checksum does not match")

        return (sender_id, receiver_id, data_id, data0, data1, checksum)
