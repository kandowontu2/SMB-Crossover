"""Original SMB attribute/palette authentication and actual render/data controls."""
from pathlib import Path
import hashlib,itertools,json
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
from cv3_life_gain_controls_v1 import fresh,run,regs,live,bus,clone,BASE
import current_kirby_meta_earned_cpu_v1 as earned
R=Path(__file__).resolve().parents[2];B=R/'build';P=B/'cv3_life_gain_watch.nes';N=B/'kirby_world_icon_palette.nes';NEW='3d597ffaf0409ff7b611c968e31818d276eda5e01ae647a3ba6234b9f88d1130';OLD='bdf9ca2bfe69ee93ca85f1b5e5319e474d9f01aa641c79a58cd9bd602253c40e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arena(b,copy=0,shot=0,offset=4,rotation=0,face=1,area=1):
 q=Arena(b,13);q.put(KbVariant=0,KbCopy=copy,KbHealth=6,Player_PageLoc=0,Player_X_Position=112,Player_Y_Position=176,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,CurrentOAMOffset=offset,GuestOamRotationActive=int(rotation!=0),RgOamRotation=rotation,SmChrBank=0,AreaType=area,PlayerFacingDir=face)
 if shot:q.set('KbShotType',3,0);q.set('KbShotKind',shot,0);q.set('KbShotX',176,0);q.set('KbShotY',160,0)
 return q
