"""Measure the translated float fragments before assigning existing spans."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from private_build_outputs_v1 import validate
O=R/'build/smb3plus-peach-float-code-1031-v1'
P=R/'build/smb3plus-kick-host-1031-v1/joint'
S=R/'tools/reference/smb3plus_peach_float_1031_v1.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir(parents=True)
    b=scoped_load(P/'candidate.nes');source=S.read_text()
    names=sorted(set(re.findall(r'M3Native::(\w+)',source)))
    prefix='.setcpu "6502X"\n.scope M3Native\n'
    prefix+=''.join(f'{n}=${address(b,"M3Native::"+n):04x}\n' for n in names)
    prefix+='.endscope\n'+''.join(f'{n}=${address(b,n):04x}\n' for n in ['M3Variant','M3Form'])
    procs=re.findall(r'\.proc (\w+)',source)
    prefix+='\n.export '+','.join(procs)+'\n.segment "CODE"\n'
    (O/'float.s').write_text(prefix+source,encoding='utf-8',newline='\n')
    (O/'private.cfg').write_text('MEMORY { CODE:start=$c000,size=$2000,type=ro,file=%O; }\nSEGMENTS { CODE:load=CODE,type=ro; }\n',encoding='utf-8')
    for label,cmd in [
        ('compile',[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-o',str(O/'float.o'),str(O/'float.s')]),
        ('link',[str(R/'tools/Windows/cc65/bin/ld65.exe'),'-C',str(O/'private.cfg'),'-o',str(O/'measure.bin'),'--dbgfile',str(O/'measure.dbg'),str(O/'float.o')])]:
        validate(cmd,O,cwd=R);p=subprocess.run(cmd,capture_output=True,text=True,cwd=R)
        (O/(label+'.json')).write_text(json.dumps(dict(command=cmd,returncode=p.returncode,
            stdout=p.stdout,stderr=p.stderr),indent=2)+'\n',encoding='utf-8')
        assert not p.returncode,(label,p.stderr)
    sizes={}
    for line in (O/'measure.dbg').read_text().splitlines():
        if line.startswith('scope\t'):
            q=dict(t.split('=',1) for t in line[6:].split(',') if '=' in t)
            if q.get('name','').strip('"') in procs:sizes[q['name'].strip('"')]=int(q['size'],0)
    assert len(sizes)==len(procs)
    d=dict(measurement_only=True,cartridge_linked=False,source=True,native=False,
        function_sizes=sizes,total_bytes=sum(sizes.values()),
        bindings={str(p):sha(p) for p in [Path(__file__),S,P/'candidate.nes',P/'candidate.dbg',
            O/'float.s',O/'private.cfg',O/'compile.json',O/'link.json',O/'float.o',O/'measure.bin',O/'measure.dbg']})
    (O/'measurement.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(sizes=sizes,total=d['total_bytes'])))


if __name__=='__main__':main()
