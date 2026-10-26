"""Metadata-only Bass galleries on exactfinal3b112 composition, NO launch."""
from pathlib import Path
import argparse,ast,hashlib,json,shutil,sys
from final_item_abilities_static_prepare_v2 import D,ROOT,core_tests,old_core
from final_inventory_bass731_ready_v1 import compiled_cpu
from final_item_abilities_current731_prepare_v1 import protocol,dma_mocks
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_run import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from parodius_visibility_hud_static_startup_v1 import MOCK
SHA='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
SOURCE_SHA='a332aec91cb2b16f8064c2423b2e0f3d5bbc9603325c0e06e4f0965d0386c220'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 source=D/'root-current-roster-composition-v1';receipt=source/'ROOT-source-readiness.json';assert sha(receipt)==SOURCE_SHA;sr=json.loads(receipt.read_text());assert sr['passed']and sr['source_only']and not sr['native_run']and sr['ROM_sha256']==SHA and sha(source/'candidate.nes')==SHA
 sm=source/'source-manifest.json';assert sha(sm)==sr['source_manifest_sha256'];files={receipt,sm,source/'ROOT-bindings.json'}
 for rel,h in json.loads(sm.read_text()).items():f=source/'source'/rel;assert sha(f)==h;files.add(f)
 assert len(json.loads(sm.read_text()))==869
 for name,z in json.loads((source/'ROOT-bindings.json').read_text()).items():f=Path(name);assert sha(f)==z['sha256'];files.add(f)
 for z in sr['component_records']:assert sha(z['path'])==z['sha256'];files.add(Path(z['path']))
 old=D/'current30a1-bass-gallery-ready-v1';diag=D/'current30a1-bass-diagnostic945-ready-v1';verify_manifest(old/'manifest.json');verify_manifest(diag/'manifest.json');files.update([old/'proof.json',old/'manifest.json',diag/'proof.json',diag/'manifest.json'])
 oldcfg=json.loads((diag/'native/config.json').read_text());oldscript=(diag/'native/run.lua').read_text();oldprefix='FINAL_ITEM_PROGRESSIVE='+lua(oldcfg)+'\n';assert oldscript.startswith(oldprefix);body=oldscript[len(oldprefix):]
 b=scoped_load(source/'candidate.nes');profiles=[];control=[];sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 def hook(n,delta=0,length=3):
  pos=location(b,n)+delta;return dict(address=address(b,n)+delta,physical_bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+length]))
 def record_exact(r):
  off=16+r['bank']*8192+r['address']%8192;assert list(b['raw'][off:off+len(r['bytes'])])==r['bytes']
 for mode in[0,1]:
  name='bass-'+('hard'if mode else'easy');oldpath=old/'profiles'/name/'native';originalcfg=json.loads((oldpath/'config.json').read_text());originalscript=(oldpath/'run.lua').read_text();assert originalscript[len('FINAL_ITEM_PROGRESSIVE='+lua(originalcfg)+'\n'):]==body
  cfg=json.loads(json.dumps(oldcfg));cfg.update(hard=bool(mode),mode_value=mode,ROM_sha256=SHA)
  cfg['ram']={n:address(b,n)for n in cfg['ram']};cfg['diagnostic']['ram']={n:address(b,n)for n in cfg['diagnostic']['ram']}
  for key,h in cfg['hooks'].items():
   owner='GameLoop'if key=='finish'else'NonMaskableInterrupt'if key=='NmiReturn'else key;delta=int(b['syms'][owner]['size'],0)-1 if key in['finish','NmiReturn']else 0;cfg['hooks'][key]=hook(owner,delta,len(h['bytes']))
  for key,h in cfg['diagnostic']['hooks'].items():
   owner='NonMaskableInterrupt'if key=='NmiReturn'else'IrqScrollSplit'if key=='IrqReturn'else'PostDmaMaskEnable'if key=='completion'else key;delta=int(b['syms'][owner]['size'],0)-1 if key in['NmiReturn','IrqReturn']else 3 if key=='completion'else 0;cfg['diagnostic']['hooks'][key]=hook(owner,delta,len(h['bytes']))
  cfg['dma_protocol']=protocol(b);cfg['smc_fields']=[address(b,n)+1 for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
  pos=location(b,'IrqScrollSplit');cfg['irq_scroll_stores']=[address(b,'IrqScrollSplit')+i for i in range(int(b['syms']['IrqScrollSplit']['size'],0)-2)if b['raw'][pos+i:pos+i+3]==b'\x8d\x05\x20'];assert len(cfg['irq_scroll_stores'])==len(oldcfg['irq_scroll_stores'])
  for n in cfg['art']:cfg['art'][n]=dict(address=address(b,n),bank=(location(b,n)-16)//8192)
  for pair in cfg['effect_records']:
   for r in pair:record_exact(r)
  for n in['native_brick','native_chunk','buster_record']:record_exact(cfg[n])
  for q in cfg['cases']:
   idx=144+q['item'];ptr=b['raw'][location(b,'InvNameLo')+idx]+256*b['raw'][location(b,'InvNameHi')+idx];g=b['segs'][b['syms']['InvNameLo']['seg']];off=int(g['ooffs'],0)+ptr-int(g['start'],0);assert q['hud_name']==list(b['raw'][off:off+7])and q['source_cost']==b['raw'][location(b,'InvCosts')+idx]
   if q['item']:assert q['icon_bank']==b['raw'][location(b,'InvHudPhysicalBanks')+q['item']-1]
  assert cfg['diagnostic']['first_frame']==850 and cfg['diagnostic']['last_frame']==950
  script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+body;assert script.split('\n',1)[1]==oldscript.split('\n',1)[1]
  out=a.output/'profiles'/name/'native';out.mkdir(parents=True)
  for ext in['.nes','.dbg','.lbl','.map']:shutil.copy2(source/('candidate'+ext),out/('candidate'+ext))
  put(out/'config.json',cfg);(out/'run.lua').write_text(script,encoding='utf-8');shutil.copy2(oldpath/'inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua')
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;emu.write=function()error("Unexpected startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end')
  checks="\nentered=true;for _,f in ipairs({849,850,945,950,951})do local s=emu.getState();s['ppu.frameCount']=f;assert(dFocus()==(f>=850 and f<=950),'Literal focus predicate')end";rt.execute(script+checks);count=rt.eval('#callbacks');assert count==72 and rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')and rt.eval('#events[emu.eventType.endFrame]')==3
  indices=[i for i in range(1,count+1)if rt.eval(f'callbacks[{i}].kind==1 and callbacks[{i}].lo==0x2001')];assert len(indices)==2 and indices[0]<indices[1]
  rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
  profiles.append(dict(profile=name,mode_value=mode,plans=16,output=str(out),script_sha256=sha(out/'run.lua'),callbacks=count,maximum_launches=1,original_NMI_stack_bank_5SMC_APU_guards_sha256=sha(out/'inherited-NMI-stack-APU-guards.lua')))
  control.append(dict(profile=name,actual_compiled_metadata_fresh=True,entire_script_body_after_config_literal_exact=True,original_controller_caps_mechanics_defaultglyph_oracle_and_strictguards_exact=True,records_source_names_costs_exact=True,static_callbacks=count,raw_diagnostic_before_original_deadline=True,focus_models=[849,850,945,950,951]));files.update([oldpath/'run.lua',oldpath/'config.json',oldpath/'inherited-NMI-stack-APU-guards.lua'])
 cpu=compiled_cpu(b);put(a.output/'assembled-cpu-controls.json',dict(passed=True,ROM_sha256=SHA,cases=len(cpu),rows=cpu,limits='Fresh finalhash finite real effect/cost/pool/selection/damage consumers; no native timing/graphics/acquisition claim.'))
 returns=core_tests(LuaRuntime,old_core((ROOT/'tools/audit/final_item_abilities_native.lua').read_text()),(ROOT/'tools/audit/final_item_abilities_static_return_v1.lua').read_text());dma=dma_mocks(LuaRuntime,(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua').read_text(),dict(dma_protocol=protocol(b)))
 put(a.output/'source-controls.json',dict(passed=True,native_run=False,ROM_sha256=SHA,profiles=control,fresh_compiled_effect_controls=len(cpu),static_return_controls=returns,DMA_controls=dma,source_freeze_sha256=sha(receipt),component_records_retained_as_components=sr['component_records'],limits='Finalcombinedhash freshsource/static only; wholeNMI/source equivalence scopes are in ROOTreceipt. No retagged7aad/9eenative/fullcoverage verdict.'))
 env=json.loads((diag/'environment.json').read_text());runtime=Path(env['emulator']).parent;isolated=a.output/'emulator';isolated.mkdir()
 for f in runtime.iterdir():
  if f.is_file():shutil.copy2(f,isolated/f.name);files.add(f)
 user=Path('C:/Mesen2/settings.json');env.update(emulator=str(isolated/'Mesen.exe'),emulator_sha256=sha(isolated/'Mesen.exe'),core_sha256=sha(isolated/'MesenCore.dll'),worker_settings_sha256=sha(isolated/'settings.json'),user_context_sha256=sha(user));s=json.loads((isolated/'settings.json').read_bytes().decode('utf-8-sig'));assert s['Nes']==env['Nes']and s['Emulation']==env['Emulation'];put(a.output/'environment.json',env);files.add(user)
 for name in['plans.json','seed-policy.json']:shutil.copy2(old/name,a.output/name);files.add(old/name)
 commands={q['profile']:'python -B tools/audit/final_inventory_successor_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --profile '+q['profile']+' --native-grant'for q in profiles};put(a.output/'commands.json',commands)
 files.update(f for f in a.output.rglob('*')if f.is_file());roots=[Path(__file__),ROOT/'tools/audit/final_inventory_successor_gallery_run_v1.py'];seen=set()
 while roots:
  f=roots.pop()
  if f in seen:continue
  seen.add(f);files.add(f)
  for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
   mods=[node.module]if isinstance(node,ast.ImportFrom)else[q.name for q in node.names]if isinstance(node,ast.Import)else[]
   for n in mods:
    if n:
     dep=ROOT/'tools/audit'/(n.split('.')[0]+'.py')
     if dep.is_file():roots.append(dep)
 for name in['final_inventory_bass731_native_v1.lua','final_item_matrix_progressive.lua','final_item_abilities_static_return_v1.lua','final_item_abilities_dma731_v1.lua','final_item_abilities_pit731_ppu_v1.lua','final_item_abilities_failure.lua','final_inventory_meter_diagnostic_v1.lua','final_item_abilities_native.lua']:files.add(ROOT/'tools/audit'/name)
 files.update([Path(sys.executable),Path(sys.modules[LuaRuntime.__module__].__file__)])
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]))
 proof=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profiles=profiles,plans=32,source_freeze_sha256=sha(receipt),source_controls_sha256=sha(a.output/'source-controls.json'),manifest_sha256=sha(a.output/'manifest.json'),manifest_bindings=len(files),maximum_owned_workers=1,maximum_launches_per_profile=1,automatic_next_profile=False,retries=False,environment=env,commands=commands,limits=['B-only complete native-boundary resource/actor/arena seeds, no acquisition.','Same entire script body/controller/caps/strictguards/defaultglyph/850..950diagnostic after configuration; actual metadata/source/ROM refreshed.','Easyfirst requires grant; Hardungranted until Easyresultreview. No retries/auto advance.','ComponentsC7aad/A9ee retain original hashes/scopes, not finalnative claims.','PhysicalfullPPU/effect/HUDpixel/cadence/all16plan finalhash outcomes remain pending; all oldFALSEs immutable.','Primary/default641/source/settings/Git unchanged by this preparer.'])
 put(a.output/'proof.json',proof);verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),commands=commands),indent=2))
if __name__=='__main__':main()
