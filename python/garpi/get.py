#!/usr/bin/env python
'''
Classes and functions to get files or directory trees from
repositories.
'''

def get_http_ftp(what,url,target,overwrite):
    from urllib2 import Request, urlopen, URLError, HTTPError, ProxyHandler, build_opener, install_opener
    import os, shutil

    if os.path.exists(target):
        if overwrite:
            os.remove(target)
        else:
            return

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


    targetfp = open(target,"w")
    shutil.copyfileobj(res,targetfp)

    return

def uriparse(uri):
    '''
    Split the URI scheme://hostname/path into [scheme,hostname,path]
    '''
    colon = uri.find(':')
    slashslash = colon + 3
    slash = uri.find('/',slashslash)
    #print colon, slashslash, slash
    return [uri[:colon], uri[slashslash:slash], uri[slash:]]

def get(url,target,overwrite=False):
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
    omitted).  See git-clone(1) for details.  If overwriting a
    git-pull is done.

    svn+TRANSPORT: - perform "svn co" using the remaining URL with
    'svn+' removed.  If overwritting, an "svn update" is done.

    '''

    urlp = uriparse(url)
    #print urlp
    if urlp[0] == 'http' or urlp[0] == 'ftp':
        get_http_ftp(urlp[0],url,target,overwrite)

    pass

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
