"""Compose current nightly plus granted Metal source, then wire scene loading."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
O=R/'build/metal-storm-lifecycle-1101-v13'
M=R/'build/metal-storm-native-integration-1101-v12'
C=R/'build/mario-tank-visible-host-1101-v5'
B=R/'build/karnov-native-platform-1101-v1'
REF=R/'tools/reference/metal_storm_scene_1101_v13.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert sha(C/'candidate.nes')=='7ec9cd5c4a462d0f4638c00ed35bc53a94c05cb80f4699f443245c0f754e3a1f'
    assert sha(M/'candidate.nes')=='83c9990061715416f8773555e11692747e2ba2a95411caa666c4326966f11150'
    assert sha(B/'candidate.nes')=='58e50db6ceead7c3706087c92d6e49014f05ff8b80b000be30c27b4e7dfa11f2'
    stage=json.loads((M/'native-owning-link.json').read_text())
    for p,h in stage['bindings'].items():assert sha(p)==h,p
    O.mkdir(exist_ok=True)
    base=(B/'candidate.nes').read_bytes();current=(C/'candidate.nes').read_bytes();metal=(M/'candidate.nes').read_bytes()
    raw=bytearray(current)
    for i,(a,z) in enumerate(zip(base,metal)):
        if a!=z:
            assert current[i] in (a,z),('Conflicting source ownership',i)
            raw[i]=z
    t=(M/'native-component.s').read_text()
    old=' Ms8Far Ms8Finish,99\n rts\nMs8WorkYes:sec\n rts'
    new=' Ms8Far Ms8Finish,99\n bcc Ms8WorkNo\nMs8WorkYes:\n Ms8Far Ms13Fresh,36\n rts'
    assert t.count(old)==1;t=t.replace(old,new)
    host=qualified(C/'candidate.nes')
    t+='\nKrSceneInit=$%04x\n'%address(host,'KrSceneInit')+REF.read_text()
    (O/'component.s').write_text(t)
    cfg=(M/'native-component.cfg').read_text().replace(M.as_posix(),O.as_posix())
    (O/'component.cfg').write_text(cfg)
    cc=R/'tools/Windows/cc65/bin'
    commands=[[cc/'ca65.exe','-g','--bin-include-dir',M,'--bin-include-dir',R/'build/metal-storm-render-host-1101-v7',O/'component.s','-o',O/'component.o'],
              [cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'unused.bin','-Ln',O/'component.lbl']]
    for command in commands:
        command=list(map(str,command));validate(command,O,cwd=R)
        p=subprocess.run(command,cwd=R,capture_output=True,text=True);assert p.returncode==0,p.stderr
    labels={m[2]:int(m[1],16) for line in (O/'component.lbl').read_text().splitlines() if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
    patches=[]
    for role,bank,off,cap in [('work',37,0x1f89,119),('check',21,0x1f8a,118),('copy',36,0x1f46,122)]:
        data=(O/f'native-{role}.bin').read_bytes();assert len(data)<=cap
        old=(M/f'native-{role}.bin').read_bytes();at=16+bank*8192+off
        assert raw[at:at+len(old)]==old and raw[at+len(old):at+cap]==b'\xff'*(cap-len(old))
        patches.append(dict(role=role,offset=at,old=bytes(raw[at:at+cap]).hex(),new=(data+b'\xff'*(cap-len(data))).hex()))
        raw[at:at+cap]=data+b'\xff'*(cap-len(data))
    # Every other compiled capsule byte stays identical, including both code fingerprints.
    for p in O.glob('native-*.bin'):
        if p.name not in ['native-work.bin','native-check.bin','native-copy.bin']:
            assert p.read_bytes()==(M/p.name).read_bytes(),p.name
    def call(pc,bank):return bytes([0x8d,0x6a,1,0xa9,pc&255,0x8d,0x6c,1,0xa9,pc>>8,0x8d,0x6d,1,0xa9,128|bank,0x20,address(host,'FarCallCommon')&255,address(host,'FarCallCommon')>>8])
    at=location(host,'InitScreen');old=call(address(host,'KrSceneInit'),29)
    index=current.find(old,at,at+100);assert index>=at and current.count(old,at,at+100)==1
    new=call(labels['Ms13Scene'],21);assert raw[index:index+18]==old
    raw[index:index+18]=new;patches.append(dict(role='InitScreen scene chain',offset=index,old=old.hex(),new=new.hex()))
    (O/'candidate.nes').write_bytes(raw)
    for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((C/('candidate'+suffix)).read_bytes())
    receipt=dict(passed=True,installed=False,menu_admitted=False,ROM_sha256=sha(O/'candidate.nes'),base_ROM_sha256=sha(C/'candidate.nes'),
                 scene_hook_wired=True,source_fragments=patches,labels={n:labels[n] for n in ['Ms13Scene','Ms13Fresh','Ms8Load']},
                 scope='Current nightly retained byte-for-byte outside existing granted Metal delta and explicit scene call. No playable admission, native gameplay, combat, health, audio or full-stage claim.',
                 bindings={str(p):sha(p) for p in [Path(__file__),REF,M/'native-component.s',M/'native-owning-link.json',C/'candidate.nes',O/'component.s',O/'component.cfg',O/'candidate.nes']})
    (O/'scene-assembly.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ['bindings','source_fragments']}))
if __name__=='__main__':main()
