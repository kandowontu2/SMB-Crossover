"""Prepare only a220-frame paired raw bootstrap diagnostic, never a gameplay retry."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from observe_chip_committed_write import lua
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'mm-proto-shot-mux-native-ready-v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def prepare(out):
 assert not out.exists()and not out.resolve().is_relative_to(R);out.mkdir(parents=True)
 neg=P/'title-dma-negative-v1/proof.json';assert sha(neg)=='b5d354c9e05516aece817ea11ce701f828074ae4111e4860f542f6c4c6386c18'
 prefix=P/'native/megaman-easy/inputs.csv';rows=list(csv.DictReader(prefix.open()));assert len(rows)==183 and sum(r['mask']!='0'for r in rows)==1 and rows[179]['mask']=='16'and rows[179]['frame']=='180'
 shutil.copyfile(prefix,out/'fixed-original-prefix.csv')
 observer=R/'tools/audit/mm_proto_bootstrap_dma_diag_v2.lua';dispatcher=R/'tools/audit/tmnt_static_exec_dispatcher_v1.lua'
 for q in[observer,dispatcher]:shutil.copyfile(q,out/q.name)
 luadeps=D/'final-tmnt-items-v1/lua-parser-deps-v1';sys.path.insert(0,str(luadeps));from luaparser import ast
 ast.parse(observer.read_text());ast.parse(dispatcher.read_text())
 roms=dict(baseline=D/'root-chip-hud-composed-v1/candidate.nes',candidate=D/'mm-proto-shot-mux-v4/candidate.nes');expected=dict(baseline='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99',candidate='c5b65d96f6d76d4e9ebc62b5b28ae02e9cdea838414035fb1b2d4e0e4b706e48')
 profiles=['UpdateScreen','SamusFreezeUpdateScreen','BankSwitchCHR','AudioUpdate','OAMandReadJoypad']
 names=['SelectedCharacter','ProtoVariant','OperMode','OperMode_Task','GameEngineSubroutine','NmiDisable','NmiSkipped','DisableScreenFlag','Mirror_PPUMASK','Mirror_PPUCTRL','VRAM_Buffer_AddrCtrl','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','VRAM_Buffer1','VRAM_Buffer2','NmiR0','NmiR1','CurrentBank','CurrentBankC','ScreenRoutineTask','FrameCounter','GamePauseStatus']
 configs={}
 for label,rom in roms.items():
  assert sha(rom)==expected[label];b=scoped_load(rom);folder=out/label;folder.mkdir()
  def hook(n,delta=0):
   at=location(b,n)+delta;return dict(pc=address(b,n)+delta,bank=(at-16)//8192,bytes=list(b['raw'][at:at+8]))
  hooks={n:hook(n)for n in profiles};hooks.update(NmiEntry=hook('NonMaskableInterrupt'),NmiReturn=hook('NonMaskableInterrupt',int(b['syms']['NonMaskableInterrupt']['size'],0)-1),GameLoopEntry=hook('GameLoop'),GameLoopDone=hook('GameLoop',int(b['syms']['GameLoop']['size'],0)-1),DmaComplete=hook('OAMandReadJoypad',7))
  assert hooks['GameLoopDone']['bank']==126 and hooks['GameLoopDone']['pc']==0x8355
  end=location(b,'GameLoop')+int(b['syms']['GameLoop']['size'],0)-1;assert b['raw'][end-5:end+1]==bytes.fromhex('a9008d390160')
  cfg=dict(profile_names=profiles,hooks=hooks,ram={n:address(b,n)for n in names},prefix=(out/'fixed-original-prefix.csv').as_posix(),limit=220,dma_next=dict(pc=0xe005,bank=127))
  configs[label]=cfg;put(folder/'config.json',cfg)
  body='dofile('+json.dumps((out/dispatcher.name).as_posix())+')\nBOOTSTRAP_DMA_DIAGNOSTIC='+lua(cfg)+'\ndofile('+json.dumps((out/observer.name).as_posix())+')\nTMNT_STATIC_EXEC.install()\n'
  (folder/'run.lua').write_text(body);ast.parse(body)
 assert configs['baseline']==configs['candidate']
 runtime=D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator';env={str(q):sha(q)for q in[runtime/'Mesen.exe',*runtime.glob('*.dll'),runtime/'settings.json',Path('C:/Mesen2/settings.json')]}
 (out/'environment').mkdir();shutil.copyfile(runtime/'settings.json',out/'environment/worker-settings.json');shutil.copyfile(Path('C:/Mesen2/settings.json'),out/'environment/user-settings.json')
 worker=json.loads((runtime/'settings.json').read_bytes().decode('utf-8-sig'));assert not worker['Nes']['RemoveSpriteLimit']and not worker['Nes']['AdaptiveSpriteLimit']and worker['Nes']['PpuExtraScanlinesBeforeNmi']==worker['Nes']['PpuExtraScanlinesAfterNmi']==worker['Emulation']['RunAheadFrames']==0
 put(out/'environment.json',dict(files=env,persisted_Nes_settings=worker['Nes'],persisted_Emulation_settings=worker['Emulation'],no_settings_writes=True))
 deps={Path(p)for p in json.loads((P/'bindings.json').read_text())}|{Path(p)for p in env}|{neg,P/'title-dma-negative-v1/catalog.json',Path(__file__),observer,dispatcher,R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py'}
 for rom in roms.values():deps|={rom,*[rom.with_suffix(ext)for ext in['.dbg','.lbl','.map']]}
 deps|={q for q in out.rglob('*')if q.is_file()};bindings={str(q):sha(q)for q in sorted(deps)};put(out/'bindings.json',bindings)
 commands={label:[sys.executable,'-B',str(Path(__file__)),'--output',str(out),'--run-granted',label]for label in roms};put(out/'commands.json',commands)
 result=dict(prepared=True,native_run=False,diagnostic_only=True,ROMs={k:dict(path=str(v),sha256=sha(v))for k,v in roms.items()},limit_PPU_endFrames=220,maximum_proposed_native_launches=2,sequential_one_worker=True,grant_required=True,bindings=len(bindings),bindings_sha256=sha(out/'bindings.json'),fixed_original_prefix_sha256=sha(prefix),original_prefix_polls=183,subsequent_inputs='Neutral controller only; no further menu selection or gameplay requested',same_config_body_per_ROM=True,new_native_code_hits_must_be_reported=True,zero_expected_gameplay_coverage=True,raw_destination_serialized_before_every_equality_decision=True,all256_bytes_write_values_stamps_and_actual_OAMADDR_preserved=True,no_equality_masks=True,mismatches='Every raw difference retained; diagnostic exits1 if ANY complete256 image differs. A completed diagnostic is not a pass.',routine_costs='Inclusive actual UpdateScreen/SamusFreezeUpdateScreen/BankSwitchCHR/AudioUpdate/OAMandReadJoypad entry-return costs, nested work explicitly included.',packet_snapshots='NMI metadata all bootstrap; actual UpdateScreen pointers/full1024 byte and both256-byte queues frames176..190; bounded PPU bus writes same epoch. Snapshots are observed memory windows, not a parser/universal read closure.',controller_state_writes=False,settings_files_untouched=True,recorded_commands=commands,old_negative_sha256=sha(neg),old_failed_physical256_unlogged=True,primary_current_source_lead='https://github.com/nesdev-org/MesenCE/blob/master/Core/NES/NesPpu.cpp',primary_source_binary_binding_unproved=True,limits='Preparation/parser-only. No native launch or title fault/pinned-core diagnosis yet. Exact failed source attributes0 excludes direct source attribute masking alone; actual failed bytes/OAMADDR/halt timing still needed. No long gameplay retry, candidate adoption, fairness or matched gameplay-performance claim.')
 put(out/'readiness.json',result);print(json.dumps(dict(prepared=True,native_run=False,readiness_sha256=sha(out/'readiness.json'),bindings=len(bindings),commands=commands),indent=2))
def launch(out,label):
 q=json.loads((out/'readiness.json').read_text());assert sha(out/'bindings.json')==q['bindings_sha256']
 for p,h in json.loads((out/'bindings.json').read_text()).items():assert sha(p)==h,p
 folder=out/label;assert not(folder/'launch.json').exists(),'One proposed launch only, no retry'
 query="@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count";assert int(subprocess.check_output(['powershell','-NoProfile','-Command',query],text=True).strip())<2
 rom=Path(q['ROMs'][label]['path']);command=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),'--emulator',str(D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'),str(folder/'run.lua'),str(rom),'--timeout','120','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 put(folder/'launch.json',dict(command=command,ROM_sha256=q['ROMs'][label]['sha256'],diagnostic_only=True))
 with(folder/'host.log').open('w')as f:r=subprocess.run(command,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 result=json.loads((folder/'diagnostic-result.json').read_text())if(folder/'diagnostic-result.json').exists()else{};put(folder/'exit.json',dict(exit=r.returncode,diagnostic_complete=result.get('diagnostic_complete',False),hardware_equality_passed=result.get('passed',False)))
 print(json.dumps(dict(label=label,exit=r.returncode,result=result),indent=2));raise SystemExit(r.returncode)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-granted',choices=['baseline','candidate']);a=p.parse_args();launch(a.output,a.run_granted)if a.run_granted else prepare(a.output)
