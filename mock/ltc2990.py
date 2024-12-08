from mock.board import I2C

class LTC2990:

    def __init__(self, i2c: I2C, address: int = 0x76):
        pass

    def get_temperature(self) -> int:
        """
        Returns the internal temperature in Celsius.
        :return: The internal temperature in Celsius (integer).
        """
        pass
