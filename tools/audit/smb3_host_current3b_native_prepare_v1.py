"""PREPARE ONLY one cold actual SMB3Mario Easy opening, at most1200PPU frames."""
from pathlib import Path
import argparse,copy,difflib,json,re,shutil,sys
from smb3_host_current3b_cpu_v1 import D,R,FIELDS,native_address,sha,put
from smb3_host_current3b_freeze_v1 import dependencies
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua
from mario_powerups900_smb3_prepare_v1 import static_chr
from mario_powerups_current3cee_static_v2 import symbols,runtime,chr_equivalence
from final_item_abilities_current731_prepare_v1 import protocol,dma_mocks

PACKET=D/'smb3-host-current3b-v3'
def hook(b,name,size=8,delta=0):
 at=location(b,name)+delta;pc=address(b,name)+delta;bank=(at-16)//8192;aliases=[70,97,127]if bank==127 else[bank]
 raw=list(b['raw'][at:at+size])
 for e in aliases:
  if bank==127:assert list(b['raw'][16+e*8192+pc-0xe000:16+e*8192+pc-0xe000+size])==raw
 return dict(pc=pc,bank=bank,banks=aliases,resident=bank==127,bytes=raw)
def once(s,old,new):assert s.count(old)==1,old;return s.replace(old,new)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(R);out.mkdir(parents=True,exist_ok=False)
 freeze=PACKET/'source-freeze-v1/readiness.json';ready=json.loads(freeze.read_text());assert ready['source_ready'] and not ready['native_run']
 for q in ready['bindings']:assert sha(q['path'])==q['sha256'],q['path']
 b=scoped_load(PACKET/'candidate.nes');rom=PACKET/'candidate.nes'
 reference=D/'current3cee-remaining27-routes-v1/native/mario3-easy';original=json.loads((reference/'manifest.json').read_text());assert original['result']['cleared'] and original['result']['deaths']==0
 envpath=D/'current3b-nmi-regression-ready-v2/readiness.json';env=copy.deepcopy(json.loads(envpath.read_text())['environment'])
 for n in ['emulator','core','worker_settings','user_settings']:assert sha(env[n])==env[n+'_sha256'],n
 assert env['persisted_worker_conditions']['RemoveSpriteLimit'] is False and env['persisted_worker_conditions']['AdaptiveSpriteLimit'] is False
 put(out/'environment.json',env)
 folder=out/'native';folder.mkdir();(folder/'frames').mkdir()
 cfg=copy.deepcopy(original['config']);cfg.update(out=folder.as_posix()+'/',limit=1200,capture=120,record=False,policy=(folder/'policy.lua').as_posix(),audit=(folder/'audit.lua').as_posix(),replay=None,prefix=None)
 # The exact qualified ordinary movement body and real cold menu controller
 # remain unchanged. The endpoint is a finite opening, never a claimed clear.
 guard=reference.parent/'native-guard.lua';shutil.copyfile(guard,folder/'native-guard.lua')
 policy=(reference/'policy.lua').read_text();body=policy.split('\n',1)[1];(folder/'policy.lua').write_text('dofile('+lua((folder/'native-guard.lua').as_posix())+')\n'+body,encoding='utf-8',newline='\n')
 harness=(reference/'harness.lua').read_text();harness=once(harness,'if cfg.replay and audit and audit.failure then','if audit and audit.failure then');harness=once(harness,'if frame>=cfg.limit then finish(false,\'frame limit\');return end','if frame>=cfg.limit then finish(true);return end');harness=once(harness,'{"cleared":','{"component_complete":');(folder/'harness.lua').write_text(harness,encoding='utf-8',newline='\n')
 audit=static_chr((reference/'audit.lua').read_text());(folder/'audit.lua').write_text(audit,encoding='utf-8',newline='\n')
 # Reuse the qualified complete256/per-write/timing protocol. Only its genuine
 # E-window bank admission extends to byte-identical current clone aliases.
 dmatext=(R/'tools/audit/final_item_abilities_dma731_v1.lua').read_text()
 dma=once(dmatext,' if bank(pc)~=dmaProtocol.bank then return end',' if not C.residentAlias(bank(pc))then return end')
 baseobserver=(R/'tools/audit/luigi_profile641_route_observer_v2.lua').read_text();prefix=baseobserver.split("hook('EnemyStomped'",1)[0]
 tail=baseobserver.split("local pixels=assert",1)[1];tail='local pixels=assert'+tail
 tail=tail.split('local stop=emu.stop',1)[0]
 prefix=once(prefix,'local C=assert(LUIGI_ROUTE_OBSERVER)','local C=assert(SMB3_RENDER_OBSERVER)')
 prefix=once(prefix,' if bank(h.pc)~=h.bank then return end'," local actual=bank(h.pc);if h.bank==127 then assert(C.residentAlias(actual),'Genuine resident alias for '..n)elseif actual~=h.bank then return end")
 prefix=prefix.replace('-- QUALIFIED_DMA_BODY',dma)
 # Source-independent render observer close is explicit; no Luigi/stomp gate
 # or name survives as a fake music qualification requirement.
 finish="""
local stop=emu.stop
emu.stop=function(code)
 if not closed then
  closed=true;pixels:close();index:close();events:close();dmaProofLog:close()
  local f=assert(io.open(OUTPUT..'render-observation-result.json','w'))
  f:write(json({passed=code==0 and frames==1200,fullPPUframes=frames,updates=updates,draws=draws,commits=commits,nmiChecks=nmis,irqChecks=irqs,minInterruptSP=minSP,actual_mode=r('CrossoverBehaviorVersion'),actual_character=r('SelectedCharacter'),actual_variant=r('M3Variant'),scope='Actual fullPPU/E008complete256/per-write/scoped-enable/interrupt/5SMC/cadence opening. No matched-parent cadence, whole-campaign, waveform or every-frame visual pass.'}));f:close()
 end
 stop(code)
end
"""
 observer=prefix+tail+finish
 observer=observer.replace("r('MarioVariant')","r('M3Variant')")
 (out/'render-observer.lua').write_text(observer,encoding='utf-8',newline='\n')
 hooks={n:hook(b,source,1 if n.endswith('Return')else 8,delta)for n,source,delta in[
  ('NmiEntry','NonMaskableInterrupt',0),('NmiReturn','NonMaskableInterrupt',int(b['syms']['NonMaskableInterrupt']['size'],0)-1),('IrqEntry','IrqScrollSplit',0),('IrqReturn','IrqScrollSplit',int(b['syms']['IrqScrollSplit']['size'],0)-1),('GameLoop','GameLoop',0),('GameLoopReturn','GameLoop',int(b['syms']['GameLoop']['size'],0)-1),('DrawAll','DrawAllMetasprites',0)]}
 render=dict(ROM_sha256=ready['candidate_ROM_sha256'],hooks=hooks,dma_protocol=protocol(b),smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 musicmodule=R/'tools/audit/smb3_host_current3b_native_v1.lua';text=musicmodule.read_text()
 names=set(re.findall(r"\br\('([\w]+)'",text))|{'B3Source4012','B3Source4015'}
 music=dict(ROM_sha256=ready['candidate_ROM_sha256'],hooks={n:hook(b,source)for n,source in [('SourceInit','B3Source9000'),('SourcePlay','B3SourceA000'),('AudioUpdate','AudioUpdate')]},ram={n:address(b,n)for n in names},source_state_addresses=[native_address(b,f,True)for f in FIELDS],original_source_addresses=FIELDS,resident_aliases=[70,97,127],payload_banks=[78,86,90,93,95,96,98,118,119],zp=address(b,'B3SourceZp'))
 music['ram'].update({n:address(b,n)for n in ['GuestNativeApu','B3VirtualMaps']})
 put(out/'configuration.json',dict(roster=cfg,render=render,music=music))
 script='ROSTER_CONFIG='+lua(cfg)+'\nSMB3_RENDER_OBSERVER='+lua(render)+'\nSMB3_RENDER_OBSERVER.residentAlias=function(b)return b==70 or b==97 or b==127 end\nSMB3_MUSIC_NATIVE_CONFIG='+lua(music)+'\ndofile('+lua((out/'render-observer.lua').as_posix())+')\ndofile('+lua(musicmodule.as_posix())+')\ndofile('+lua((folder/'harness.lua').as_posix())+')\nassert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()\nassert(SMB3_MUSIC_INSTALL_RETURN_DISPATCHER)()\n'
 (out/'run.lua').write_text(script,encoding='utf-8',newline='\n')
 for s in [script,text,observer,policy,harness,audit]:assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(',s),'No fixture game-state writes'
 # Compile/load the whole actual generated startup under the qualified mocked
 # API; then prohibit host callback mutation while advancing inactive frames.
 luadeps=D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1';sys.path.insert(0,str(luadeps));from lupa.lua54 import LuaRuntime
 labels,banks=symbols(b,rom);rt=runtime(LuaRuntime,labels,banks)
 rt.execute("state['cpu.ps']=32;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end")
 rt.execute(script);count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].kind==2 and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
 rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
 for frame in range(1,5):rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.inputPolled);runevents(emu.eventType.endFrame)")
 assert rt.eval('#callbacks')==count and rt.eval('inputCalls')==4
 chrproof=chr_equivalence(LuaRuntime,(reference/'audit.lua').read_text(),audit,labels,banks,17)
 dmamocks=dma_mocks(LuaRuntime,dmatext,dict(dma_protocol=render['dma_protocol']))
 # Original13 hardware rejection mocks remain literal; alias admission is
 # separately source-bound above to actual same-byte70/97/127 protocol copies.
 put(out/'static-controls.json',dict(passed=True,native_run=False,callbacks=count,inactive_whole_startup_frames=4,runtime_registration_removal=0,original_controller_body_exact=True,original_CHR_static_equivalence=chrproof,original_DMA_13_rejection_mocks=dmamocks,qualified_DMA_body_only_delta='Physical bank admission accepts actual byte-identical70/97/127; all256 writes/full hardware/timing assertions unchanged.',actual_generated_native_script_sha256=sha(out/'run.lua')))
 diffs=''.join(difflib.unified_diff(baseobserver.splitlines(True),observer.splitlines(True),fromfile='qualified-luigi-route-observer',tofile='music-opening-render-observer'));(out/'render-observer.patch').write_text(diffs,encoding='utf-8',newline='\n')
 nativecmd=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),'--emulator',env['emulator'],str(out/'run.lua'),str(rom),'--timeout','180']+['--option='+x for x in env['actual_command_overrides']]
 files={Path(x['path'])for x in ready['bindings']}|{freeze,envpath,Path(__file__),musicmodule,R/'tools/audit/luigi_profile641_route_observer_v2.lua',R/'tools/audit/final_item_abilities_dma731_v1.lua'}
 files|=set(dependencies([Path(__file__),R/'tools/audit/smb3_host_current3b_native_run_v1.py',R/'tools/audit/smb3_host_current3b_native_verify_v1.py',R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py']))
 files|={Path(env[n])for n in ['emulator','core','worker_settings','user_settings']}|{reference/n for n in ['manifest.json','policy.lua','harness.lua','audit.lua']}|{guard,rom.with_suffix('.lbl')}
 files|={f for f in luadeps.rglob('*')if f.is_file()and'__pycache__'not in f.parts}|{f for f in out.rglob('*')if f.is_file()}
 bindings={str(f.resolve()):sha(f)for f in sorted(files,key=str)}
 put(out/'readiness.json',dict(passed=True,status='PREPARE_DO_NOT_RUN',native_run=False,native_granted=False,ROM_sha256=ready['candidate_ROM_sha256'],source_ready_sha256=sha(freeze),native_command=nativecmd,bindings=bindings,environment=env,maximum_launches=1,native_workers=1,timeout_seconds=180,maximum_PPU_frames=1200,automatic_retries=0,stop_first_failure=True,baseline='No existing same-input3b M3 music/cadence native trace is available. No old differently-phased route is used as a matched parent control. This pilot measures actual facts; cadence comparison needs separately authorized matching inputs.',controller='Qualified3cee actual M3Mario Easy natural controller body and cold menu path unchanged. Only finite1200 endpoint/metadata/output paths and always-enabled original audit-failure check differ.',source_oracle='Postrun same-input original executable ordered logical sourceAPU/RAM/virtualmaps/AXYP/SP/source-state; existing physical common-mixer order retained and logged separately.',remaining_scope='Only opening/normal music; no native pause/title/othertrack/waveform/allroster claim. Actual DMC starts/fetches/clone-active aliases required whenever the observed original source emits enables.'))
 command=[sys.executable,'-B',str(R/'tools/audit/smb3_host_current3b_native_run_v1.py'),'--packet',str(out),'--expected-readiness-sha256',sha(out/'readiness.json'),'--native-grant']
 put(out/'command.json',dict(command=command,not_executed=True,explicit_ROOT_grant_required=True))
 print(json.dumps(dict(passed=True,native_run=False,bindings=len(bindings),callbacks=count,readiness_sha256=sha(out/'readiness.json'),command_sha256=sha(out/'command.json'))))
if __name__=='__main__':main()
