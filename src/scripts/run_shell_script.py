import subprocess
from pathlib import Path
import os

script_location = Path(__file__).absolute().parent
shell_script = os.path.join(script_location, 'start.sh')

print(f'running {shell_script}')
with open(shell_script, "r", encoding="utf-8") as fp:
    for line in fp.read().split("\n"):
        process = subprocess.Popen(line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        if process.returncode:
            raise RuntimeError("start.sh returned non-zero exit code")