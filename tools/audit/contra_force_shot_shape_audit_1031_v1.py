"""Source-authentic CF shot radii/art bounds and original collision comparator."""
from pathlib import Path
import hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_weapon_probe_v1 as W
T=W.T
O=R/'build/contra-force-shot-shape-audit-1031-v1';K=R/'build/contra-force-scroll-publisher-1031-v2/kernel';J=K.parent/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
L={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(K/'runtime.lbl').read_text())}
q3=(K/'ram3.bin').read_bytes();raw=(J/'candidate.nes').read_bytes();cs=16+128*8192
radius=[list(T.Mem()[0xf94a+i:0xf94c+i])for i in range(0,58,2)]
def art(frame):
 i=q3[L['CfShotFrameIndex']-0xa000+frame];size=q3[L['CfShotBytes']-0xa000+i]
 ptr=q3[L['CfShotLo']-0xa000+i]+256*q3[L['CfShotHi']-0xa000+i];rec=list(q3[ptr-0xa000:ptr-0xa000+size]);pixels=[]
 for k in range(0,len(rec),4):
  dy,dx,tile,attr=rec[k:k+4];dy=dy-256 if dy>=128 else dy;dx=dx-256 if dx>=128 else dx
  at=((tile&1)*4096+(tile&254)*16)%1024;pat=raw[cs+968*1024+at:cs+968*1024+at+32]
  for yy in range(16):
   py=15-yy if attr&128 else yy;a=(py//8)*16+py%8
   for xx in range(8):
    b=xx if attr&64 else 7-xx
    if ((pat[a]>>b)&1)|(((pat[a+8]>>b)&1)<<1):pixels.append((dx+xx,dy+1+yy))
 return dict(frame=frame,record=rec,opaque_pixels=len(pixels),bounds=[min(x for x,y in pixels),min(y for x,y in pixels),max(x for x,y in pixels),max(y for x,y in pixels)]if pixels else None)
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,source_CPU=True,native=False,rows=[],original_comparator=[],radii=radius)
 try:
  linked=(K/'ram2.bin').read_bytes()[L['tbl_F94A']-0xc000:L['tbl_F94A']-0xc000+58];assert linked==bytes(v for pair in radius for v in pair)
  for v in range(4):
   for facing,pad in [('right',1),('left',2)]:
    c=W.machine(v,0);m=c.memory;T.step(c,pad)
    for _ in range(4):T.step(c,4)
    bodyY=m[0x668];T.step(c,68);T.call(c,0x8132)
    shots=W.slots(m);assert shots
    for shot in shots:
     idx=shot['age'];assert idx==6 and radius[idx]==[6,8]
     shot['original_radius_index']=idx;shot['original_radii']=radius[idx];shot['art']=art(shot['animation'][0])
     shot['body_anchor_Y']=bodyY;shot['shot_anchor_offset_Y']=shot['y']-bodyY
    d['rows'].append(dict(class_id=v,facing=facing,bodyY=bodyY,shots=shots))
  # Actual fixed source FAE6 comparator with legal source actor fields. Target
  # radius1=[3,3] is an explicitly declared donor-arena target, not an SMB box.
  for dx in(-9,-8,0,8,9):
   for dy in(-11,-10,0,10,11):
    c=W.machine(0,0);m=c.memory;m[0x782+2]=1;m[0x682+2]=1;m[0x720+2]=1;m[0x64e+2]=112;m[0x668+2]=168
    m[0x682+10]=1;m[0x720+10]=6;m[0x64e+10]=112+dx;m[0x668+10]=168+dy
    T.call(c,0xfa16,x=2);m[0x0e]=1;T.call(c,0xfae6,x=10)
    found=bool(m[0x74c+2]);assert found==(abs(dx)<9 and abs(dy)<11),(dx,dy,found)
    d['original_comparator'].append(dict(dx=dx,dy=dy,hit=found,target_radius=[3,3],projectile_radius=[6,8]))
  pulse=json.loads((R/'build/contra-force-scroll-combat-pulse-controls-1031-v1/controls.json').read_text());f=next(f for f in pulse['cohorts'][0]['frames']if f['source_shots'])
  sy=f['source_shots'][0]['y'];goomba=f['enemies'][0];off=f['native_boxes'][0]['offsets'];top=goomba['y']+off[1]
  d.update(passed=True,linked_original_table=dict(CPU=L['tbl_F94A'],raw_bank=2,bytes_exact=True),settled_native_negative=dict(shot_anchorY=sy,native_GoombaY=goomba['y'],native_bbox=off,native_top=top,source_radiusY=8,closed_shot_bottom=sy+8,point_misses=sy<top,radius_still_misses=sy+8<top,source_art=art(5)),
   conclusion='Point-only host test is incomplete, but genuine pistol radius6/8 alone still misses the settled-Y189 reduced nativeGoomba box by1pixel. Preserve this negative; do not move original muzzle/art. A native-target body adaptation must be explicit if needed.',scope='8 actual original class/facing crouch-pistol allocations plus25 original fixed collision executions. No hosted kill, native run, target health or readiness claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  refs=[Path(__file__),Path(W.__file__),Path(T.__file__),T.P/'candidate.nes',T.P/'candidate.dbg',T.P/'copy_bank_FF.asm',T.P/'copy_bank_04.asm',K/'runtime.lbl',K/'ram2.bin',K/'ram3.bin',J/'candidate.nes',R/'build/contra-force-scroll-combat-pulse-controls-1031-v1/controls.json']
  d['bindings']={str(p.resolve()):sha(p)for p in refs};p=O/'audit.json';p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],error=d.get('error'))),flush=True)
if __name__=='__main__':main()
