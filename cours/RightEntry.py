class RightEntry:

    def __init__(self):
        self.username = "";
        self.server = "";
        self.read = 0;
        self.write = 0;
        self.execute = 0;

    
    def __str__(self):
        print("Username :")
        print(self.username)
        print("Server :")
        print(self.server)
        print("Read :")
        print(self.read)
        print("Write :")
        print(self.write)
        print("Execute :")
        print(self.execute)
