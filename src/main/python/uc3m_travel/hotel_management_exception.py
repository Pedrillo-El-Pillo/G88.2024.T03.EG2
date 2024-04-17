"""Customized exceptions for the Hotel Management System"""
class HotelManagementException(Exception):
    """Custom exception class for Hotel Management"""
    def __init__(self, message):
        self.__message = message
        super().__init__(self.message)

    @property
    def message(self):
        """Getter:  Error message for the exception"""
        return self.__message

    @message.setter
    def message(self,value):
        """setter for the error message"""
        self.__message = value
