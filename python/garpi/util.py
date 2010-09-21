import logging, logging.handlers, sys,os

def stderr(s):
    sys.stderr.write(str(s)+'\n')
    return s
def try_traceback(a):
    try:
        a.printTraceback(sys.stderr)
    except:
        pass

from logging import _srcfile
class MyLogger(logging.Logger):
    DEBUG   = logging.DEBUG
    INFO    = logging.INFO
    WARN    = logging.WARN
    WARNING = logging.WARNING
    ERROR   = logging.ERROR
    FATAL   = logging.FATAL


    def log(self, level, msg, *args, **kwargs):
        logging.Logger.log(self, level, msg, *args, **kwargs)
        try_traceback(msg)
        return msg
    def debug(self, msg, *args, **kwargs):
        logging.Logger.debug(self, msg, *args, **kwargs)
        try_traceback(msg)
        return msg
    def info(self, msg, *args, **kwargs):
        logging.Logger.info(self, msg, *args, **kwargs)
        try_traceback(msg)
        return msg
    def warning(self, msg, *args, **kwargs):
        logging.Logger.warning(self, msg, *args, **kwargs)
        try_traceback(msg)
        return msg
    def error(self, msg, *args, **kwargs):
        logging.Logger.error(self, msg, *args, **kwargs)
        try_traceback(msg)
        return msg
    def error_notrace(self, msg, *args, **kwargs):
        logging.Logger.error(self, msg, *args, **kwargs)
        return msg
    def critical(self, msg, *args, **kwargs):
        logging.Logger.critical(self, msg, *args, **kwargs)
        try_traceback(msg)
        return msg

    def findCaller(self):
        f = sys._getframe(2)
        while 1:
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back.f_back
                continue
            return filename, f.f_lineno, ""

class LogMaker(object):
    default_format = '%(asctime)s %(process)d %(levelname)s %(module)s:%(lineno)d - %(message)s'
    def __init__(self,name):
        self.log = None
        self.name = name
        self.format = LogMaker.default_format
        return

    def make_logger(self):
        if self.log: return self.log
        self.log = MyLogger(self.name)
        self.rfh = logging.handlers.RotatingFileHandler(self.name+'.log','a',10e6,50)
        self.rfh.setLevel(logging.DEBUG)
        self.log.setLevel(logging.INFO)
        f = logging.Formatter(self.format)
        self.rfh.setFormatter(f)
        self.log.addHandler(self.rfh)
        return self.log

    def set_format(self,format = None):
        if format is None: format = LogMaker.default_format
        self.rfh.setFormatter(logging.Formatter(format))
        #print 'changed format from "%s" to "%s"'%(self.format,format)
        ret = self.format
        self.format = format
        return ret

    def set_file(self,filename):
        'Change the file name for the log'
        self.rfh.baseFilename = filename
        return

    def new_file(self,filename):
        self.set_file(filename)
        #self.rfh.doRollover()
        return

    def set_level(self,level):
        self.log.setLevel(level)
        return


log_maker = LogMaker('garpi')
log = log_maker.make_logger()


def extractall(tar):
    for member in tar.getmembers():
        tar.extract(member)


def untar(filename):
    import tarfile
    log.info("Untar %s in %s"%(filename,os.getcwd()))
    tar = tarfile.open(filename)
    try:
        tar.extractall()
    except AttributeError:
        extractall(tar)
    tar.close()


