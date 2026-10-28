"""Bounded real cold portrait, native backdrop and caller controls; no native run."""
from pathlib import Path
import argparse,difflib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from celeste_host_controls_v4 import *
from proto_palette_coalesce_controls_v1 import ppu

def consume(q):
 ptr=address(q.b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8)
 q.m.page(2,(location(q.b,'FastNmiVramCopy')-16)//8192)
 c,w,_=run(q,'UpdateScreen');image,bus=ppu(w)
 return dict(CPU=c.processorCycles,image=image,bus=bus)
def packet(q):return bytes(q.get('VRAM_Buffer1',i)for i in range(q.get('VRAM_Buffer1_Offset')+1))
def pos(b,n):
 s=b['syms'][n]
 if 'seg'not in s:return int(s.get('val','0'),0)
 g=b['segs'][s['seg']]
 if 'ooffs'not in g:return int(s.get('val','0'),0)
 return[(int(g['ooffs'],0)-16)//8192,int(s.get('val','0'),0)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 old,b=[scoped_load(z)for z in[a.baseline,a.rom]]
 files=[Path(__file__),R/'tools/audit/celeste_host_controls_v4.py',R/'tools/audit/sunny_integrated_controls_v1.py',R/'tools/audit/proto_palette_coalesce_controls_v1.py',a.baseline,a.baseline.with_suffix('.dbg'),a.rom,a.rom.with_suffix('.dbg'),R/'tools/prepare_celeste_host_visual_v2.py',R/'build/celeste-host-visual-v2-overlay/src/celeste_mario_host.s',R/'build/celeste-host-visual-v2-overlay/src/x5_menu_ui.s']
 proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={},bindings={str(z):sha(z)for z in files});ck=proof['checks']
 try:
  raw0,raw=old['raw'],b['raw'];assert raw[16+1048576:]==raw0[16+1048576:]
  delta={bank:[i for i in range(8192)if raw[16+bank*8192+i]!=raw0[16+bank*8192+i]]for bank in range(128)};delta={k:v for k,v in delta.items()if v};assert set(delta)=={81,99},delta.keys()
  assert all(i>=0x1b10 for i in delta[81]);assert len(delta[99])<=3
  missing=[]
  for n in old['syms']:
   if n=='_FARCALL_COUNT':continue # compile-time macro counter, not RAM/code
   if n not in b['syms']:missing.append(n);continue
   assert pos(old,n)==pos(b,n),('old symbol moved',n,pos(old,n),pos(b,n))
  assert all(n.startswith('Unnamed')or'::__'in n for n in missing),missing
  ck['layout']=dict(passed=True,changed_bytes_by_bank={k:len(v)for k,v in delta.items()},all_old_named_entries_and_RAM_preserved=True,compile_time_farcall_count=[pos(old,'_FARCALL_COUNT'),pos(b,'_FARCALL_COUNT')],removed_debug_labels=missing,CHR_exact=True,host_end=pos(b,'CmHostAreaColors::Body'))
  assets=json.loads((R/'chr/characters/celeste-mario-assets.json').read_text());records={(z['pose'],z['face']):z['parts']for z in assets['records']};rows=[]
  for mode,tier,flags in itertools.product([0,1],range(3),[0x30,0x31,0x70,0x71]):
   q=cmseed(b,tier);q.put(OperMode=mode,CrossoverMenuIndex=0,Player_SprAttrib=0,Player_State=1,CmState=1,CrouchingFlag=1,Player_X_Speed=16,Left_Right_Buttons=1)
   if mode==0:c,_,_=run(q,'DrawSelectionPreview',a=87,x=29,y=0,p=flags)
   else:
    run(q,'DrawPlayer_Intermediate');c,_,_=run(q,'X5PortraitRender',a=87,x=q.get('ObjectMetasprite'),y=0,p=flags)
   parts=records[25,1];px,py=q.get('Player_X_Position'),q.get('Player_Y_Position');want=bytes(v for tile,atr,yy,xx in reversed(parts)for v in[(py+yy)&255,tile,atr,(px+xx)&255])
   assert bytes(q.m[0x200:0x210])==want,(mode,tier,flags,list(q.m[0x200:0x210]),list(want))
   assert q.get('CurrentOAMOffset')==16 and q.get('ObjectMetasprite')==233 and q.get('CmPose')==25 and q.m.banks[2]==98
   assert q.get('CmState')==1 and q.get('CrouchingFlag')==1 and q.get('Player_X_Speed')==16
   assert[q.get('X5ChrMode',i)for i in range(4)]==[130]*4
   assert[q.get('CurrentCHRBank',i)for i in range(4)]==[230,231,232,233]
   rows.append(dict(mode=mode,tier=tier,flags=flags,OAM=list(q.m[0x200:0x210]),CPU=c.processorCycles,pose=25,Cbank=98))
  ck['real_menu_lives_portraits']=dict(passed=True,cases=len(rows),rows=rows,authenticated_four_8x16_parts=True,active_physics_state_not_rewritten=True)
  # Other actual portraits and full gameplay are unchanged, including full
  # CPU return state. Only cold routing adds cost; hot route bytes are exact.
  rows=[]
  for char,key,var in[(0,'MarioVariant',0),(8,'MarioVariant',1),(1,'ProtoVariant',0),(1,'ProtoVariant',1),(2,'MarioVariant',0),(3,'BillVariant',0),(4,'Z2Variant',1),(5,'Cv3Variant',3),(9,'RlVariant',1),(10,'MarioVariant',0),(11,'MarioVariant',0),(12,'DarkwingVariant',1),(13,'KbVariant',1),(14,'CdVariant',1),(15,'MacVariant',0),(15,'MacVariant',1),(15,'MacVariant',2),(16,'MarioVariant',0),(17,'M3Variant',1),(18,'VvVariant',3),(19,'TnVariant',3),(20,'IcVariant',1),(21,'RcVariant',1),(23,'MarioVariant',0)]:
   for mode in[0,1]:
    pairs=[]
    for bundle in[old,b]:
     q=seed(bundle,char);q.set(key,var);q.put(OperMode=mode,CurrentOAMOffset=0)
     run(q,'DrawPlayer_Intermediate');c,w,_=run(q,'X5PortraitRender',a=87,x=q.get('ObjectMetasprite'),y=0,p=0x71)
     pairs.append((registers(c),app(q),q.m.banks,cleanwrites(q,w),c.processorCycles))
    assert pairs[0][:4]==pairs[1][:4],('foreign portrait',char,key,var,mode,pairs[0][0],pairs[1][0])
    rows.append(dict(char=char,variant=var,mode=mode,CPU_delta=pairs[1][4]-pairs[0][4]))
  ck['foreign_portraits']=dict(passed=True,cases=len(rows),full_AXYP_SP_appRAM_ordered_writes_banks=True,rows=rows)
  colors=[0x22,0x22,15,15,15,0x22,15,15];rows=[]
  for area,ctrl in itertools.product(range(4),range(8)):
   qs=[cmseed(bundle,2)for bundle in[old,b]]
   for q in qs:q.put(AreaType=area,BackgroundColorCtrl=ctrl,VRAM_Buffer1_Offset=0)
   cs=[run(q,'GetPlayerColors')[0]for q in qs];packets=[packet(q).hex()for q in qs];outputs=[consume(q)for q in qs]
   expected=colors[ctrl or area]
   assert 0x3f00 not in outputs[0]['image'] and outputs[1]['image'][0x3f00]==expected
   assert {k:v for k,v in outputs[1]['image'].items()if k!=0x3f00}==outputs[0]['image']
   assert [q.get('AreaType')for q in qs]==[area,area] and[q.get('BackgroundColorCtrl')for q in qs]==[ctrl,ctrl]
   assert outputs[1]['bus'][0]==(0x3f00,expected) and outputs[1]['bus'][1:]==outputs[0]['bus']
   rows.append(dict(AreaType=area,BackgroundColorCtrl=ctrl,expected_backdrop=expected,queue_before=packets[0],queue_after=packets[1],producer_delta=cs[1].processorCycles-cs[0].processorCycles,consumer_delta=outputs[1]['CPU']-outputs[0]['CPU']))
  ck['native_GetColors_UpdateScreen']=dict(passed=True,cases=len(rows),rows=rows,old_missing_universal_background_counterexample=True,existing_native_background_table=True)
  bounds=[]
  for offset,flags in itertools.product(range(84),range(0x20,0x60)):
   q=cmseed(b,1);q.put(VRAM_Buffer1_Offset=offset,BackgroundColorCtrl=0);base=address(b,'VRAM_Buffer1');q.m[base:base+88]=bytes([0x99]*88);q.m[base+offset]=0
   c,w,_=run(q,'GetPlayerColors',a=87,x=23,y=17,p=flags);end=q.get('VRAM_Buffer1_Offset')
   wanted=offset+10 if offset<=73 else offset+4 if offset<=79 else offset
   assert end==wanted and end<=83 and q.m[base+end]==0,(offset,flags,end,wanted)
   assert bytes(q.m[base+84:base+88])==bytes([0x99]*4)
   if flags==0x20:bounds.append(dict(offset=offset,end=end,backdrop_appended=offset<80,body_palette_appended=offset<=73,CPU=c.processorCycles))
  ck['queue_bounds_all_entry_flags']=dict(passed=True,cases=84*64,actual_capacity=84,all_canaries_exact=True,rows=bounds,deferral='Offset80..83 defers backdrop; offset74..83 defers body palette. CmColors leaves palette cache dirty, so later UI can retry.')
  rows=[]
  for char,var in[(0,0),(0,1),(1,1),(2,0),(3,0),(5,3),(15,2),(18,3),(19,3),(23,0),(0,4)]:
   for mode in[0,1]:
    pairs=[]
    for bundle in[old,b]:
     q=cmseed(bundle,2)if char==0 and var==4 else seed(bundle,char)
     if var!=4:q.set('MarioVariant',var)
     q.put(CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1)
     c,w,_=run(q,'GameLoop',p=0x71);pairs.append((registers(c),app(q),q.m.banks,cleanwrites(q,w),c.processorCycles))
    assert pairs[0]==pairs[1],('hot fullcaller',char,var,mode)
    rows.append(dict(char=char,variant=var,mode=mode,CPU_delta=0))
  ck['hot_complete_GameLoop']=dict(passed=True,cases=len(rows),full_AXYP_SP_appRAM_writes_banks_CPU_exact=True,rows=rows)
  irq=0
  for name in['CmHostPortraitRender','CmHostColors']:
   q=cmseed(b,2);q.put(CurrentOAMOffset=0,VRAM_Buffer1_Offset=0);run(q,'DrawPlayer_Intermediate');c,w,n=run(q,name,a=87,x=29,y=0,p=0x30,irq=True);irq+=n
  ck['actual_IRQ']=dict(passed=True,injections=irq,scope='Inherited real-vector enabled-boundary checks in bank81/fixed paths; unchanged record/core paths retain separate frozen controls. No native timing/visible-pixel claim.')
  for p,h in proof['bindings'].items():assert sha(p)==h
  proof['passed']=True
 except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:a.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=True,sha256=sha(a.output),checks=list(ck))))
if __name__=='__main__':main()
