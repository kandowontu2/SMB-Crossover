"""Actual sourcecart completed-group/OAM/pattern/PPU pairs; no native claim.
Frozen exact-source atlas/pose qualification is the pixel oracle. This test
checks its actual importer/emitter/final mapper/palette composition, not a
new original-game action legality or a claim that hardware shows >8/line.
"""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import contra_force_p1_stale_palette_ppu_v2 as F
V=F.V;Q,T,C=V.Q,V.T,V.C;O=R/'build/contra-force-p1-group-ppu-controls-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=R/'build/contra-force-body-pack-v3';SHOT=R/'build/contra-force-shot-pack-v1'
BM=json.loads((BODY/'packing.json').read_text());SM=json.loads((SHOT/'packing.json').read_text());BA=(BODY/'atlas.chr').read_bytes();SA=(SHOT/'atlas.chr').read_bytes()
def decode(pair):
 return [[((pair[y//8*16+y%8]>>(7-x))&1)|(((pair[y//8*16+y%8+8]>>(7-x))&1)<<1)for x in range(8)]for y in range(16)]
def pixels(records,pattern,pal):
 out={}
 for i,r in reversed(list(enumerate(records))):
  y,t,a,x=r
  if y>=240:continue
  v=decode(pattern(i,t))
  for yy in range(16):
   for xx in range(8):
    z=v[15-yy if a&128 else yy][7-xx if a&64 else xx]
    if z:out[(x+xx,y+1+yy)]=(pal[a&3][z],a&32)
 return out
def actual_pattern(m,t):
 start=(t&1)*4096+(t&254)*16;raw=T.B['raw']
 return bytes(raw[1048592+m.chr_latches[(start+i)//1024]*1024+(start+i)%1024]for i in range(32))
def maxline(records):return max([0]+[sum(y+1<=line<y+17 for y,_,_,_ in records if y<240)for line in range(240)])
def expected(parts,x,y,bodypage=None,loan=False):
 rows=[];patterns=[]
 for p in parts:
  attr=p['attr'];tile=2*p['local_pair']if bodypage is not None else p['target_window6_tile']
  if bodypage is None and attr&3==3:attr=(attr&252)|1
  if loan:attr|=8
  rows.append([y+p['y']-128,tile,attr,x+p['x']-128]);at=(bodypage*1024 if bodypage is not None else 0)+p['local_pair']*32;patterns.append((BA if bodypage is not None else SA)[at:at+32])
 return rows,patterns
def draw(m):
 capture={}
 def hook(c,i):
  if m.rawtags[1]!=3:return
  if c.pc==Q.L['CfP1EarlyTag']:capture['early']=list(m[512:512+T.get(m,'CurrentOAMOffset')])
  if c.pc==Q.L['CfP1LateEntry']:capture['prelate']=[list(m[512+i:516+i])for i in range(0,256,4)]
 z=Q.V.invoke(m,'FwNativeDrawAll',a=87,p=0x79,hook=hook)
 assert set(capture)=={'early','prelate'}
 return capture,z
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,ready=False,checks={},scope='Explicit source pose/frame fixtures; actual24KBloader/auth importer/source emitter/nativeDrawAll/normalNMI. Pixel references inherit frozen original-source atlas qualification. Hardware8/line saturation measured separately; not all-pixel visibility/admission.')
 try:
  for doc in [BM,SM]:
   for p,h in doc['bindings'].items():assert sha(p)==h,p
  base=V.scene();bp=next(v for v in BM['per_pose_source_metadata']if v['variant']==0 and v['frame']==base.ram[2][0x31a]);body,bodypat=expected(bp['parts'],104,192,bp['local_page'])
  native_palette=list(T.B['raw'][T.location(T.B,'GroundPaletteData')+3:T.location(T.B,'GroundPaletteData')+35]);rows=[];by={v['frame']:v for v in SM['views']}
  for frame,v in by.items():
   m=C.clone(base);m.vram[0x3f00:0x3f20]=bytes(native_palette)
   T.put(m,VRAM_Buffer1_Offset=0);m[T.address(T.B,'VRAM_Buffer1')]=0;Q.public(m,26)
   for at,value in [(0x382+10,v['source_witness']['kind']),(0x31a+10,frame),(0x334+10,v['high'])]:m.ram[2][at]=value
   loan=any(p['attr']&3==3 for p in v['target_parts']);shot,shotpat=expected(v['target_parts'],144,176,loan=loan)
   for epoch in range(2):
    cap,z=draw(m);want=body+shot;actual=[cap['early'][i:i+4]for i in range(0,len(cap['early']),4)]
    assert actual==want,('exact source early body+shot',frame,epoch,actual,want)
    last=T.get(m,'SmFreezeLastBlue');cf=last==193;pre=cap['prelate'];post=[list(m[512+i:516+i])for i in range(0,256,4)]
    for i,(a,b)in enumerate(zip(pre,post)):
     marker=a[2]&24;hidden=(marker==8 and not cf)or(marker==16 and cf)
     assert b==[248 if hidden else a[0],a[1],a[2]&231,a[3]],('whole-group/priority',frame,epoch,i,a,b,cf)
    pp=F.normal(m);pal=[list(m.vram[0x3f10+i*4:0x3f14+i*4])for i in range(4)]
    assert pal[0][1:]==[55,18,15]and pal[1][1:]==([32,56,22]if cf else[26,48,39])
    assert pal[2]==native_palette[24:28]and pal[3]==native_palette[28:32],('worldP2P3',frame,epoch,pal)
    for i,r in enumerate(want):assert actual_pattern(m,r[1])==(bodypat+shotpat)[i],('finalhardwarepattern',frame,epoch,i,m.chr_latches)
    source_shot=[[r[0],r[1],r[2]&231,r[3]]for r in shot]
    original_palette=[[15,55,18,15],[15,32,56,22],[15,22,48,39],[15,32,56,22]]
    ref=pixels(source_shot,lambda i,t:shotpat[i],original_palette)
    actualshot=post[len(body):len(want)];rendered=pixels(actualshot,lambda i,t:actual_pattern(m,t),pal)
    assert rendered==(ref if cf or not loan else{}),('source colors/opaque/priority',frame,epoch,len(rendered),len(ref))
    rows.append(dict(frame=frame,epoch=epoch,loan=loan,CF_epoch=cf,parts=len(shot),body_parts=len(body),source_shot_pixels=len(ref),admitted_shot_pixels=len(rendered),software_visible_parts=sum(r[0]<240 for r in post),hardware_line_demand=maxline(post),CPU=z['CPU'],normalNMI_CPU=pp['CPU']))
  out['checks']=dict(unique_actual_source_frames=len(by),paired_complete_Draws=len(rows),exact_source_patterns_after_actual_normalNMI=True,source_pixel_palette_priority_and_whole_groups=True,native_worldP2P3_unchanged=True,normal_hardware_limit=8,maximum_line_demand=max(r['hardware_line_demand']for r in rows),overloaded_finite_cases=[r for r in rows if r['hardware_line_demand']>8],rows=rows)
  out['passed']=True
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),Path(F.__file__),V.P/'source-stage.json',V.P/'joint/candidate.nes',BM and BODY/'packing.json',BODY/'atlas.chr',SHOT/'packing.json',SHOT/'atlas.chr',R/'build/contra-force-p1-native-first-controls-v3/controls.json']
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],error=out.get('error'),summary={k:v for k,v in out['checks'].items()if k not in['rows','overloaded_finite_cases']})),flush=True)
if __name__=='__main__':main()
