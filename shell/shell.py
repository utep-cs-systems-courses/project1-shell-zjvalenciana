#! /usr/bin/env python3

import os, sys, time, re

while 1: #keep rinning until user exits

    pid = os.getpid()

    if 'PS1' in os.environ: #if we have PS1 in envirnment use
        os.write(1, (os.environ['PS1']).encode())
        try:
            comand = [str(n) for n in input().split()]
        except EOFError:    #catch error
            sys.exit(1)
    else:
        os.write(1, ('$ ').encode())    #otherwise type $
        try:
            comand = [str(n) for n in input().split()]
        except EOFError:    #catch error
            sys.exit(1)


    if 'cd' in comand:         # change directory 
        try:
            os.chdir(comand[1])
        except FileNotFoundError:   #catch error
            pass
        continue

    def exe(args): #exec 
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            #os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly

        os.write(2, (f"{args[0]}: command not found.").encode())
        sys.exit(1)                 # terminate with error

    def run_comand(comand):
        rc = os.fork()      #create child process 
        args = comand.copy()


        if '&' in args:
            args.remove('&')

        if 'exit' in args: # exit rpogram 
            sys.exit(0)


        if rc < 0:                      #frok failed 
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        elif rc == 0:                   # child
            if '>' in args:
                os.close(1)                 # redirect child's stdout
                os.open(args[-1], os.O_CREAT | os.O_WRONLY);
                os.set_inheritable(1, True)

                argg = args[0:args.index(">")]
                exe(argg)

            if '<' in args:
                os.close(0)                 # redirect child's stdin
                os.open(args[-1], os.O_RDONLY);
                os.set_inheritable(0, True)

                argg = args[0:args.index("<")]
                exe(argg)

            '''if '/' in args:
                program = args[0]
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass'''   

            if '|' in args:                 #pipe command 
                args = ' '.join([str(elem) for elem in args])
                pipe = args.split("|")
                prog1 = pipe[0].split()
                prog2 = pipe[1].split()

                pr, pw = os.pipe()  #file descriptors for reading and writing
                for f in (pr, pw):
                    os.set_inheritable(f, True)

                pipeFork = os.fork()
                if pipeFork < 0:    #fork failed
                    os.write(2, ("fork failed").encode())
                    sys.exit(1)
                
                elif pipeFork == 0: #child process which will write to pipe
                    os.close(1)     #close fd 1 and rederict it
                    os.dup(pw)      #attach fd1 to pipe input fd
                    os.set_inheritable(1, True) #set fd1 inheritable
                    for fd in (pr, pw):
                        os.close(fd)
                    exe(prog1)

                else:               #parent
                    os.close(0)
                    os.dup(pr)
                    os.set_inheritable(0, True)
                    for fd in (pw, pr):
                        os.close(fd)
                    exe(prog2)

            else:
                exe(args)


        else:                           # parent (forked ok)
            if not '&' in comand:
                #os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % (pid, rc)).encode())
                childPidCode = os.wait() #wait and get child pid and return code 
                #os.write(1, ("Parent: Child %d terminated with exit code %d\n" % childPidCode).encode())


    if not comand: #if no commands typed keep prompting
        pass
    else:
        run_comand(comand) #if command passed execute