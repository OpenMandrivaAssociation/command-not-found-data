import time
import os
import sys
import subprocess
import fcntl
import select

def execute_command(command, shell=False, cwd=None, timeout=0, raiseExc=True, print_to_stdout=False, exit_on_error=False):
    output = ""
    start = time.time()
    try:
        child = None
        print "Executing command: %s" % command
        child = subprocess.Popen(
            command,
            shell=shell,
            bufsize=0, close_fds=True,
            stdin=open("/dev/null", "r"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
            )
        # use select() to poll for output so we dont block
        output = logOutput([child.stdout, child.stderr],
                start, timeout, print_to_stdout=print_to_stdout)
    except Exception, ex:
        # kill children if they arent done
        if type(ex) == IOError and ex.errno==4:
            print 'Process execution has been terminated'
            exit()
        try:
            if child is not None and child.returncode is None:
                os.killpg(child.pid, 9)
            if child is not None:
                os.waitpid(child.pid, 0)
        except:
            pass
        raise ex
    
    # wait until child is done, kill it if it passes timeout
    niceExit=1
    while child.poll() is None:
        if (time.time() - start)>timeout and timeout!=0:
            niceExit=0
            os.killpg(child.pid, 15)
        if (time.time() - start)>(timeout+1) and timeout!=0:
            niceExit=0
            os.killpg(child.pid, 9)
    if not niceExit and raiseExc:
        raise CommandTimeoutExpired("Timeout(%s) expired for command:\n # %s\n%s" % (timeout, command, output))
    
    print "Child returncode was: %s" % str(child.returncode)
    if child.returncode:
        if exit_on_error:
            exit(1)
        if raiseExc:
            raise ReturnCodeNotZero("Command failed.\nReturn code: %s\nOutput: %s" % (child.returncode, output), child.returncode)
    return (output, child.returncode)
    
def logOutput(fds, start=0, timeout=0, print_to_stdout=False):
    done = 0
    output = ''
    #print 'NEW CALL epoll', fds[0].fileno(), fds[1].fileno()
    
    # set all fds to nonblocking
    for fd in fds:
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        if not fd.closed:
            fcntl.fcntl(fd, fcntl.F_SETFL, flags| os.O_NONBLOCK)
            
    epoll = select.epoll()
    epoll.register(fds[0].fileno(), select.EPOLLIN)
    epoll.register(fds[1].fileno(), select.EPOLLIN)
    reg_num = 2
    try:
        done = False
        while not done:
            events = epoll.poll(1)
            for fileno, event in events:
                if event & select.EPOLLIN:
                    #print (fileno, event)
                    if fileno == fds[0].fileno():
                        r =  fds[0].read()
                        #print r
                        output += r
                        if print_to_stdout:
                            sys.stdout.write(r)
                    else:
                        r = fds[1].read()
                        #print r
                        output += r
                        if print_to_stdout:
                            sys.stdout.write(r)
                elif event & select.EPOLLHUP:
                    epoll.unregister(fileno)
                    reg_num -= 1
                    if not reg_num:
                        done = True
    finally:
        epoll.close()    
    return output 
