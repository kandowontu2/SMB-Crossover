"""Prepare BASIC140 remaining genuine effect/mode cells; source-only, no launch."""
from pathlib import Path
import argparse,hashlib,json,shutil
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--mode',type=int,choices=[0,1],required=True);p.add_argument('--event',type=lambda t:int(t,0),choices=[0x13,0x15,0x24,0x21,0x1e,0x1f,0x2f],required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rom=D/'cv3-remaining-queue256-v1/qualified-v3/candidate.nes';assert sha(rom)=='0c45ce16fa189debc2303f4df664a0e75f326a807a64bf23280797734615339c';b=load(rom);labels=qualified(rom)
 parent=D/'cv3-remaining-static-observer-v1/replay-packet-v1/held0802';assert sha(parent/'run.lua')=='784f86a5d5cecd2a1d97934fc9f5e514f62abf820967e356da08d5dea9fd1148';old=(parent/'run.lua').read_text();cfg=json.loads((parent/'configuration.json').read_text());original_cfg=json.loads((parent/'configuration.json').read_text())
 def hook(name):
  if'::'in name:
   scope,leaf=name.split('::');pc=labels[(scope,leaf)];off=location(b,scope)+pc-address(b,scope)
  else:pc=address(b,name);off=location(b,name)
  return dict(address=pc,physical_bank=(off-16)//8192,bytes=list(b['raw'][off:off+3]),genuine_source_symbol=name)
 variant,sub,cue={0x13:(1,1,1),0x15:(1,2,2),0x24:(2,1,3),0x21:(2,2,4),0x1e:(2,3,5),0x1f:(3,0,6),0x2f:(3,0,7)}[a.event];cfg['variant']=variant;cfg['mode']=a.mode;cfg['expected_cue']=cue;cfg['expected_actors']=0 if cue==7 else 3 if cue in[4,5]else 1;cfg['expected_cues']=3 if cue in[4,5]else 1;cfg['queue_protocol']=1
 cfg['cases']=[dict(name=f'basic-source{a.event:02x}-coldmode{a.mode}',kind='bat'if cue==7 else'fireball'if cue==6 else'sub',profile='basic',mode=a.mode,sub=sub,event=a.event,updates=140)]
 for name,h in cfg['hooks'].items():
  if name=='NmiReturn':off=location(b,'NonMaskableInterrupt')+int(b['syms']['NonMaskableInterrupt']['size'],0)-1;h.update(address=address(b,'NonMaskableInterrupt')+int(b['syms']['NonMaskableInterrupt']['size'],0)-1,physical_bank=(off-16)//8192,bytes=[b['raw'][off]])
  elif name in['NoLagSoDraw','SkipDrawingCauseLagged']:
   pc=labels[(name,)];off=location(b,'GameCoreRoutine')+pc-address(b,'GameCoreRoutine');h.update(address=pc,physical_bank=(off-16)//8192,bytes=list(b['raw'][off:off+3]))
  else:h.update(hook(name))
 for n in list(cfg['ram']):cfg['ram'][n]=address(b,n)
 for n in['Cv3FxProducerFast','Cv3FxDrain','Cv3FxDrainGate','Cv3FxSpawn','Cv3Spawn','Cv3FxService::Decode','Cv3FxResidentNoise::NC15','Cv3MusicAndNoiseTick::Continue','Cv3FxBatEnter','Cv3FxQueueCommand']:cfg['hooks'][n]=hook(n)
 for n in['Cv3FxQueue','Cv3FxQueueHead','Cv3FxQueueTail','Cv3FxQueueOverflow','Cv3FxPendingNoise','Cv3FxPendingPulse','GuestNativeApu','R0','R1']:cfg['ram'][n]=address(b,n)
 for n in['Cv3FxProducerFast','Cv3FxDrain','Cv3FxDrainGate']:
  if n not in cfg['perf_names']:cfg['perf_names'].append(n)
 s0=location(b,'Cv3Spawn');length=int(b['syms']['Cv3Spawn']['size'],0);target=address(b,'Cv3FxProducerFast');signature=bytes([0x20,target&255,target>>8]);body=b['raw'][s0:s0+length];assert body.count(signature)==1;cfg['producer_caller_return']=address(b,'Cv3Spawn')+body.index(signature)+3
 def caller_return(proc,target):
  start=location(b,proc);raw=b['raw'][start:start+int(b['syms'][proc]['size'],0)];at=address(b,target);sig=bytes([0x20,at&255,at>>8]);assert raw.count(sig)==1;return address(b,proc)+raw.index(sig)+3
 cfg['bat_caller_return']=caller_return('Cv3BatUpdate','Cv3FxBatEnter');cfg['bat_command_return']=caller_return('Cv3FxBatEnter','Cv3FxQueueCommand')
 cfg['queue_writers']={}
 for name,proc,opcode,operand in[('fast-slot','Cv3FxProducerFast',0x99,address(b,'Cv3FxQueue')),('fast-head','Cv3FxProducerFast',0xee,address(b,'Cv3FxQueueHead')),('command-slot','Cv3FxQueueCommand',0x99,address(b,'Cv3FxQueue')),('command-head','Cv3FxQueueCommand',0xee,address(b,'Cv3FxQueueHead'))]:
  start=location(b,proc);n=int(b['syms'][proc]['size'],0);raw=b['raw'][start:start+n];sig=bytes([opcode,operand&255,operand>>8]);assert raw.count(sig)==1,(name,raw.hex());cfg['queue_writers'][name]=dict(pc=address(b,proc)+raw.index(sig),bank=(start-16)//8192,opcode=list(sig),genuine_owner=proc)
 start=location(b,'Cv3FxDrain');raw=b['raw'][start:start+int(b['syms']['Cv3FxDrain']['size'],0)];at=address(b,'AvAudioRequest');sig=bytes([0xa9,26,0x8d,at&255,at>>8]);assert raw.count(sig)==1;cfg['queue_writers']['legacy-transfer']=dict(pc=address(b,'Cv3FxDrain')+raw.index(sig)+2,bank=(start-16)//8192,opcode=list(sig[2:]),genuine_owner='Cv3FxDrain')
 cfg['publication_protocol']='Main slot write then final INC head; NMI owned drain/voice state. No fake typedAv publication or public-wrapper alias.'
 assert cfg['cases'][0]['profile']=='basic'and cfg['cases'][0]['updates']==140
 text=old.split('\n',1)[1];legacy_old='if entered and not done and (v==21 or v==22 or(v>=26 and v<=32)) then';legacy_new='if entered and not done and (v==21 or v==22 or(v>=26 and v<=32)) and not(C.queue_protocol==1 and v==26)then';assert text.count(legacy_old)==1;text=text.replace(legacy_old,legacy_new,1);module=(Path(__file__).with_name('cv3_remaining_sfx_queue_native_v2.lua')).read_text();assert text.count('local timing=assert')==1;text=text.replace('local timing=assert',module+'\nlocal timing=assert',1)
 assert text.count(' age=0;apuUpdate=-1\n')==1;text=text.replace(' age=0;apuUpdate=-1\n',' age=0;apuUpdate=-1\n queueStartCase()\n',1)
 assert text.count('local function finishCase()\n')==1;text=text.replace('local function finishCase()\n','local function finishCase()\n queueFinishCase()\n',1)
 needle='requests:close();perf:close();dmaBus:close()';assert text.count(needle)==1;text=text.replace(needle,needle+';queueLog:close();imageLog:close()',1)
 # All original actual arena/resource/controller code remains literal. Added
 # calls only observe/validate Lua state; no new emulated writes are introduced.
 reverse=text.replace(module+'\n','',1).replace(' queueStartCase()\n','',1).replace(' queueFinishCase()\n','',1).replace(';queueLog:close();imageLog:close()','',1);reverse=reverse.replace(legacy_new,legacy_old,1);assert reverse==old.split('\n',1)[1]
 script=a.output/'run.lua';script.write_text('CV3_REMAINING_NATIVE_CONFIG='+lua(cfg)+'\n'+text,newline='\n');(a.output/'configuration.json').write_text(json.dumps(cfg,indent=2)+'\n');shutil.copyfile(parent/'run.lua',a.output/'qualified-static-parent.lua');shutil.copyfile(rom.with_suffix('.lbl'),a.output/'candidate.lbl')
 assert script.read_text().endswith('installStaticReturns()\n')and not any(w in script.read_text().splitlines()[0]for w in['True','False'])
 result=dict(prepared=True,native_executed=False,scope='One source-prepared0c45 BASIC140 genuine effect/mode cell, no native grant/launch. Original controller/resource/seed/arena/hardware guards retained. Legitimate case metadata changes per oldv7 mapping; NMI legacy26 transfer separately observed from main request.',ROM=str(rom),ROM_sha256=sha(rom),script=str(script),script_sha256=sha(script),configuration_sha256=sha(a.output/'configuration.json'),qualified_parent_script_sha256=sha(parent/'run.lua'),module_sha256=sha(Path(__file__).with_name('cv3_remaining_sfx_queue_native_v2.lua')),literal_controller_seed_guard_code_retained=True,case_metadata_exact_old_v7_mapping=True,actual_numeric_mode=a.mode,event=a.event,expected_raw_cue=cue,legacy_transfer_observer_delta='Old generic typedAv callback excludes actual NMI legacy26 transfer so one main publication remains one request. Actual transfer now separately recorded with genuine writer/audio owner; hardware guards unchanged.',all_old_seed_controller_guard_code_retained=True,actual_main_publication='Cv3FxProducerFast entries with actualCv3Spawn returnPC; genuine STA slot and final INC head commits. RMW dummy writes are observed separately; no alias.',actual_NMI_consumer='Cv3FxDrain entry/return inside AudioUpdate and hardwareNMI, committed byte sequence and tail=head; pending/Owned snapshots.',original_APU_and_source_guard='All old rawAPU/voice/DMC logs/guards retained. Added ordered actual source register-image capture at genuine Decode/resident NC15 boundaries, without400F masks.',intentional_timing='requests/cueEpoch now attach to actual queue-head commit, source event1E (rawcue5) rather than old typedAv31. ActualNMI consumer epoch/cues preserved separately; no artificial event rephasing.',new_game_RAM_writes=0,additional_perf_hooks=['Cv3FxProducerFast','Cv3FxDrain','Cv3FxDrainGate'],tools={f.relative_to(ROOT).as_posix():sha(f)for f in[Path(__file__),Path(__file__).with_name('cv3_remaining_sfx_queue_native_v2.lua'),ROOT/'tools/audit/observe_chip_committed_write.py']})
 (a.output/'preparation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
