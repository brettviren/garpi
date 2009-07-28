from util import log

class CmtStates:
    def __init__(self):
        return

    def register(self,machine):
        machine.add_state('CMT_DOWNLOAD',self.download)
        machine.add_state('CMT_UNPACK',self.unpack)
        machine.add_state('CMT_BUILD',self.build)
        return

    def download(self,garpi):
        log.info('cmt download')
        return ('CMT_UNPACK',garpi)

    def unpack(self,garpi):
        log.info('cmt unpack')
        return ('CMT_BUILD',garpi)

    def build(self,garpi):
        log.info('cmt build')
        return ('DONE',garpi)
