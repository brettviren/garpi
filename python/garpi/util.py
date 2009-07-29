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

class LogFileObj:
    'Facade implementing write() that calls given callable'
    def __init__(self,callobj):
        self.callobj = callobj
    def write(*args,**kwd):
        return self.callobj(args,kwd)


class LogMaker():
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
        self.rfh.baseFilename = filename
        return
    def set_level(self,level):
        self.log.setLevel(level)
        return


log_maker = LogMaker('garpi')
log = log_maker.make_logger()


def untar(filename):
    import tarfile
    log.info("Untar %s in %s"%(filename,os.getcwd()))
    tar = tarfile.open(filename)
    tar.extractall()
    tar.close()

def source2env(filename):
    '''Return a map showing the environment after doing equivalent of
    "source filename".'''
    import commands
    ret,res = commands.getstatusoutput('source %s && env'%filename)
    if ret != 0:
        from exception import CommandFailure
        raise CommandFailure, 'Failed to source "%s" from %s'%(filename,os.getcwd())
    
    env = {}
    for line in res.split('\n'):
        ind = line.find('=')
        key = line[:ind]
        val = line[ind+1:]
        env[key] = val
        continue
    return env
