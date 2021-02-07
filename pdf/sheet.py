from fpdf                import FPDF
from config              import Config
from database.markstable import MarksTable

class Sheet(FPDF):
    def __init__(self, pc):
        self.pc = pc
        super().__init__()
        self.add_font('Sofia','','pdf/Sofia-Regular.ttf',uni=True)
        self.add_page()
        self.year = int(MarksTable.year())
        self.set_font('Sofia', '', 22)
        self.cell(180, 10, self.pc['name'], 0, 1, align='C')
        markList = MarksTable().list(lord=pc['memberId'], year=self.year)
        self.marks = []
        for row in markList:
            self.marks.append(row[5])

    def parchment(self, text, width):
        y = self.get_y()
        x = self.get_x()
        self.set_xy(x, y+1)
        self.image('images/pdfpart.png', w=width, h=10)
        self.set_xy(x, y+2.5)
        self.set_font('Sofia', '', 10)
        self.cell(width, 5, text, 0, 2, align='C')
        self.set_xy(x, y+11)

    def stats(self):
        x = self.get_x()
        self.parchment('Skills', 30)

        self.set_font('Times', '', 8)
        for s in Config.senechalConfig['stats']:
            self.cell(20, 3, s)
            self.cell(5, 3, str(self.pc['stats'][s.lower()[:3]]), 0, 2, align='R')
            self.set_x(x)

        self.cell(20, 1, "", 0, 2)
        self.cell(20, 3, "Damage")
        self.cell(5, 3, str(round((self.pc['stats']['str'] + self.pc['stats']['siz']) / 6)) + 'd6', 0, 2, align='R')
        self.set_x(x)

        self.cell(20, 3, "Healing Rate")
        self.cell(5, 3, str(round((self.pc['stats']['con'] + self.pc['stats']['siz']) / 10)), 0, 2, align='R')
        self.set_x(x)

        self.cell(20, 3, "Move Rate")
        self.cell(5, 3, str(round((self.pc['stats']['dex'] + self.pc['stats']['siz']) / 10)), 0, 2, align='R')
        self.set_x(x)

        self.cell(20, 3, "HP")
        self.cell(5, 3, str(round((self.pc['stats']['con'] + self.pc['stats']['siz']))), 0, 2, align='R')
        self.set_x(x)

        self.cell(20, 3, "Unconscious")
        self.cell(5, 3, str(round((self.pc['stats']['con'] + self.pc['stats']['siz']) / 4)), 0, 2, align='R')
        self.set_x(x)

    def skills(self):
        for sn, sg in self.pc['skills'].items():
            x = self.get_x()
            self.parchment(sn, 30)
            for name, value in sg.items():
                self.set_font('Times', '', 8)
                self.cell(20, 3, name)
                self.cell(5, 3, str(value), 0, 0, align='R')
                self.set_font('ZapfDingbats', '', 8)
                self.cell(3, 3, "on"[name in self.marks], 0, 2)
                self.set_x(x)

    def traits(self):
        x = self.get_x()
        traits = self.pc['traits'];
        virtues = []
        if 'Culture' in self.pc['main']:
            for name, value in Config.senechalConfig['virtues'].items():
                if name in self.pc['main']['Culture']:
                    virtues = value
        print(virtues)
        self.parchment('Traits', 50)
        for row in Config.senechalConfig['traits']:
            self.set_font('ZapfDingbats', '', 8)
            self.cell(3, 3, "on"[row[0] in self.marks], 0, 0)
            if row[0] in virtues:
                self.set_font('Times', 'U', 8)
            else:
                self.set_font('Times', '', 8)

            self.cell(15, 3, row[0], 0, 0)
            self.set_font('Times', '', 8)
            self.cell(5, 3, str(traits[row[0].lower()[:3]]), align='R')
            self.cell(3, 3, "/", 0, 0, align='C')
            self.cell(5, 3, str(20-traits[row[0].lower()[:3]]), align='R')
            if row[1] in virtues:
                self.set_font('Times', 'U', 8)
            else:
                self.set_font('Times', '', 8)
            self.cell(15, 3, row[1], 0, 0)
            self.set_font('ZapfDingbats', '', 8)
            self.cell(3, 3, "on"[row[1] in self.marks], 0, 2)
            self.set_x(x)
        chivalry = traits['ene']+traits['gen']+traits['jus']+traits['mod']+traits['mer']+traits['val']
        self.set_font('Times', '', 8)
        self.cell(50, 3, "Chivalry: " +str(chivalry)+"/80", 0, 2, align='C')


    def passions(self):
        x = self.get_x()
        self.parchment('Passions', 50)
        for name, value  in self.pc['passions'].items():
            self.set_font('Times', '', 8)
            self.cell(42, 3, name, 0, 0)
            self.cell(5, 3, str(value), 0, 0, align='R')
            self.set_font('ZapfDingbats', '', 8)
            self.cell(3, 3, "on"[name in self.marks], 0, 2)
            self.set_x(x)

    def param(self,  name, value):
        self.set_font('Times', 'B', 8)
        self.write(3, name+": ")
        self.set_font('Times', '', 8)
        self.write(3, str(value)+"\n")

    def main(self):
        self.parchment( 'Knight', 80)
        x = self.get_x()
        y = self.get_y()

        from database.eventstable import EventsTable
        if 'memberId' in self.pc:
            self.pc['main']['Glory'] = EventsTable().glory(self.pc['memberId'])

        skipp = ['Homeland', 'Lord', 'Home', 'Culture', 'Glory', 'Born', 'Squired', 'Knighted']
        x = self.get_x()
        y = self.get_y()
        self.param("Homeland", self.pc['main']['Homeland'])
        self.set_xy(x+40, y)
        self.param("Lord", self.pc['main']['Lord'])
        y += 4
        self.set_xy(x, y)
        self.param("Home", self.pc['main']['Home'])
        self.set_xy(x+40, y)
        self.param("Culture", self.pc['main']['Culture'])

        y += 4
        self.set_xy(x, y)
        self.param("Age", str(self.year - int(self.pc['main']['Born'])))
        self.set_xy(x+20, y)
        self.param("Born", self.pc['main']['Born'])
        self.set_xy(x+40, y)
        self.param("Squired", self.pc['main']['Squired'])
        self.set_xy(x+60, y)
        self.param("Knighted", self.pc['main']['Knighted'])

        for name, value in self.pc['main'].items():
            if name not in skipp:
                y += 4
                self.set_xy(x, y)
                self.param(name, value)
        y += 4
        self.set_xy(x, y)

    def fill(self):
        y = self.get_y()
        x = self.get_x()
        
        self.stats()
        self.skills()
        
        self.set_xy(x+40, y)
        self.traits()
        self.passions()
        
        self.set_xy(x+100, y)
        self.main()
