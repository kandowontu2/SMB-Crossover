"""Provide a cold ROM world-palette callback in source-proven HUD padding."""
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_probes_1101_v17 as P
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
O=R/'build/metal-storm-palette-1101-v18';REF=R/'tools/reference/metal_storm_world_palette_1101_v18.inc'
sha=P.P.P.sha
def main():
    O.mkdir(exist_ok=True);b=qualified(P.O/'candidate.nes');meta=qualified(R/'build/metal-storm-native-integration-1101-v12/candidate.nes');raw=bytearray(b['raw'])
    source=R/'build/bt-ready-menu-1031-v2/joint/src/chip_dale_health.s';text=source.read_text()
    assert 'jmp CdQueueHud\n .res 48,$ea' in text
    start=location(b,'CdHud');at=start+27;assert at==16+79*8192+0x707
    assert raw[at-3:at]==bytes([0x4c,address(b,'CdQueueHud')&255,address(b,'CdQueueHud')>>8])
    assert raw[at:at+48]==bytes([0xea])*48 and address(b,'CdHud::Done')==0xa737
    names=['FarcallJmpTarget_SMC','NextBank_SMC','HuCommonRestore','HuNativeWorldPalette']
    definitions=''.join(f'{n}=${address(b,n):04x}\n' for n in names)
    (O/'helper.s').write_text(definitions+REF.read_text())
    (O/'helper.cfg').write_text('MEMORY { H:start=$a707,size=48,file=%O; } SEGMENTS { CODE:load=H,type=ro; }')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'helper.s','-o',O/'helper.o'],[cc/'ld65.exe','-C',O/'helper.cfg',O/'helper.o','-o',O/'helper.bin']]:
        cmd=list(map(str,cmd));validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);assert p.returncode==0,p.stderr
    data=(O/'helper.bin').read_bytes();assert len(data)<=48
    patches=[]
    def patch(at,old,new,role):
        assert len(old)==len(new) and raw[at:at+len(old)]==old
        raw[at:at+len(old)]=new;patches.append(dict(role=role,offset=at,old=old.hex(),new=new.hex()))
    patch(at,bytes([0xea])*len(data),data,'Source-explicit unreachable Chip HUD padding')
    entry=location(meta,'Ms12MetalRoute');assert raw[entry:entry+2]==bytes([0xa9,0xab])
    patch(entry,bytes(raw[entry:entry+3]),bytes([0x4c,0x07,0xa7]),'Metal route cold world palette dispatch')
    (O/'candidate.nes').write_bytes(raw)
    for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((P.O/('candidate'+suffix)).read_bytes())
    q=dict(passed=True,installed=False,ROM_sha256=sha(O/'candidate.nes'),base_ROM_sha256=sha(P.O/'candidate.nes'),patches=patches,
           allocation=dict(bank=79,offset_half_open=[0x707,0x737],source=str(source),source_sha256=sha(source),capacity=48,used=len(data)),
           rationale='World palette service32 runs in immutable ROM and restores the original HuCommon Y/P frame before the native area selector. Other services retain their original transport.',
           bindings={str(p):sha(p) for p in [Path(__file__),REF,source,P.O/'candidate.nes',O/'helper.s',O/'candidate.nes']})
    (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k not in ['patches','bindings']}))
if __name__=='__main__':main()
