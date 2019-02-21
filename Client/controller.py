from gpiozero import DigitalOutputDevice
from gpiozero import PWMOutputDevice

class Controller(object):
    def __init__(self, irrigation=12, ventilation=13, step_size = 0.1):
        ''' raspberry pi pin definitions '''
        self.irrigation = PWMOutputDevice(irrigation)
        self.ventilation = PWMOutputDevice(ventilation)
        self.step_size = step_size

    def irrigation_up(self):
        ''' increment irrigation power to maximum in steps '''
        self.irrigation.on()
        updated_val = self.irrigation.value + self.step_size
        if updated_val > 1:
            self.irrigation.value = 1
        else:
            self.irrigation.value = updated_val
        
    def irrigation_down(self):
        ''' decrement irrigation power to minimum in steps '''
        self.irrigation.on()
        updated_val = self.irrigation.value - self.step_size
        if updated_val < 0:
            self.irrigation.off()
        else:
            self.irrigation.value = updated_val

    def ventilation_up(self):
        ''' increment ventilation power to maximum in steps '''
        self.ventilation.on()
        updated_val = self.ventilation.value + self.step_size
        if updated_val > 1:
            self.ventilation.value = 1
        else:
            self.ventilation.value = updated_val

    def ventilation_down(self):
        ''' decrement ventilation power to minimum in steps '''
        updated_val = self.ventilation.value - self.step_size
        if updated_val < 0:
            self.ventilation.off()
        else:
            self.ventilation.value = updated_val
    
