#!/usr/bin/env python
'''
Classes and functions to get files or directory trees from
repositories.
'''

from util import log
import fs 
import os

def get_git(scheme,url,target,overwrite,tag):
    import git

    if os.path.exists(target + '/.git'):
        if not overwrite: return
    else:
        if len(scheme) == 1: giturl = url
        else: giturl = url[4:]
        git.clone(giturl,target)

    fs.goto(target)
    git.fetch()
    out = git.branch()
    for line in out.split('\n'):
        if not line: continue
        if line[0] != '*': continue
        out = line.split()[1]
        break
    #print out,tag
    if out != tag:
        lbranches,rbranches = git.branches()
        if tag in lbranches:
            git.checkout(tag)
        else:
            # git 1.5 does not put remotes/ like 1.6 does
            from exception import CommandFailure
            try:
                git.checkout('origin/'+tag,tag)
            except CommandFailure:
                git.checkout('remotes/origin/'+tag,tag)
    git.pull()
    fs.goback()
    return


def get_svn(url,target,overwrite):
    cmd = 'co'
    if os.path.exists(target):
        if overwrite:
            cmd = 'up'
        else:
            log.info('Pre-existing file found, not re-getting %s'%target)
            return target

    fs.assure(target)
    import svn
    if cmd == 'up':
        fs.goto(target)
        svn.svncmd('up')
    else:
        svn.svncmd('%s %s %s'%(cmd,url,target))
    return target

def get_cvs(url,module,tag,target,overwrite):
    cmd = 'co'
    if os.path.exists(target+'/CVS'):
        if overwrite:
            cmd = 'up'
        else:
            log.info('Pre-existing file found, not re-getting %s'%target)
            return target

    fs.assure(target)
    import cvs
    if cmd == 'up':
        fs.goto(target)
        cvs.cvscmd('up')
    else:
        tagflag = ""
        if tag: tagflag = "-r "+tag
        cvs.cvscmd('-d %s %s %s %s %s'%(url,cmd,tagflag,module,target))
    return target

def get_http_ftp(what,url,target,overwrite):
    from urllib2 import Request, urlopen, URLError, HTTPError, ProxyHandler, build_opener, install_opener
    import shutil

    if os.path.exists(target):
        if overwrite:
            log.info('Removing pre-existing file %s'%target)
            shutil.rmtree(target)
        else:
            log.info('Pre-existing file found, not re-getting %s'%target)
            return target

    proxy = os.getenv(what+'_proxy')
    if proxy : 
        proxy_support = ProxyHandler({what:proxy})
        opener = build_opener(proxy_support)
        install_opener(opener)

    #print 'openning',url

    try:
        res = urlopen(url)
    except HTTPError, e:
        print e.__class__, e 
        raise IOError,'Failed to get '+url
    except URLError, e:
        print e.__class__, e 
        raise IOError,'Failed to get '+url


    dirname = os.path.dirname(target)
    if dirname:
        fs.assure(dirname)
    else:
        dirname = '.'
    filename = os.path.basename(url)
    targetfile = os.path.join(dirname,filename)
    targetfp = open(targetfile,"w")
    shutil.copyfileobj(res,targetfp)
    targetfp.close()

    return target


def uriparse(uri):
    '''
    Split the URI scheme://hostname/path into [scheme,hostname,path]
    '''
    colon = uri.find(':')
    slashslash = colon + 3
    slash = uri.find('/',slashslash)
    #print colon, slashslash, slash
    return [uri[:colon], uri[slashslash:slash], uri[slash:]]



def get(url,target,overwrite=False,tag=None):
    '''
    Get the file or directory tree at the given URL and place it at
    the given target path.  If overwrite is True and target is
    preexisting it will be overwritten (updated).

    The URL is expected to be in a standard form:

    SCHEME://HOSTNAME/PATH

    The following URL schemes are supported:

    http: - the file given in PATH via HTTP

    ftp: - the file given in PATH via anonymous FTP

    git+TRANSPORT: git-clone a repository.  TRANSPORT can be http,
    rsync, ssh or empty to use native git protocol (the '+' can be
    omitted).  For local repository, use "git+file:///path/to/git".
    See git-clone(1) for details.  If overwriting a git-pull is done.

    svn+TRANSPORT: - perform "svn co" using the remaining URL with
    'svn+' removed.  If overwritting, an "svn update" is done.

    cvs+:TRANSPORT: - perform "cvs co" using the remaining URL with
    'cvs+' removed.  If overwritting, an "cvs update" is done.
    '''

    log.info('Getting url "%s" --> "%s"'%(url,target))

    urlp = uriparse(url)
    if urlp[0] == 'http' or urlp[0] == 'ftp':
        return get_http_ftp(urlp[0],url,target,overwrite)

    scheme = urlp[0].split('+')
    #print 'scheme=',scheme

    print urlp,scheme
    if urlp[0] == 'git' or scheme[0] == 'git':
        return get_git(scheme,url,target,overwrite,tag)

    if scheme[0] == 'svn':
        return get_svn(scheme[1]+'://'+urlp[1]+'/'+urlp[2]+'/'+tag,target,overwrite)
    if scheme[0] == 'cvs':
        # get_cvs(url,module,tag,target,overwrite):
        #print 'CVS: "%s", "%s", "%s"'%(urlp[0],urlp[1],urlp[2])
        url = ':%s:%s:%s'%(scheme[1],urlp[1],'/'.join(urlp[2].split('/')[:-1]))
        module = urlp[2].split('/')[-1]
        #print 'url=%s, module=%s'%(url,module)
        print 'Note: getting from CVS, if this appears to hang, it is waiting for a password'
        return get_cvs(url,module,tag,target,overwrite)

    msg = 'Unhandled URL: "%s"'%url
    log.error(msg)
    raise ValueError, msg

if '__main__' == __name__:
    import sys
    url=sys.argv[1]
    try:
        target=sys.argv[2]
    except IndexError:
        target='file.out'
    try:
        overwrite=bool(sys.argv[3])
    except IndexError:
        overwrite=False
    get(url,target,overwrite)