def main():
 assert sha(P)==OLD and sha(N)==NEW;old,new=scoped_load(P),scoped_load(N);out=B/'kirby_world_icon_palette_controls.json';assert not out.exists()
 original=Path('C:/NES/Super Mario Bros. (World).nes');raw=original.read_bytes();assert sha(original)=='0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea'
 table=bytes.fromhex('01020302010103030301010202210102010102ff02');hits=[i for i in range(16,32784-len(table))if raw[i:i+len(table)]==table];assert hits==[26731];pc=0x8000+hits[0]-16
 reader=bytes([0xb9,pc&255,pc>>8,5,4,0x85,4]);refs=[i for i in range(16,32784-len(reader))if raw[i:i+len(reader)]==reader];assert refs==[26931]and refs[0]-16+0x8000==0xe923
 original_cases=[]
 for enemy,extra in itertools.product([0,10,14,16],[0,32,64,128,224]):
  memory=[0]*65536;memory[0x8000:]=raw[16:32784];memory[4]=extra;c=NesMPU(memory=memory,pc=0xe923);c.y=enemy
  for _ in range(3):c.step()
  assert c.pc==0xe92a and memory[4]==extra|1
  original_cases.append(dict(enemy=enemy,entry_attributes=extra,actual_original_attributes=memory[4]))
 palettes=[]
 for area,name in enumerate(['WaterPaletteData','GroundPaletteData','UndergroundPaletteData','CastlePaletteData']):
  at=location(new,name);packet=new['raw'][at:at+36];hs=[i for i in range(16,32784-len(packet)+1)if raw[i:i+len(packet)]==packet];assert len(hs)==1
  palettes.append(dict(area=area,source=name,original_file_offset=hs[0],packet_sha256=hashlib.sha256(packet).hexdigest(),sprite_palette1=list(packet[24:27]),whole_packet_original_exact=True))
 world=[]
 for enemy in[0,10,14,16]:
  q=Arena(new,0);q.put(ObjectOffset=0,FrameCounter=0,TimerControl=0,Enemy_OffscreenBits=0);q.set('Enemy_ID',enemy);q.set('Enemy_State',4 if enemy==0 else 0);q.set('Enemy_Flag',1);q.invoke('EnemyGraphicsEngine',x=0)
  assert q.get('Enemy_SprAttrib')&3==1
  world.append(dict(enemy=enemy,actual_compiled_attribute=q.get('Enemy_SprAttrib'),metasprite=q.get('EnemyMetasprite')))
 renders=[]
 for copy,shot,offset,rot,face,area in itertools.product(range(15),[0,2,3],[4,220,244],[0,32],[1,2],range(4)):
  # A compact representative cross-product retains every copy/shot path,
  # near-full rejection, rotation and all source environment palettes.
  if (copy*3+shot+offset+rot+face+area)%11 and not(copy in[2,7,9]and shot==0 and offset==4 and rot==0):continue
  qs=[arena(b,copy,shot,offset,rot,face,area)for b in[old,new]];cs=[run(q,'KbDrawShots')[0]for q in qs]
  assert regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks and cs[0].processorCycles==cs[1].processorCycles
  delta=[i for i in range(0x8000)if qs[0].m[i]!=qs[1].m[i]]
  # No code/helper/caller state changes: only emitted OAM palette bits.
  assert all(512<=i<768 and(i-512)%4==2 and qs[0].m[i]&3==0 and qs[1].m[i]==(qs[0].m[i]&252)|1 for i in delta),(copy,shot,delta[:12])
  assert len(qs[0].m.writes)==len(qs[1].m.writes)
  for (a,x),(b,y)in zip(qs[0].m.writes,qs[1].m.writes):assert a==b and(x==y or 512<=a<768 and(a-512)%4==2 and y==(x&252)|1)
  if copy not in[2,7,9]and shot!=2:assert not delta
  if copy in[2,7,9]and offset==4 and rot==0 and shot==0:assert len(delta)==(4 if copy==9 else 2)
  renders.append(dict(copy=copy,shot=shot,OAMoffset=offset,rotation=rot,face=face,area=area,cycles=cs[1].processorCycles,changed_emitted_attributes=len(delta)))
 full=[]
 for identity,mode in itertools.product(BASE,[0,1]):
  qs=[fresh(b,identity,mode)for b in[old,new]];cs=[run(q,'GameLoop')[0]for q in qs];assert regs(cs[0])==regs(cs[1])and live(qs[0])==live(qs[1])and bus(qs[0])==bus(qs[1])and cs[0].processorCycles==cs[1].processorCycles
  full.append(dict(identity=identity,mode=mode,full_live_state_banks_SMC_registers_bus_cycles_exact=True))
 q=arena(new,2,2);image=list(q.m);banks=q.m.banks[:];a=clone(new,image,banks);c,trace=run(a,'KbDrawShots',record=True);lo=address(new,'KbDrawShots');hi=lo+int(new['syms']['KbDrawShots']['size'],0);k=(location(new,'KbDrawShots')-16)//8192;keys=sorted({z for z in trace if z[1]==k and lo<=z[0]<hi});irqs=[]
 for key in keys:
  t=clone(new,image,banks);d,_=run(t,'KbDrawShots',inject=key);assert regs(d)==regs(c)and live(t,irq=True)==live(a,irq=True)and bus(t)==bus(a)
  io=[(at,v)for i,(at,v)in enumerate(t.m.writes)if i in t.m.irq_indices and at>=8192];assert io==[(0x2006,(t.get('IrqPPUCTRL')&1)<<2),(0x5128,0),(0x2005,32),(0x2005,t.get('IrqNewScroll')),(0x2006,128|(t.get('IrqNewScroll')>>3))];irqs.append(dict(pc=key[0],bank=key[1],extra_cycles=d.processorCycles-c.processorCycles))
 # Existing genuine inhale/Down/use/discard mechanisms, bounded to affected3.
 plan=[dict(name=earned.FAMILIES[i-1][1],kind='copy',family=i,enemy=address(new,earned.FAMILIES[i-1][0]),limit=430,image=True)for i in[2,7,9]]
 original_plans,expected=earned.plans,earned.EXPECTED
 try:
  earned.plans=lambda unit,b:plan;earned.EXPECTED=NEW;acquired=earned.campaign(new,'copies-low')
 finally:earned.plans=original_plans;earned.EXPECTED=expected
 assert acquired['passed']and acquired['plan']==plan
 z=dict(passed=True,native_run=False,source_CPU_only=True,parent_sha256=OLD,candidate_sha256=NEW,original_SMB=dict(path=str(original),sha256=sha(original),enemy_attribute_table_cpu='E85B',attribute_reader_cpu='E923',reader_bytes=list(reader),actual_original_reader_cases=original_cases,area_palettes=palettes),current_compiled_world_attributes=world,render_cases=renders,ordinary_full_GameLoops=full,actual_IRQ_cases=irqs,acquired_three_families=acquired,shape_CHR_tiles_offsets_flip_priority_unchanged=True,new_RAM=0,code_or_timing_delta=0,limits='Finite assembled source CPU only. Original seven-byte attribute reader and complete palette packets authenticated locally; no original whole-game execution claim. No candidate native/PPU/timing/cadence/audio/pixel verification yet. GreyCheep uses native area palette1: gray underwater, green ground; no arbitrary fixed gray recoloring.',bindings={str(p):sha(p)for p in[Path(__file__),P,P.with_suffix('.dbg'),N,N.with_suffix('.dbg'),B/'kirby_world_icon_palette_build.json',original,R/'src/kirby_copy_icons.inc',R/'src/kirby_draw.s',R/'src/kirby_core.s',R/'src/sprite_render.s',R/'src/metasprite.s',R/'src/reset.s',R/'inc/constants.inc',R/'tools/audit/current_kirby_meta_earned_cpu_v1.py']})
 out.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(dict(passed=True,path=str(out),sha256=sha(out),renders=len(renders),full_calls=len(full),IRQ=len(irqs),earned_calls=acquired['GameLoop_calls'])))
if __name__=='__main__':main()
