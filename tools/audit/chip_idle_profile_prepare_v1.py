"""Prepare one source-only static Chip8b4 cost/snapshot overlay, no native launch."""
from pathlib import Path
import argparse,csv,hashlib,json
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rom=D/'root-chip-native-adapter-v6/candidate.nes';assert sha(rom)=='8b4accd2672b4b85508a365f81f499fb786f25e5572932aafc21837d5e591824';old=D/'root-chip-native-audio-v3/candidate';baseline=D/'root-chip-native-audio-v1/baseline';b=load(rom);q=qualified(rom);bindings=json.loads((old/'manifest.json').read_text())
 for path,h in bindings.items():assert sha(path)==h,('Original environment/input drift',path)
 def bind(p):bindings[str(p)]=sha(p)
 names=['GameLoop','OperModeExecutionTree','GameCoreRoutine','PlayerCtrlRoutine','EnemiesAndLoopsCore','DrawAllMetasprites','CdMovement','CdWeapons','CdGraphics','CdBodyContact','AudioUpdate','RemainingAudioBegin','GuestAudioBegin','ExpandedAudioUpdate','ChNativeAudioUpdate','ChNativeBridge','ChNativeService','ChNativeSourcePlay','ChNativeSourceInit','ChNativeRead','ChNativeMapC1High','ChNativeMapC5High','ChNativeSyncC1Low','GuestAudioFinish','GuestAudioNativeFlush','SophiaLandAudioTick']
 def hook(n):
  proc,sep,leaf=n.partition('::');pc=q[(proc,leaf)]if sep else address(b,n);off=location(b,proc)+pc-address(b,proc);return dict(name=n,address=pc,physical_bank=(off-16)//8192,bytes=list(b['raw'][off:off+3]))
 functions=[hook(n)for n in names];pools=sorted({(h['physical_bank'],h['address']&0xe000)for h in functions}|{(126,0x8000),(127,0xe000)})
 returns=set()
 for bank,base in pools:
  raw=b['raw'][16+bank*8192:16+(bank+1)*8192]
  for i in range(8190):
   if raw[i]==0x20:returns.add((base+i+3)&65535)
 smc=next(g for g in b['segs'].values()if g.get('name')=='"SMCCODE"');start=int(smc['start'],0);end=start+int(smc['size'],0)-1;assert len(returns)<2048 and 0x100<=start<=end<0x200
 nmi=hook('NonMaskableInterrupt');irq=hook('IrqScrollSplit')
 def endhook(n,h):
  pc=address(b,n)+int(b['syms'][n]['size'],0)-1;off=location(b,n)+pc-address(b,n);assert b['raw'][off]==0x40;return dict(name=n+' preRTI',address=pc,physical_bank=h['physical_bank'],bytes=[64])
 cfg=dict(first_wall=380,last_wall=460,snapshot_windows=[[390,395],[421,426],[451,456]],max_snapshots=64,max_spans=16000,max_events=3000,ram_ranges=[[0,2047],[0x5c00,0x7fff]],ram_bytes=11264,functions=functions,return_pcs=sorted(returns),smc_start=start,smc_end=end,source_return=hook('ChNativeBridgeReturn'),interrupts=dict(NMI=nmi,NMIReturn=endhook('NonMaskableInterrupt',nmi),IRQ=irq,IRQReturn=endhook('IrqScrollSplit',irq)),markers=[hook(n)for n in['GameLoop::PauseSkip','GameEngine::NoLagSoDraw']])
 body=(ROOT/'tools/audit/chip_idle_profile_capture_v1.lua').read_text(encoding='utf-8');text=(old/'run.lua').read_bytes().decode('utf-8');anchor='local C=assert(CHIP_AUDIO_NATIVE)';assert text.count(anchor)==1;before,after=text.split(anchor,1);script=a.output/'run.lua';script.write_bytes((before+'CHIP_IDLE_PROFILE='+lua(cfg)+'\n'+body+'\n'+anchor+after).encode('utf-8'));assert 'emu.write('not in body and 'emu.setInput('not in body and 'emu.stop('not in body
 for name,p in[('baseline',baseline),('candidate',old)]:
  rows=list(csv.DictReader((p/'cadence.csv').open()));last=None;steps=[]
  for row in rows:
   value=int(row['nmiSkipped'])
   if last is not None and value!=last:steps.append({k:int(row[k])for k in['wall','updates','dmas','sourceCalls','nmiSkipped']})
   last=value
  out=dict(native_original_result=json.loads((p/'audio-native.json').read_text()),first_skip_counter_changes=steps[:6],qualification='Old NmiSkipped is a cumulative byte; startup value10 is not a new active skip. Saved CSV has no stackedPC/entry RAM or function timings.');(a.output/(name+'-saved-observations.json')).write_text(json.dumps(out,indent=2)+'\n')
  for f in[p/'cadence.csv',p/'audio-native.json',p/'ownership-guards.json',p/'run.lua',p/'manifest.json',p/'preparation.json']:bind(f)
 bind(rom);bind(rom.with_suffix('.dbg'));bind(rom.with_suffix('.lbl'));bind(ROOT/'tools/audit/chip_idle_profile_capture_v1.lua');bind(Path(__file__).resolve());bind(script)
 (a.output/'configuration.json').write_text(json.dumps(cfg,indent=2)+'\n');bind(a.output/'configuration.json')
 command=['python','tools/audit/run_mesen_isolated.py','--output',str(a.output),'--emulator',json.loads((old/'preparation.json').read_text())['emulator'],str(script),str(rom),'--timeout','180','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false','--option=--nes.removeSpriteLimit=false']
 result=dict(prepared=True,native_executed=False,native_grant=False,production_mutated=False,ROM=str(rom),ROM_sha256=sha(rom),script=str(script),script_sha256=sha(script),original_script_sha256=sha(old/'run.lua'),original_guard_source_and_controller_text_byteexact_around_insertion=True,original_coldmenu_Chip_Easy0_1300_emptyinput_source_SMC_stack_PPU_8sprite_guards_retained=True,profile_window=[380,460],snapshot_windows=cfg['snapshot_windows'],source_first_extra_skip=dict(wall=393,sourceCalls=3,qualification='Immutable old CSV; exact actual timing and foreground entry-state missing'),static_return_addresses=len(returns),return_pools=[dict(bank=x,base=y)for x,y in pools],functions=len(functions),bounded_RAM_snapshot_limit=64,bytes_per_snapshot=11264,no_emulated_state_writes=True,all_frozen_bindings=bindings,future_command_NOT_GRANTED=command,counterfactual_limit='Entry RAM/CPU/banks support finite deterministic CPU-only replay after capture. Such replay does not reproduce native NMI acceptance, PPU behavior, DMA stalls or hardware scheduling unless explicitly separately modeled. No optimization justified until actual capture.',tool_sha256=sha(__file__))
 (a.output/'preparation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['all_frozen_bindings','future_command_NOT_GRANTED','return_pools']},indent=2))
if __name__=='__main__':main()
