import g2coreGuiBackendLogHistory
import g2coreGuiBackendDRO
import gcodeFile

class g2coreGuiBackend:
    def __init__(self, application):
        self.protocol = None
        self.application = application
        self.userCommandQueue = ['{"sr":n}']
        self.logHistory = g2coreGuiBackendLogHistory.g2coreGuiBackendLogHistory()
        self.digitalReadOut = g2coreGuiBackendDRO.g2coreGuiBackendDRO()
        self.gCode = None
        self.isSendingGCode = False
        
    def setProtocol(self, protocol):
        self.protocol = protocol

    def setGCode(self, gCode):
        self.gCode = gCode

    def startSendingGCode(self):
        self.isSendingGCode = True
        
    def animate(self):
        if self.protocol != None:
            self.protocol.animate()
            while (True):
#                prefix = getLogLinePrefix()
                coreLine = self.protocol.getLine()
                if coreLine != None:
                    self.logHistory.addLine(0, coreLine)
                    data = self.protocol.getLastLineAsJson()
                    if data != None:
                        self.digitalReadOut.animate(data)
                    
                else:
                    break
                
            moreDataToSend = True
            while moreDataToSend:
                if self.protocol.hasFreeTxBuffers():
                    command = None
                    if len(self.userCommandQueue)>0:
                        command = self.userCommandQueue.pop(0)
                    else:
                        if self.gCode != None and self.isSendingGCode:
                            command = self.gCode.getLine()
                            if command == None:
                                self.isSendingGCode = False
                        else:
                            self.isSendingGCode = False    
                    if command != None:
                        self.protocol.sendLine(command)
                        self.logHistory.addLine(1, command)
                    else:
                        moreDataToSend = False
                else:
                    moreDataToSend = False
                
    def appendUserCommandToQueue(self, command):
        isSpecialCommand = False
        strippedCommand = command.strip();
        if len(strippedCommand)>0:
            firstChar = strippedCommand[0]
            #feedhold, queue flush, end feedhold, kill job and reset board 
            if firstChar=="!" or firstChar=="%" or firstChar=="~" or firstChar==chr(4) or firstChar==chr(24):
                isSpecialCommand = True
            
        if isSpecialCommand:
            self.protocol.sendSpecialCommand(strippedCommand) #Sending the stripped version to help with panicked
            self.logHistory.addLine(1, strippedCommand)
        else:
            self.userCommandQueue.append(command)
