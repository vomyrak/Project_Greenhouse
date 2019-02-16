from gpiozero import DigitalOutputDevice

class Controller(object):
    def __init__(self, irrigation=4, ventilation=17):
        self.irrigation = DigitalOutputDevice(irrigation)
        self.ventilation = DigitalOutputDevice(ventilation)

    def irrigation_on(self):
        self.irrigation.on()

    def irrigation_off(self):
        self.irrigation.off()

    def ventilation_on(self):
        self.ventilation.on()

    def ventilation_off(self):
        self.ventilation.off()
    