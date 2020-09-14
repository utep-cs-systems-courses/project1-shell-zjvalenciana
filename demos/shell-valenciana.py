import os, sys, time, re

while 1: #keep rinning until user exits
    cwd = os.getcwd()
    pid = os.getpid()

    comand = [str(n) for n in input('$ ').split()] #prompt for command and parameters 

    def run_comand(comand):
        rc = os.fork()
        args = comand.copy()
        
        if args[0] == 'exit':
            sys.exit(0)


        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)






        elif rc == 0:                   # child

            if args[0] == 'cd':         # change directory 
                os.chdir(args[1])

            if '>' in args:
                os.close(1)                 # redirect child's stdout
                os.open(args[-1], os.O_CREAT | os.O_WRONLY);
                os.set_inheritable(1, True)

                argg = args[0:args.index(">")]

                for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                    program = "%s/%s" % (dir, argg[0])
                    os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                    try:
                        os.execve(program, argg, os.environ) # try to exec program
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly

                os.write(2, (f"{argg[0]}: command not found.").encode())
                sys.exit(1)                 # terminate with error

            if '<' in args:
                os.close(0)                 # redirect child's stdin
                os.open(args[-1], os.O_RDONLY);
                os.set_inheritable(0, True)

                argg = args[0:args.index("<")]

                for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                    program = "%s/%s" % (dir, argg[0])
                    os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                    try:
                        os.execve(program, argg, os.environ) # try to exec program
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly

                os.write(2, (f"{argg[0]}: command not found.").encode())
                sys.exit(1)                 # terminate with error

            else:
                for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                    program = "%s/%s" % (dir, args[0])
                    os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                    try:
                        os.execve(program, args, os.environ) # try to exec program
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly

                os.write(2, (f"{args[0]}: command not found.").encode())
                sys.exit(1)                 # terminate with error







        else:                           # parent (forked ok)
            childPidCode = os.wait()
            os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                        childPidCode).encode())
            print(f"current directory: {cwd}")
    
    if not comand: #if no commands typed keep prompting
        pass
    else:
        run_comand(comand) #if command passed execute