"""Whole linked regular-NMI instruction cost to DMA, explicit synthetic CHR states."""
from pathlib import Path
import argparse,hashlib,itertools,json,shutil
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_nmi_vram_fast_cpu_v1 import Bus
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
from parodius_visibility_hud_design_v1 import packet_without_labels
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);shutil.copy2(Path(__file__),a.output/Path(__file__).name);old=scoped_load(a.base/'nmi-fast-candidate-v1/candidate.nes');new=scoped_load(a.candidate);rows=[];genuine=json.loads((a.base/'broad-budget-v1/genuine-failing-packets.json').read_text())
 def execute(bundle,packet,variant,capture,active,pending,mode_pattern,admission_offset=0,attr_offset=None):
  m=Bus(bundle);m.page(1,77);m.page(2,88);m.palette=[(i*73+19)&63 for i in range(32)];values=dict(SelectedCharacter=18,CrossoverBehaviorVersion=1,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,DisableScreenFlag=0,PnInitialized=0x50,VvVariant=variant,PnBombCapturePending=capture,PnBombPaletteReady=1-capture,SmFreezePalettePending=0,CurrentBank=205,CurrentBankC=216,Mirror_PPUCTRL=0xa0,Mirror_PPUMASK=0x1e,VRAM_Buffer1_Offset=len(packet)-1,VRAM_Buffer_AddrCtrl=0,X5HudChrUpper=0x81+4*variant if pending else 1,InvHudPhysical=0 if pending else 139+variant,InvHudActive=active,ReloadCHRBank=1,VvHudDirty=0,NmiDisable=0,Sprite0HitDetectFlag=1,HorizontalScroll=0,X5WideChrActive=1,SsChrActive=0)
  for n,v in values.items():m.put(address(bundle,n),v)
  if pending:m.put(address(bundle,'InvHudPhysical'),admission_offset)
  if attr_offset is not None:m.put(address(bundle,'X5HudChrUpper'),0x81+attr_offset*4)
  for i,v in enumerate(packet):m.put(address(bundle,'VRAM_Buffer1')+i,v)
  for i,v in enumerate(mode_pattern):m.put(address(bundle,'X5ChrMode')+i,v);m.put(address(bundle,'CurrentCHRBank')+i,i*7&255)
  m.put(0x2002,0x80);m.writes=[];c=NesMPU(memory=m,pc=address(bundle,'NonMaskableInterrupt'));c.sp=0xfd;c.a=0x55;c.x=3;c.y=7;c.p=0x34;starts={};spans=[]
  hooks={address(bundle,n):n for n in ['SamusFreezeUpdateScreen','BankSwitchCHR']};pending_returns=[]
  for step in range(50000):
   for ret in pending_returns[:]:
    if c.pc==ret['pc']and c.sp==ret['sp']:spans.append(dict(name=ret['name'],cycles=c.processorCycles-ret['start']));pending_returns.remove(ret)
   if c.pc in hooks:
    name=hooks[c.pc];ret=m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1;pending_returns.append(dict(pc=ret&65535,sp=(c.sp+2)&255,name=name,start=c.processorCycles))
   before=len(m.writes);c.step()
   if any(at==0x4014 for at,v in m.writes[before:]):break
  else:raise AssertionError(('NMI prefix timeout',hex(c.pc),m.banks))
  return dict(entry_through_STA4014_instruction_cycles=c.processorCycles,spans=spans,active=m[address(bundle,'InvHudActive')],upper=m[address(bundle,'X5HudChrUpper')],mask=m[0x2001],CPU_data_writes=sum(at==0x2007 for at,v in m.writes),palette_reads=len(m.reads),SP_at_DMA=c.sp,actualC=m.banks[2],fiveSMC_writes=[(at,v)for at,v in m.writes if at in [address(bundle,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(bundle,'FarcallJmpTarget_SMC')+2]])
 patterns={'PnPublish_slots0_6_7':[0x80,0,0,0,0,0,0x81,0x81,0,0,0,0],'six_direct_synthetic_boundary':[0x80]*4+[0,0,0x81,0x81,0,0,0,0],'all_legacy_synthetic_boundary':[0]*12,'all_direct_synthetic_boundary':[0x80]*12}
 for failure in genuine:
  packet=failure['source_packet']['bytes'][:failure['decoded']['consumed_bytes']]+[0];variant=failure['variant'];cold=failure['profile']=='pentarou-easy';filtered=packet_without_labels(packet)
  if cold:assert filtered[:3]==[0x23,0xc0,8];filtered=filtered[11:]
  for pattern,values in patterns.items():
   guarded='PnHudPreUpdateScreen'in new['syms'];before=execute(old,packet,variant,int(cold),1,False,values);after=execute(new,filtered,variant,int(cold),0 if cold else 2*variant+1,False,values,attr_offset=31 if guarded and not cold else None);rows.append(dict(profile=failure['profile'],phase='cold_capture'if cold else'steady_attributes',CHR_fixture=pattern,CHR_mode=values,before=before,after=after,saved_instruction_cycles=before['entry_through_STA4014_instruction_cycles']-after['entry_through_STA4014_instruction_cycles']))
   if cold:
    q=Arena(new,18);q.put(DisableScreenFlag=0,VvVariant=variant,VvMeter=0,VvHudDirty=1,InvHudActive=0,X5HudChrUpper=1,VRAM_Buffer1_Offset=0,ReloadCHRBank=0,PnInitialized=0x50,PnBombPaletteReady=1);q.array('VRAM_Buffer1',[0]*84);q.invoke('PnHud');full=[q.get('VRAM_Buffer1',i)for i in range(43)];after=execute(new,full,variant,0,0,True,values);assert after['active']==2*variant+1;rows.append(dict(profile=failure['profile'],phase='following_first_full',CHR_fixture=pattern,CHR_mode=values,after=after))
    q.put(FrameCounter=0,ColorRotateOffset=0,AreaType=1);q.invoke('ColorRotation');appended=[q.get('VRAM_Buffer1',i)for i in range(q.get('VRAM_Buffer1_Offset')+1)];assert len(appended)==50 and appended[:42]==full[:42];after=execute(new,appended,variant,0,0,True,values);rows.append(dict(profile=failure['profile'],phase='first_full_then_actual_ColorRotation_append_COMPONENT',CHR_fixture=pattern,CHR_mode=values,after=after,concern='Actual compiled later producer appends7B after first full42B even when HUD initially admitted at offset0. Source component, not a naturally recorded first-HUD epoch.'))
   else:
    # The original live heavy prefix is genuine. Invalid-cache first publish
    # at that same prefix is an admitted CPU component, not asserted to be a
    # naturally observed first-HUD chronology. Do not call this a native fail.
    offset=packet.index(0x20,30);assert packet[offset:offset+3]==[0x20,0x22,28]and offset==31
    q=Arena(new,18);q.put(DisableScreenFlag=0,VvVariant=variant,VvMeter=0,VvHudDirty=1,InvHudActive=0,X5HudChrUpper=1,VRAM_Buffer1_Offset=offset,ReloadCHRBank=0,PnInitialized=0x50,PnBombPaletteReady=1);q.array('VRAM_Buffer1',[0]*84);q.array('VRAM_Buffer1',packet[:offset]+[0]);q.invoke('PnHud');full=[q.get('VRAM_Buffer1',i)for i in range(q.get('VRAM_Buffer1_Offset')+1)]
    if guarded:
     assert full==packet[:offset]+[0]and q.get('X5HudChrUpper')==1 and q.get('VvHudDirty')==1;after=execute(new,full,variant,0,0,False,values);assert after['active']==0
     rows.append(dict(profile=failure['profile'],phase='first_full_heavy_prefix_deferred_in_foreground',CHR_fixture=pattern,CHR_mode=values,admission_offset=offset,after=after))
    else:
     assert full==packet
     after=execute(new,full,variant,0,0,True,values,admission_offset=offset);assert after['active']==2*variant+1;rows.append(dict(profile=failure['profile'],phase='first_full_on_genuine_heavy_prefix_COMPONENT_NOT_NATIVE_REACHABILITY',CHR_fixture=pattern,CHR_mode=values,admission_offset=offset,after=after,concern='Current offset<40 admission permits this component. Natural first-full coincidence and hardware deadline are not established.'))
 q=dict(passed=True,native_run=False,goal_complete=False,ROM_sha256=sha(a.candidate),script_sha256=sha(Path(__file__)),rows=rows,scope='Whole actual compiled regular-NMI prefix (no hooks skipped, no external routine stubs), from first instruction through completed STA4014 instruction. Explicit synthetic legal CHR mode vectors and packet reconstructions; not an exact replay of unavailable full historical RAM. CPU model does not emulate513/514-cycle DMA, PPU rendering/OAM destination, physical IRQ scheduling, or DMC stalls. No full hardware-NMI deadline claim. The native410-cycle CHR span remains its immutable native observation.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),rows=[dict(profile=r['profile'],phase=r['phase'],CHR_fixture=r['CHR_fixture'],before=r.get('before',{}).get('entry_through_STA4014_instruction_cycles'),after=r['after']['entry_through_STA4014_instruction_cycles'],CHR_spans=[s for s in r['after']['spans']if s['name']=='BankSwitchCHR'])for r in rows]),indent=2))
if __name__=='__main__':main()
