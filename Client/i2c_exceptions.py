class I2CError(Exception):
    """Base class for I2C exceptions"""
    pass

class AppVerificationFailureError(I2CError):
    
    def __str__(self):
        return "Hardware application verification failed"

class AppStartupFailureError(I2CError):
    
    def __str__(self):
        return "Hardware application startup failed"

class ModeConfigurationFailureError(I2CError):
    
    def __str__(self):
        return "Hardware mode configuration failed"

class I2CReadingError(I2CError):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class I2CTimeoutError(I2CError):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message