"""Keep Tank's normal Mario animation while preserving projectile processing."""
from pathlib import Path
import hashlib,json,subprocess
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
R=Path(__file__).resolve().parents[2];BASE=R/'build/mario-tank-visible-host-1101-v5';O=R/'build/tank-normal-walk-1101-v33'

def main():
 O.mkdir(exist_ok=True);b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw'])
 assert hashlib.sha256(raw).hexdigest()=='7ec9cd5c4a462d0f4638c00ed35bc53a94c05cb80f4699f443245c0f754e3a1f'
 row=next(x for x in json.loads((BASE/'graft-assembly.json').read_text())['source_owner_intervals'] if x['name']=='MT_LOAD_MAP')
 assert row['bank']==82 and row['remaining']==27
 pc=row['run_PC']+row['used'];at=16+82*8192+(pc&8191);assert raw[at:at+27]==bytes([255])*27
 start=location(b,'BmGraphics');entry=address(b,'BmGraphics');hook=start+0x17
 # Current source: MarioVariant load, CMP4/BEQ Celeste, native farcall.
 assert raw[start+0x10:start+0x17]==bytes([0xad,address(b,'MarioVariant')&255,address(b,'MarioVariant')>>8,0xc9,4,0xf0,0x21])
 old=bytes(raw[hook:hook+18]);assert old[0]==141 and old[15]==32
 def far(target,bank,tail):
  safe=address(b,'SafecallA_SMC')+1;ptr=address(b,'FarcallJmpTarget_SMC');common=address(b,'FarCallCommon')
  return bytes([141,safe&255,safe>>8,169,target&255,141,(ptr+1)&255,(ptr+1)>>8,169,target>>8,141,(ptr+2)&255,(ptr+2)>>8,169,bank,76 if tail else 32,common&255,common>>8])
 native=old[4]+256*old[9];assert old==far(native,129,False)
 source=f''' ; A is the MarioVariant value at the verified BmGraphics callsite.
.segment "CODE"
cmp #7
bne Native
lda #0
sta ${address(b,'MegaManShotPose'):04x}
Native:
.byte {','.join(str(x) for x in far(native,129,True))}
'''
 (O/'walk.s').write_text(source);(O/'walk.cfg').write_text(f'MEMORY {{ H:start=${pc:04x},size=27,file=%O; }} SEGMENTS {{ CODE:load=H,type=ro; }}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',O/'walk.s','-o',O/'walk.o'],[cc/'ld65.exe','-C',O/'walk.cfg',O/'walk.o','-o',O/'walk.bin']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 code=(O/'walk.bin').read_bytes();assert len(code)==27;raw[at:at+27]=code;raw[hook:hook+18]=far(pc,210,False)
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 q=dict(passed=True,ROM_sha256=hashlib.sha256(raw).hexdigest(),helper_PC=pc,helper_offset=at,hook_PC=entry+0x17,hook_offset=hook,old_call=old.hex(),helper_bytes=27,source_sha256=hashlib.sha256(source.encode()).hexdigest(),installed=False,scope='Only MarioVariant7 clears the source throw-pose latch immediately before native graphics. Actual shot processing already ran and is unchanged. Uses exactly the granted MT_LOAD_MAP27B remainder; no CHR or RAM-cookie change. Tests pending; always-glowing shoes not integrated.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
