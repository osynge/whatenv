import subprocess, threading

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd


    def run(self, timeout):
        self.process = None
        self.rc = None
        self.stdout = ""
        self.stderr = ""

        def target():
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            self.rc = self.process.wait()
            self.stdout,self.stderr = self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
        return self.rc, self.stdout, self.stderr


if __name__ == "__main__":
    command = Command("echo 'Process started'; sleep 2; echo 'Process finished'")
    print command.run(timeout=3)
    print command.run(timeout=1)
