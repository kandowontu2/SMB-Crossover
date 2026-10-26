"""Execute final-packet HUD deferral and compare original native producer I/O."""
from pathlib import Path
import argparse,hashlib,itertools,json,shutil
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_nmi_vram_fast_cpu_v1 import Bus,run
from check_tmnt_render_oa import address
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Ports(Bus):
 def __init__(self,b):
  super().__init__(b);self.w=0;self.vram=0;self.inc=1;self.data=[];self.events=[]
 def __getitem__(self,at):
  if at==0x2002:self.w=0;self.events.append(('read',at))
  if at==0x2007:self.events.append(('read',at));self.vram=(self.vram+self.inc)&0x3fff
  return super().__getitem__(at)
 def __setitem__(self,at,v):
  if isinstance(at,int)and 0x2000<=at<=0x2007:
   self.events.append(('write',at,v))
   if at==0x2000:self.inc=32 if v&4 else 1
   if at==0x2005:self.w^=1
   if at==0x2006:
    self.vram=((v&63)<<8)|(self.vram&255)if not self.w else(self.vram&0x3f00)|v;self.w^=1
   if at==0x2007:self.data.append((self.vram,v));self.vram=(self.vram+self.inc)&0x3fff
  return super().__setitem__(at,v)
def literal(length,seed=0):
 return [0x21,(seed*7)&255,length]+[(seed+i*13)&255 for i in range(length)]if length else[]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);shutil.copy2(Path(__file__),a.output/Path(__file__).name);b=scoped_load(a.candidate);old=scoped_load(a.base/'nmi-fast-candidate-v1/candidate.nes');rows=[];failure=None
 def invoke(bundle,packet,variant,upper,active,physical,dirty,flags,ctrl=0,pointer=None,capture=0,engine=8,disabled=0):
  m=Ports(bundle);m.page(2,88);base=address(bundle,'VRAM_Buffer1');ptr=base if pointer is None else pointer;m.palette=[(i*17+3)&63 for i in range(32)]
  values=dict(SelectedCharacter=18,CrossoverBehaviorVersion=1,OperMode=1,OperMode_Task=3,GameEngineSubroutine=engine,DisableScreenFlag=disabled,PnInitialized=0x50,VvVariant=variant,PnBombCapturePending=capture,PnBombPaletteReady=1-capture,SmFreezePalettePending=0,CurrentBankC=216,Mirror_PPUCTRL=0xa0,NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer1_Offset=len(packet)-1,VRAM_Buffer_AddrCtrl=ctrl,X5HudChrUpper=upper,InvHudPhysical=physical,InvHudActive=active,ReloadCHRBank=0,VvHudDirty=dirty)
  for n,v in values.items():m.put(address(bundle,n),v)
  for i,v in enumerate(packet):m.put(base+i,v)
  m.put(0x2002,0x80);m.put(0x1fe,0xff);m.put(0x1ff,0x01)
  r=run(bundle,m,address(bundle,'SamusFreezeUpdateScreen'),0x0200,0x55,37,193,flags)
  return r,m
 def foreground(variant,meter,prefix,full):
  q=Arena(b,18);q.put(DisableScreenFlag=0,VvVariant=variant,VvMeter=meter,VvHudDirty=1,InvHudActive=0 if full else 2*variant+1,X5HudChrUpper=1,VRAM_Buffer1_Offset=len(prefix),ReloadCHRBank=0,PnInitialized=0x50,PnBombPaletteReady=1);q.array('VRAM_Buffer1',[0]*84);q.array('VRAM_Buffer1',prefix+[0]);q.invoke('PnHud');packet=[q.get('VRAM_Buffer1',i)for i in range(q.get('VRAM_Buffer1_Offset'))];return packet,{n:q.get(n)for n in ['InvHudActive','InvHudPhysical','X5HudChrUpper','VvHudDirty']}
 def check(kind,variant,meter,prefix,suffix,full,dirty,flags,engine=8,disabled=0):
  packet,lease=foreground(variant,meter,prefix,full);hud=42 if full else 11;assert len(packet)==len(prefix)+hud
  admitted=not suffix and engine==8 and not disabled if full else len(packet)+len(suffix)<=31
  whole=packet+suffix+[0];assert len(whole)<=84
  desired=whole if admitted else prefix+suffix+[0]
  original,om=invoke(old,whole,variant,1,1,139+variant,dirty,flags,engine=engine,disabled=disabled)
  reference,rm=invoke(old,desired,variant,1,1,139+variant,dirty,flags,engine=engine,disabled=disabled)
  after,m=invoke(b,whole,variant,lease['X5HudChrUpper'],lease['InvHudActive'],lease['InvHudPhysical'],dirty,flags,engine=engine,disabled=disabled)
  assert m.data==rm.data,('ordered native PPUDATA',kind,variant,meter,len(prefix),len(suffix),m.data,rm.data)
  assert after['state']==original['state'],('native AXYP/SP',kind,variant,meter,len(prefix),len(suffix),flags,after['state'],original['state'])
  assert after['banks']==original['banks']and after['reads']==original['reads']
  assert [m[base]for base in range(address(b,'VRAM_Buffer1'),address(b,'VRAM_Buffer1')+len(whole))]==whole,'Temporary prefix terminator restored exactly'
  assert m[address(b,'NmiR0')]+256*m[address(b,'NmiR1')]==address(b,'VRAM_Buffer1')+len(whole)-1
  assert m[address(b,'InvHudActive')]==(2*variant+1 if not full or admitted else 0)
  assert m[address(b,'InvHudPhysical')]==(139+variant if not full or admitted else 0)
  assert m[address(b,'X5HudChrUpper')]==1
  assert m[address(b,'VvHudDirty')]==(dirty if admitted else 1),'Later foreground Dirty cannot be erased by success'
  assert m[address(b,'ReloadCHRBank')]==int(full and admitted)
  # No pre-helper uses private foreground scratch or extra application RAM.
  allowed={address(b,n)for n in ['InvHudActive','InvHudPhysical','X5HudChrUpper','VvHudDirty','ReloadCHRBank','NmiR0','NmiR1']}
  before_ram={i:om[i]for i in list(range(256))+list(range(0x200,0x800))+list(range(0x5c00,0x8000))};diff=[i for i,v in before_ram.items()if m[i]!=v and i not in allowed];assert not diff,('unexpected application RAM',diff[:10])
  rows.append(dict(kind=kind,variant=variant,meter=meter,prefix_bytes=len(prefix),suffix_bytes=len(suffix),whole_bytes=len(whole)-1,admitted=admitted,live_dirty=dirty,flags=flags,gateway_cycles=after['cycles'],native_data_writes=len(m.data),extra_scroll_writes=sum(at==0x2005 for at,v in after['writes'])-sum(at==0x2005 for at,v in reference['writes'])))
 try:
  # Actual recorded heavy prefix, plus bounded legal literal producer shapes.
  genuine=json.loads((a.base/'broad-budget-v1/genuine-failing-packets.json').read_text());heavy=next(q for q in genuine if q['profile']=='octopus-hard')['source_packet']['bytes'][:31]
  suffixes=[[],literal(1),literal(2),[0x3f,0x0c,4,15,39,23,15],literal(20),literal(32)]
  for variant,meter,suffix,dirty,flags in itertools.product([1,2,3],[0,1,0x55,0xaa,255],suffixes,[0,1],[0x30,0x75,0xff]):check('first_full_final_extent',variant,meter,[],suffix,True,dirty,flags)
  prefixes=[[],literal(1),literal(2),[0x3f,0x0c,4,15,39,23,15],literal(7),literal(17),literal(28),heavy]
  for variant,meter,prefix,suffix,dirty,flags in itertools.product([1,2,3],[0,1,0x55,0xaa,255],prefixes,suffixes,[0,1],[0x30,0x75,0xff]):
   if len(prefix)+11+len(suffix)>83:continue
   check('attributes_final_extent',variant,meter,prefix,suffix,False,dirty,flags)
  for variant,engine,disabled,dirty in itertools.product([1,2,3],[6,8],[0,1],[0,1]):check('first_full_owner_change',variant,0,[],[],True,dirty,0x75,engine=engine,disabled=disabled)
 except Exception as e:
  failure=dict(passed=False,error=repr(e),completed_cases=len(rows),ROM_sha256=sha(a.candidate),tool_sha256=sha(Path(__file__)));(a.output/'failure.json').write_text(json.dumps(failure,indent=2)+'\n',encoding='utf-8');raise
 (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n',encoding='utf-8');q=dict(passed=True,native_run=False,goal_complete=False,ROM_sha256=sha(a.candidate),tool_sha256=sha(Path(__file__)),cases=len(rows),cases_sha256=sha(a.output/'cases.json'),ordered_non_HUD_PPUDATA_exact=True,queue_bytes_restored=True,final_pointer_exact=True,native_AXYP_SP_exact=True,later_live_Dirty_preserved=True,limits='Actual assembled CPU foreground/gateway with isolated packet/resource setup. First-full and attribute deferrals intentionally change HUD publication timing. Prefix split adds two scroll writes and an extra status-read boundary versus a compacted native-only packet; all occur inside the native display-off gateway. No native render, DMA, physical IRQ/DMC, starvation or60Hz claim.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q,indent=2))
if __name__=='__main__':main()
