"""Measure actual6502 native world material/geometry/align leaves privately."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import recover_prince_core_1101_v1 as B
from private_build_outputs_v1 import validate
P,O=B.P,B.O


def main():
 c=P.T.labels(O/'world-coordinates-v7.lbl');point=P.T.labels(O/'contact-point.lbl')
 src=R/'tools/reference/prince_host_world_1102_v8.s'
 pre=''.join(f'{n}=${a:04x}\n'for n,a in dict(SourceWorldContext=c['PpWorldContext'],SourceWorldColumn=c['PpWorldColumn'],SourceWorldPrivateMap=c['PpWorldPrivateMap'],**{n:point[n]for n in ['PpQueryX','PpQueryY','PpHostReadPoint']}).items())
 asm=O/'host-world-v8.s';asm.write_text(pre+src.read_text());cfg=O/'host-world-v8.cfg'
 start=c['PpWorldCoordinateEnd']
 slots={'WORLD_EXTRA':(start,0xc360-start),'WORLD_GEOMETRY':(0xc4ff,0x110),'WORLD_MATERIAL':(0xbd83,0x25d),'WORLD_ALIGN':(0xc40b,0xa6),'WORLD_LANDING':(0xc362,0x9f)}
 cfg.write_text('MEMORY{'+''.join(f'M{i}:start=${a:04x},size=${size:x},file=%O;'for i,(a,size)in enumerate(slots.values()))+'}SEGMENTS{'+''.join(f'{n}:load=M{i},type=ro,define=yes;'for i,n in enumerate(slots))+'}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/'host-world-v8.o'],[cc/'ld65.exe','-C',cfg,O/'host-world-v8.o','-o',O/'host-world-v8.bin','-Ln',O/'host-world-v8.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 labels=P.T.labels(O/'host-world-v8.lbl');offset=0;regions=[]
 for n,(at,size)in slots.items():
  used=labels[f'__{n}_SIZE__'];regions.append(dict(segment=n,half_open=[at,at+used],source_file_offset=offset,bytes=used,remaining=size-used));offset+=used
 assert offset==(O/'host-world-v8.bin').stat().st_size
 q=dict(measured=True,qualified=False,private_proposal_only=True,host_ROM_created=False,code_bytes=offset,regions=regions,owned_geometry_state_half_open=[0xc078,0xc0a6],scope='Compiled native metatile authority, original32x64 world coordinate transform, actual surface/swept landing and align bindings. Update/export/camera/health/combat/owner hooks remain separate; executable state slots are conditional private proposals.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),src,asm,O/'host-world-v8.bin',O/'world-coordinates-v7.bin',O/'contact-point.bin']})
 (O/'host-world-layout-v8.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
