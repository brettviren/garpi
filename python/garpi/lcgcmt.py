'''
Things related to LCGCMT project that are not related to projects in general..  
'''

from projects import Project

class Lcgcmt(Project):
    def __init__(self):
        Project.__init__(self,"lcgcmt")
        return

    def project_externals(self,project):
        '''Determine external dependencies of the given project.  The
        project is assumed to be downloaded.  Returns an ordered
        list.'''
        return []


