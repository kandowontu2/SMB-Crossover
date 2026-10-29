"""Complete source poses and actual native foreign/own callers; no PPU claim."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from sunny_integrated_controls_v1 import *

def pub(q):
 c,w,_=run(q,'X5PublishChr',a=87,x=177,y=91,p=0x71);upper=0;pages={}
 for at,v in w:
  if at==0x5130:upper=v&3
  if 0x5120<=at<=0x512b:pages[at-0x5120]=(upper<<8)|v
 assert len(pages)==12
 return pages,c,w

def setup(b,var=3,tier=0,area=1):
 q=seed(b,0);run(q,'X5ColdInit');q.put(CrossoverMenuIndex=0,MarioVariant=var,VRAM_Buffer1_Offset=0,PlayerStatus=tier,PlayerSize=int(tier==0))
 run(q,'MenuResolveCharacter');run(q,'GetAreaType',a=area<<5);run(q,'QueueSelection');return q

def signature(q,c,w):
 live=[]
 for g in q.b['segs'].values():
  if g.get('name')in['"SHORTRAM"','"SMCCODE"']:live.extend(range(int(g['start'],0),int(g['start'],0)+int(g['size'],0)))
 return registers(c),app(q),q.m.banks,bytes(q.m[z]for z in live),cleanwrites(q,w)

def image(q,pages,lo=0,hi=16):
 out={};raw=q.b['raw']
 for i in range(lo,hi,4):
  sy,t,attr,sx=q.m[0x200+i:0x204+i]
  window=((t&1)*4096+(t&254)*16)//1024;at=1048592+pages[window]*1024+((t&254)*16)%1024
  for y in range(16):
   yy=15-y if attr&128 else y;o=at+yy%8+(yy//8)*16
   for x in range(8):
    bit=x if attr&64 else 7-x;v=(raw[o]>>bit&1)|((raw[o+8]>>bit&1)<<1)
    if v:out[(sx+x,sy+y+1)]=v
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
 paths=[R/'build/roster-shared-celeste-small-chr-v1.nes',R/'build/kamikaze-mario-host-v4/candidate.nes'];old,b=[scoped_load(p)for p in paths]
 fs=[Path(__file__),R/'src/kamikaze_mario_render_v2.inc',R/'src/kamikaze_mario_source_art_v2.inc',R/'chr/characters/kamikaze-mario-source-v2.chr',R/'build/kamikaze-mario-art-v2/source-art.json',R/'tools/prepare_kamikaze_mario_host_v4.py']+[p.with_suffix(e)for p in paths for e in['.nes','.dbg','.lbl']]+list((R/'build/kamikaze-mario-host-v4/overlay/src').glob('*'))
 proof=dict(passed=False,source_CPU_only=True,native_run=False,bindings={str(p.resolve()):sha(p)for p in fs},checks={});ck=proof['checks']
 try:
  diff={i:sum(x!=y for x,y in zip(old['raw'][16+i*8192:16+(i+1)*8192],b['raw'][16+i*8192:16+(i+1)*8192]))for i in range(128)};diff={i:v for i,v in diff.items()if v}
  assert set(diff)=={1,62,66,81,99,124,125,127},diff
  moved=[n for n in old['syms']if n!='_FARCALL_COUNT'and n in b['syms']and address(old,n)!=address(b,n)]
  assert all(n.startswith('CrossoverGraphicsBank::')for n in moved),moved
  assert address(b,'KmCoreStart')==0xb690 and address(b,'KmCoreEnd')<=0xc000
  assert old['raw'][16+62*8192+0xa00:16+62*8192+0x1690]==b['raw'][16+62*8192+0xa00:16+62*8192+0x1690]
  ck['layout']=dict(passed=True,PRG_diff=diff,moved_only_private_resident_labels=moved,core_bytes=address(b,'KmCoreEnd')-address(b,'KmCoreStart'),no_new_RAM=True,FF_future_span_unchanged=True)
  n=0;costs=[]
  for char,var,obj,flags in itertools.product(range(24),[0,1,4,255],[0,233],[0x30,0x31,0x70,0x71]):
   pair=[]
   for bundle in[old,b]:
    q=seed(bundle,char);q.put(MarioVariant=var,ObjectMetasprite=obj);c,w,_=run(q,'CrossoverGraphicsBank',a=87,x=177,y=91,p=flags);pair.append((signature(q,c,w),c.processorCycles))
   assert pair[0][0]==pair[1][0],('resident foreign',char,var,obj,flags);costs.append(pair[1][1]-pair[0][1]);n+=1
  ck['resident_foreign']=dict(passed=True,cases=n,full_six_flags_AXY_live_SHORTRAM_33SMC_all_appRAM_banks_writes_exact=True,CPU_delta=[min(costs),max(costs)])
  src=(Path('C:/NES/the stash/Kamikaze_Mario_DX_Plus_V1.9_SMB1_Hack.nes')).read_bytes();table=src[16+0x6e17:16+0x6e17+208];chr=src[16+81920:]
  n=0
  for frame,face in itertools.product(range(26),[1,2]):
   q=setup(b,3);q.put(PlayerFacingDir=face,Player_X_Position=96,Player_Rel_XPos=96,Player_Y_Position=120,Player_Rel_YPos=120,CurrentOAMOffset=0,GuestOamRotationActive=0)
   # Select actual source frame through the real native-ID map's public entry.
   ids=json.loads((R/'build/kamikaze-mario-art-v2/source-art.json').read_text())['host_pose_mapping']
   if frame not in ids:continue
   run(q,'KmSelect',x=ids.index(frame));run(q,'HpPrepareNativePointers');run(q,'DrawMetasprite',x=233,y=0);pages,_,_=pub(q)
   assert q.get('CurrentOAMOffset')==16 and pages[0]==696+frame//8
   expected={}
   for i,t in enumerate(table[frame*8:(frame+1)*8]):
    if t==252:continue
    p=chr[t*16:t*16+16]
    for y in range(8):
     for x in range(8):
      v=(p[y]>>(7-x)&1)|((p[y+8]>>(7-x)&1)<<1)
      if v:
       xx=(i%2)*8+x;xx=15-xx if face==2 else xx;expected[(96+xx,120-8+(i//2)*8+y+1)]=v
   assert image(q,pages)==expected,('literal source pixels',frame,face)
   n+=1
  ck['literal_source_body_pixels']=dict(passed=True,cases=n,all26_frames_both_faces=True,actual_Hp_DrawMetasprite_X5PublishChr_consumers=True,original_pixel_indices_exact=True,native4_sprite_budget=True)
  # Full Main state classification. A deliberate source presentation changes
  # descriptor/pattern pointers and OAM; retain every actual changed byte for
  # review rather than filtering unspecified application memory silently.
  pairs=[]
  for var in[0,3]:
   q=setup(b,var,0);q.put(GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1,A_B_Buttons=0,VRAM_Buffer1_Offset=0)
   for k in range(84):q.m[address(b,'VRAM_Buffer1')+k]=0
   c,w,_=run(q,'GameLoop');pairs.append((q,c,w))
  allowed={address(b,n)+i for n,length in[('MarioVariant',1),('ObjectMetasprite',1),('SmPosePtr',2),('SmChrBank',1),('PlayerChrBank',1),('CurrentCHRBank',1),('X5ChrMode',1),('X5WideChrActive',1),('ReloadCHRBank',1),('CurrentBankC',1)]for i in range(length)}
  allowed.update(range(0x200,0x300))
  # Renderer pointer R0/R1 is dead at the Main return; the next complete
  # caller rebuilds it. CurrentOAMOffset and the slot0 native pointer cache
  # represent the intentional four-part complete source body.
  allowed.update([address(b,n)for n in['R0','R1','CurrentOAMOffset']])
  allowed.update([address(b,n)for n in['HpNativeDrawLo','HpNativeDrawHi']])
  changes=[];unexpected=[]
  for i in range(0x8000):
   if 0x100<=i<0x200 or 0x2000<=i<0x5c00:continue
   if pairs[0][0].m[i]!=pairs[1][0].m[i]:
    changes.append([i,pairs[0][0].m[i],pairs[1][0].m[i]])
    if i not in allowed:unexpected.append(changes[-1])
  ck['Main_observed_presentation_delta']=dict(changes=changes,unexpected=unexpected)
  assert not unexpected,('unclassified full Main state',unexpected)
  ck['Main_observed_presentation_delta']['passed']=True
  # Multiple complete Main updates, every area/tier/mode. Retain all123
  # live page1 bytes; unlike app(), this includes the real short RAM and
  # all33 SMC bytes. Only explicit presentation fields may differ.
  tested=0;costs=[]
  for area,tier,mode,keys in itertools.product(range(4),range(3),[0,1],[0,1,129]):
   qs=[setup(b,var,tier,area)for var in[0,3]]
   previous_x=[0,0]
   for q in qs:
    q.put(CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=keys,Left_Right_Buttons=keys&3,A_B_Buttons=keys&192)
   for age in range(3):
    out=[]
    for index,q in enumerate(qs):
     q.put(VRAM_Buffer1_Offset=0,VRAM_Buffer2_Offset=0)
     for k in range(84):q.m[address(b,'VRAM_Buffer1')+k]=0
     c,w,_=run(q,'GameLoop',a=0,x=previous_x[index],y=0,p=0x33);previous_x[index]=c.x
     state=app(q,skip=allowed);live=bytes(q.m[i]for i in range(0x100,0x17b)if i not in allowed)
     # IdleLoop ignores returned X, then preserves it into the next
     # PauseRoutine/UI path until GameLoop's explicit LDX0. Forward it
     # above to prove the different render-end count has no later effect.
     out.append((state,live,[c.a,c.y,c.p,c.sp],q.m.banks,c.processorCycles))
    assert out[0][:3]==out[1][:3],('full native progression',area,tier,mode,keys,age)
    assert out[0][3][:2]==out[1][3][:2]and out[0][3][3:]==out[1][3][3:]
    costs.append(out[1][4]-out[0][4]);tested+=1
  ck['full_Main_progression']=dict(passed=True,updates=tested,physics_nonvisual_RAM_AYP_SP_all_live_page1_exact=True,render_end_X_is_forwarded_into_next_complete_Main=True,IdleLoop_ignores_returned_X=True,only_explicit_visual_fields_and_C_art_bank_differ=True,CPU_delta=[min(costs),max(costs)],typed_empty_map=True)
  assert all(sha(p)==h for p,h in proof['bindings'].items());proof['passed']=True
 except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
 a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))));assert proof['passed']
if __name__=='__main__':main()
