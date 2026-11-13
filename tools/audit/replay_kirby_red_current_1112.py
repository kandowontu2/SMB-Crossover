"""Re-run retained natural red-shell encounter without captures or log files."""
import json
from hashlib import sha256
from pathlib import Path
from run_stdout_mesen_1110 import R, run


def controller():
    source=R/'build/kirby-red-shell-1110-v3/controller.lua'
    assert sha256(source.read_bytes()).hexdigest()=='15d360ea10e46543d869b39363dd2bf2718f4f210a3aff7db5a9987d8fb4a14c'
    text=source.read_text()
    first,body=text.split('\n',1)
    body=body.replace(" local f=assert(io.open(OUTPUT..'result.json','w'))\n",'')
    body=body.replace(' f:write(json({',' print(\'SMB_NATIVE_RECEIPT \'..json({')
    body=body.replace('ROM_sha256=C.sha','ROM_SHA256=C.sha')
    begin=body.index(' f:close()\n')
    end=body.index(' emu.stop(passed and 0 or 1)',begin)
    body=body[:begin]+body[end:]
    assert 'io.open' not in body and 'emu.takeScreenshot' not in body
    return first+"\nC.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))\n"+body


def main():
    rom=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    output=R/'build/kirby-red-current-1112'
    output.mkdir(exist_ok=True)
    script=output/'controller.lua'
    script.write_text(controller(),encoding='utf-8',newline='\n')
    result=run(script,rom,output/'capture',sha256(rom.read_bytes()).hexdigest(),90)
    print(json.dumps({k:result[k] for k in ('passed','receipt_SHA256','script_SHA256','receipt')}),flush=True)
    assert result['passed']


if __name__=='__main__':
    main()
