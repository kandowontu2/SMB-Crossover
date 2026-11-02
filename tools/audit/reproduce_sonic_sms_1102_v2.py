"""Reproduce the exact supplied SMS Sonic ROM from pinned original assembly."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/sonic-sms-original-1102-v2'
PIN='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'

def main():
    q=json.loads((O/'prepared.json').read_text())
    for row in q['extractor']+q['tools']:assert sha(O/row['path'])==row['SHA256']
    exports=[]
    for line in (O/'annot/sonic1.cfg').read_text().splitlines():
        words=line.strip().split()
        if words and words[0]=='binexport':
            dest=(O/words[3]).resolve();assert dest.is_relative_to(O.resolve())
            dest.parent.mkdir(parents=True,exist_ok=True);exports.append(dest)
    assert len(exports)==258
    for name in ['baserom','build','out']:(O/name).mkdir(exist_ok=True)
    with zipfile.ZipFile('C:/Users/kando/Downloads/Sonic The Hedgehog (USA Europe Brazil) (En).zip') as z:
        raw=z.read('Sonic The Hedgehog (USA, Europe, Brazil) (En).sms')
    assert hashlib.sha256(raw).hexdigest()==PIN
    (O/'baserom/sonic1.sms').write_bytes(raw)
    steps=[('extract',[sys.executable,'-B','tools/rom_unpack.py','baserom/sonic1.sms','annot/sonic1.cfg','src/whole.asm']),
           ('assemble',[str(O/'bin/wla-z80.exe'),'-w','-o','build/whole.o','src/whole.asm']),
           ('link',[str(O/'bin/wlalink.exe'),'-r','-s','src/whole.lnk','out/s1.sms'])]
    for name,cmd in steps:
        p=subprocess.run(cmd,cwd=O,capture_output=True,text=True)
        (O/(name+'.log')).write_text(p.stdout+p.stderr)
        assert p.returncode==0,(name,p.stderr[-2000:])
    result=(O/'out/s1.sms').read_bytes();assert result==raw
    files=[p for p in O.rglob('*') if p.is_file()]
    report=dict(passed=True,original_ROM_reproduced=True,ROM_SHA256=sha(O/'out/s1.sms'),source_revision=q['source_revision'],
                files=len(files),bytes=sum(p.stat().st_size for p in files),exports=len(exports),
                scope='Pinned extractor generates original assembly; WLA-Z80 and linker reconstruct all262144bytes exactly. Not an NES translation or gameplay qualification.',
                bindings={str(p):sha(p) for p in [Path(__file__),O/'prepared.json',O/'annot/sonic1.cfg',O/'src/whole.asm',O/'out/s1.sms']})
    (O/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
