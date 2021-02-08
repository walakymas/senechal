from unittest import TestCase


class TestSheet(TestCase):
    def test_fill(self):
        print("fill")
        from config import Config
        Config.reload()
        from pdf.sheet import Sheet
        pdf = Sheet(Config.characters[470683159889969153])
        pdf.output('/tmp/Perin.pdf')
        print("saved")


