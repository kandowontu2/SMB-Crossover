"""Correct the Lua integer/concatenation token before freezing the new packet."""
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_smb3plus_kick_discovery_1031_v2 as P


def main():
    P.main()
    out=Path(sys.argv[sys.argv.index('--output')+1]).resolve()/'discovery'
    script=out/'controller.lua';text=script.read_text()
    assert text.count('cm.address//8192..')==1
    text=text.replace('cm.address//8192..','tostring(cm.address//8192)..')
    script.write_text(text,encoding='utf-8',newline='\n')
    ready=out/'ready.json';d=json.loads(ready.read_text())
    for p in [Path(__file__).resolve(),script]:d['bindings'][str(p)]=P.P.sha(p)
    ready.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()
