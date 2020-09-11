import os, sys, time, re

while 1:
    pid = os.getpid()

    #os.write(1, (f"About to fork (pid:{pid})\n").encode())
    #os.write(1, (input("$ ")).encode())

    comand = input("$ ") #prompt for comand and store it 

    #run_comand(comand)

    def run_comand(comand):
        rc = os.fork()

        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        elif rc == 0:                   # child
            args = [comand, "shell-valenciana.py"]
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly

            os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error

        else:                           # parent (forked ok)
            childPidCode = os.wait()
            os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                        childPidCode).encode())

    run_comand(comand)
