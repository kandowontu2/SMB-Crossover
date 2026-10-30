"""Update an unexecuted legacy prepare receipt to the supported output runner."""
from pathlib import Path
import argparse
import hashlib
import json

R=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('folder',type=Path)
    a=p.parse_args()
    folder=a.folder.resolve()
    assert folder.is_relative_to(R/'build')
    assert not any((folder/n).exists() for n in ['execution.json','result.json','ready-legacy-runner.json'])
    ready=folder/'ready.json'
    record=json.loads(ready.read_text())
    assert record['prepared'] and not record['native_run']
    for path,expected in record['bindings'].items():assert sha(path)==expected,path
    old=R/'tools/audit/run_mesen_isolated.py'
    new=R/'tools/audit/run_mesen_output_v2.py'
    command=record['command']
    assert Path(command[2]).resolve()==old
    command[2]=str(new)
    previous=folder/'ready-legacy-runner.json'
    previous.write_bytes(ready.read_bytes())
    record['bindings'].update({str(previous):sha(previous),str(new):sha(new),str(Path(__file__)):sha(__file__)})
    record['runner_update']='Supported SMB_RUN_OUTPUT adapter; same ROM/controller/emulator/options/frame bound. No emulator launched.'
    ready.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(ready=str(ready),sha256=sha(ready),command=command)))


if __name__=='__main__':main()
