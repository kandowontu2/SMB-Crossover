"""Small Celeste CHR owner repair: source CPU, real native mixed glyphs, no native."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from celeste_host_controls_v4 import *
from celeste_small_controls_v5 import irq
from celeste_mac_union_controls_v1 import full

def publish(q):
 c,w,_=run(q,'X5PublishChr');upper=0;pages={}
 for at,v in w:
  if at==0x5130:upper=v&3
  if 0x5120<=at<=0x512b:pages[at-0x5120]=v+(upper<<8)
 assert len(pages)==12
 return pages,w

def setup(b,tier=0,area=1,outline=0):
 q=cmseed(b,tier);run(q,'X5ColdInit');run(q,'GetAreaType',a=area<<5);q.put(CmTier=tier,PlayerStatus=tier,PlayerOutlinesOff=outline,Player_Y_Position=160,Player_Rel_YPos=160,CurrentOAMOffset=0);return q

def bitmap(q,pages,start,end):
 out=bytearray();raw=q.b['raw'];base=1048592
 for i in range(start,end,4):
  tile=q.m[0x201+i];attr=q.m[0x202+i];window=((tile&1)*4096+(tile&254)*16)//1024;page=pages[window];local=((tile&254)*16)%1024
  for yy in range(16):
   y=15-yy if attr&128 else yy;at=base+page*1024+local+(y//8)*16+y%8
   for xx in range(8):
    bit=xx if attr&64 else 7-xx;out.append((raw[at]>>bit&1)|((raw[at+8]>>bit&1)<<1))
 return hashlib.sha256(out).hexdigest()

def native_mix(q):
 start=q.get('CurrentOAMOffset');q.put(R3=0,ObjectOffset=0);q.set('Enemy_MovingDir',1,0);q.set('Enemy_X_Position',160,0);q.set('Enemy_PageLoc',1,0);q.set('Enemy_Y_Position',160,0);q.set('Enemy_Y_HighPos',1,0);run(q,'DrawMetasprite',x=address(q.b,'METASPRITE_GOOMBA_WALKING_1'),y=1);mid=q.get('CurrentOAMOffset')
 q.set('FloateyNum_Control',1,0);q.set('FloateyNum_X_Pos',192,0);q.set('FloateyNum_Y_Pos',128,0);run(q,'FloateyNumberRender',x=0);end=q.get('CurrentOAMOffset');return start,mid,end

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
 paths=[R/'build/celeste-small-v1.nes',R/'build/celeste-small-chr-v2.nes'];old,b=[scoped_load(p)for p in paths]
 files=[Path(__file__),R/'tools/prepare_celeste_small_chr_v1.py',R/'tools/prepare_celeste_small_chr_v2.py',R/'tools/audit/celeste_small_controls_v5.py',R/'tools/audit/celeste_host_controls_v4.py',R/'tools/audit/sunny_integrated_controls_v1.py',R/'src/mmc5.s',R/'src/mmc5_expanded.s',R/'src/metasprite_engine.s',R/'src/native_goomba_draw.s',R/'src/celeste_mario_art.inc',R/'chr/characters/celeste-mario.chr',R/'chr/characters/celeste-mario-assets.json',R/'build/celeste_small_handoff_v1.json']+[p.with_suffix(ext)for p in paths for ext in['.nes','.dbg','.lbl']]+list((R/'build/celeste-small-chr-v2-overlay/src').glob('*'))
 proof=dict(passed=False,source_CPU_only=True,native_run=False,bindings={str(p.resolve()):sha(p)for p in files},checks={});ck=proof['checks']
 try:
  ds={k:sum(x!=y for x,y in zip(old['raw'][16+k*8192:16+(k+1)*8192],b['raw'][16+k*8192:16+(k+1)*8192]))for k in range(128)};ds={k:v for k,v in ds.items()if v};assert set(ds)=={98}and old['raw'][1048592:]==b['raw'][1048592:]
  for n,z in old['syms'].items():
   if n=='_FARCALL_COUNT':continue
   assert n in b['syms']and address(old,n)==address(b,n),('old label',n)
  assert address(b,'CmSmallChrStart')==0xbdfa and address(b,'CmSmallChrEnd')==0xbe0b
  ck['layout']=dict(passed=True,changed_bytes_by_bank=ds,helper_span=[0xbdfa,0xbe0b],all_old_PC_RAM_CHR_exact=True)
  meta=json.loads((R/'chr/characters/celeste-mario-assets.json').read_text());rr=[r for r in meta['records']if 12<=r['pose']<=23]
  assert len(rr)==24;tiles=[p[0]for r in rr for p in r['parts']];assert max(tiles)==50 and all(t%2==0 and t+1<64 for t in tiles)
  ck['source_window_closure']=dict(passed=True,records=24,poses=list(range(12,24)),both_faces=True,max_tile=50,max_pair_tile=51,all_use_window0=True,outline='X5PlayerOutlineFlag is0 for raw0; native records contain only source color classes, no appended mask. Both outline settings run actual mixed callers below.')
  allowed=[address(b,'CurrentCHRBank')+i for i in[1,2,3]]+[address(b,'X5ChrMode')+i for i in[1,2,3]]+[address(b,'ReloadCHRBank')]
  costs=[];n=0
  for bank,flags,shape in itertools.product([1,2,252,255],[p for p in range(256)if p&0x30==0x30],['native','already','direct']):
   outs=[]
   for bundle in[old,b]:
    q=setup(bundle);q.put(CmGfxBank=bank,ReloadCHRBank=0)
    if shape=='already':
     for i in range(4):q.set('CurrentCHRBank',(bank+228+i)&255,i);q.set('X5ChrMode',130,i)
    if shape=='direct':
     for i in range(1,4):q.set('CurrentCHRBank',37+i,i);q.set('X5ChrMode',129,i)
    before=[(q.get('CurrentCHRBank',i),q.get('X5ChrMode',i))for i in range(1,12)]
    c,w,_=run(q,'CmDraw',a=87,x=177,y=91,p=flags)
    assert c.y==4 and q.get('CmTemp')==(bank+228+4)&255
    if bundle is b:assert before==[(q.get('CurrentCHRBank',i),q.get('X5ChrMode',i))for i in range(1,12)]
    outs.append((registers(c),app(q,skip=allowed),q.m.banks,bytes(q.m[z]for z in smc_at(bundle)),[(at,v)for at,v in cleanwrites(q,w)if at not in allowed],c.processorCycles))
   assert outs[0][:5]==outs[1][:5],('leaf full ABI/otherRAM',bank,flags,shape,outs[0][0],outs[1][0]);costs.append(outs[1][5]-outs[0][5]);n+=1
  ck['leaf_full_ABI']=dict(passed=True,cases=n,all64_flags=True,AXYP_SP_CmTemp_banks_5SMC_all_other_appRAM_and_ordered_writes=True,explicit_intentional_fields=allowed,CPU_delta=[min(costs),max(costs)],CmTemp_modulo_wrap=True)
  rows=[]
  for area,outline,tier,pose,face in itertools.product(range(4),[0,1],range(3),[12,16,17,20,22,23],[1,2]):
   parent=setup(old,tier,area,outline);nativepages,_=publish(parent);n0,n1,n2=native_mix(parent);expected=[bitmap(parent,nativepages,n0,n1),bitmap(parent,nativepages,n1,n2)]
   q=setup(b,tier,area,outline);q.put(PlayerFacingDir=face);run(q,'CmGraphics::Select',x=pose);run(q,'CmDraw');run(q,'HpPrepareNativePointers');run(q,'DrawMetasprite',x=233);bodyend=q.get('CurrentOAMOffset');assert bodyend==8
   n0,n1,n2=native_mix(q);pages,w=publish(q);assert all(pages[i]==nativepages[i]for i in range(1,12)) and pages[0]==740+q.get('CmGfxBank')
   actual=[bitmap(q,pages,n0,n1),bitmap(q,pages,n1,n2)];assert actual==expected,('native glyph classes',area,outline,tier,pose,face)
   # Demonstrate the old ownership defect without changing the old result.
   bad=setup(old,tier,area,outline);bad.put(PlayerFacingDir=face);run(bad,'CmGraphics::Select',x=pose);run(bad,'CmDraw');badpages,_=publish(bad)
   rows.append(dict(area=area,outline=outline,tier=tier,pose=pose,face=face,pages=[pages[i]for i in range(4)],old_pages=[badpages[i]for i in range(4)],native_glyph_hashes=actual,body_OAM=list(q.m[0x200:0x208]),native_OAM=list(q.m[0x200+n0:0x200+n2])))
  ck['real_body_goomba_floatey_mix']=dict(passed=True,cases=len(rows),all_areas_both_outlines_tiers_faces=True,all11_nonbody_windows_native_exact=True,actual_X5PublishChr_writes_decoded_with_5130=True,body_only_window0=True,examples=rows[:4]+rows[-4:],source_color_classes_not_native_PPU=True)
  rows=[]
  for mode,area,outline,tier,keys in itertools.product([0,1],range(4),[0,1],range(3),[0,1,129]):
   outs=[]
   for bundle in[old,b]:
    q=setup(bundle,tier,area,outline);q.put(CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=keys,Left_Right_Buttons=keys&3,A_B_Buttons=keys&192)
    for name,value in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),('Enemy_X_Position',144),('Enemy_PageLoc',1),('Enemy_Y_Position',176),('Enemy_Y_HighPos',1),('Enemy_MovingDir',2),('FloateyNum_Control',1),('FloateyNum_Timer',40),('FloateyNum_X_Pos',192),('FloateyNum_Y_Pos',128)]:q.set(name,value,0)
    c,w,_=run(q,'GameLoop',p=0x71);outs.append((registers(c),app(q,skip=allowed),q.m.banks,bytes(q.m[z]for z in smc_at(bundle)),[(at,v)for at,v in cleanwrites(q,w)if at not in allowed],c.processorCycles))
   assert outs[0][:5]==outs[1][:5],('whole GameLoop ABI',mode,area,outline,tier,keys);rows.append([mode,area,outline,tier,keys,outs[1][5]-outs[0][5]])
  ck['complete_owned_GameLoop']=dict(passed=True,calls=len(rows),full_AXYP_SP_OAM_other_appRAM_ordered_writes_banks_5SMC_exact=True,only_explicit_seven_CHR_reload_fields_differ=True,CPU_delta=[min(r[-1]for r in rows),max(r[-1]for r in rows)],typed_empty_map_one_real_Goomba_plus_score=True)
  n=0
  for char,mode in itertools.product(range(24),[0,1]):
   if char==22:continue
   pair=[]
   for bundle in[old,b]:
    q=seed(bundle,char);q.put(MarioVariant=0,CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1);pair.append(full(q,p=0x71))
   assert pair[0]==pair[1],('foreign',char,mode);n+=1
  ck['foreign_complete_GameLoop']=dict(passed=True,calls=n,all_state_writes_banks_OAM_CPU_exact=True)
  # New helper: every instruction visited under real IRQ and lagNMI.
  for kind in['IRQ','NMI']:
   q=setup(b);q.put(NmiDisable=255,CmGfxBank=2);oldstep=NesMPU.step;seen=set()
   def step(c):
    if q.m.banks[1]==98 and 0xbdfa<=c.pc<0xbe0b and c.pc not in seen:
     seen.add(c.pc)
     def ss():return(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,tuple(q.m.banks),bytes(q.m[:8]),bytes(q.m[0x101+c.sp:0x200]),bytes(q.m[0x5c00:0x5ffe]),bytes(q.m[z]for z in smc_at(b)))
     before=ss()
     if kind=='NMI':c.nmi()
     else:q.m[0x5204]=128;c.irq()
     for _ in range(60000):
      oldstep(c)
      if c.pc==before[5]and c.sp==before[4]:break
     else:raise AssertionError('ISR timeout')
     assert ss()==before,('new helper ISR',kind,hex(c.pc))
    oldstep(c)
   NesMPU.step=step
   try:run(q,'CmDraw',p=0x30)
   finally:NesMPU.step=oldstep
   ck[kind+'_new_helper']=dict(passed=True,boundaries=len(seen),full_six_flags_AXY_SP_PC_live_stack_R0_R7_banks_5SMC_Celeste_state=True)
  assert all(sha(f)==h for f,h in proof['bindings'].items());proof['passed']=True
 except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
 a.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))));assert proof['passed']
if __name__=='__main__':main()
