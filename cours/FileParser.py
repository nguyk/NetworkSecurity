class FileParser:
#    def __init__(self): # Notre méthode constructeur                                                                                                                                                     
    def openFile(self):
        self.file = open("config.spatch", "r")
        self.content = self.file.read()

    def closeFile(self):
        self.file.close()

    def parse(self):
        contentArray = self.content.split("\n")
        for line in contentArray:
            print(line)
