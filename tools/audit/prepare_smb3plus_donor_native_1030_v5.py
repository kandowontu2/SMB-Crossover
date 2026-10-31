"""Apply donor controller pulses at Mesen's genuine input-polled event."""
from pathlib import Path
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_smb3plus_donor_native_1030_v4 as P


def main():
    # Generate the same bounded observation packet, then correct the input
    # consumer before freezing readiness or running anything.
    output=Path(sys.argv[sys.argv.index('--output')+1]).resolve()/'discovery'
    assert not output.exists()
    P.main()
    path=output/'controller.lua';text=path.read_text()
    assert text.count('    emu.setInput(input, 0, 0)')==1
    text=text.replace('    emu.setInput(input, 0, 0)','')
    text+='''
local polls, driven = 0, 0
emu.addEventCallback(function()
    local input = {}
    for _, pulse in ipairs(PULSES) do
        if frame >= pulse[1] and frame < pulse[1] + 4 then
            input[string.lower(pulse[2])] = true
            driven = driven + 1
        end
    end
    emu.setInput(input, 0)
    polls = polls + 1
end, emu.eventType.inputPolled)
'''
    path.write_text(text,encoding='utf-8',newline='\n')
    ready=output/'ready.json';d=json.loads(ready.read_text())
    d['input_application']='inputPolled (older startFrame-only input was ineffective)'
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    d['bindings'][str(Path(__file__))]=sha(__file__)
    d['bindings'][str(path)]=sha(path)
    ready.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()
