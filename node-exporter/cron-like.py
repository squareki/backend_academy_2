import os
import pathlib
import re
import subprocess
from time import sleep

def get_win_ver() -> str:
    output = subprocess.getoutput("ver")
    #print(output)
    search = re.search("Microsoft Windows \[Version ([\d.]+)\]", output)
    version = search.group(1)
    #print(version)
    filepath = pathlib.Path("./node_textfile/windows.prom")
    with open(filepath, "w", newline="") as f:
        f.write("# HELP node_host_machine_windows_info Host Machine Windows Info\n")
        f.write("# TYPE node_host_machine_windows_info gauge\n")
        f.write('node_host_machine_windows_info{version="')
        f.write(version)
        f.write('"} 1\n')
    return version

def get_prom_file_count() -> int:
    _, _, files = next(os.walk(pathlib.Path("./node_textfile")))
    print(files)
    file_count = len([x for x in files if x.endswith(".prom")])
    print(file_count)
    filepath = pathlib.Path("./node_textfile/textfile_collector.prom")
    with open(filepath, "w", newline="") as f:
        f.write("# HELP node_host_machine_textfiles_collected Host Machine Textfiles Collected\n")
        f.write("# TYPE node_host_machine_textfiles_collected gauge\n")
        f.write(f"node_host_machine_textfiles_collected {file_count}\n")
    return file_count

if __name__ == "__main__":
    print("start")
    while True:
        r = get_win_ver()
        n = get_prom_file_count()
        sleep(5)
    print("ok")