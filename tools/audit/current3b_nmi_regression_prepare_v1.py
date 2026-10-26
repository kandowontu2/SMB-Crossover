"""PREPARE ONLY: exact qualified menu1800 and Hard1F240 on combined3b."""
from pathlib import Path
import argparse, copy, hashlib, json, re, shutil, subprocess, sys
from final_roll_items_prepare import lua as menu_lua
from observe_chip_committed_write import lua as hard_lua
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_audio_fallback_oc import qualified
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
FINAL='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
OLD_MENU=D/'parodius-menu-clean731-preparation-v1'
OLD_HARD=D/'root-clean731-hard1f-v1/fixture'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,z):assert not p.exists(),p;p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();P=a.candidate;O=a.output;O.mkdir(parents=True,exist_ok=False)
 ROM=P/'candidate.nes';assert sha(ROM)==FINAL
 source_ready=P/'ROOT-source-readiness.json';assert sha(source_ready)=='a332aec91cb2b16f8064c2423b2e0f3d5bbc9603325c0e06e4f0965d0386c220';assert get(source_ready)['passed']
 source=get(P/'source-manifest.json');assert len(source)==869 and all(sha(P/'source'/n)==h for n,h in source.items())
 b=scoped_load(ROM);labels=qualified(ROM)
 oldmenu=get(OLD_MENU/'menu/preparation.json');script=Path(oldmenu['script']);assert sha(script)==oldmenu['script_sha256']=='df20d7da9e8cd5c631018144fe561caf5ed08891866c4aab0c66a18869582094'
 for f,h in oldmenu['dependencies'].items():assert sha(f)==h,f
 c=get(script.with_name('config.json'));before=copy.deepcopy(c);changes=[]
 assert(c['mode'],c['variant'],c['character'],c['limit'])==(0,1,18,1800)
 for family in ['hooks','hud_hooks','lifecycle_hooks']:
  for name,h in c[family].items():
   old=copy.deepcopy(h)
   if name in ['NmiReturn','IrqReturn']:
    proc='NonMaskableInterrupt'if name=='NmiReturn'else'IrqScrollSplit';pc=address(b,proc)+int(b['syms'][proc]['size'],0)-1;off=location(b,proc)+pc-address(b,proc)
   else:pc=address(b,name);off=location(b,name)
   h.update(address=pc,bank=(off-16)//8192,bytes=list(b['raw'][off:off+len(h['bytes'])]))
   if h!=old:changes.append(dict(family=family,name=name,before=old,after=h))
 for family in ['ram','profile_ram','hud_ram','lifecycle_ram']:
  assert all(address(b,n)==v for n,v in c[family].items()),family
 for record in c['body_sources'].values():
  off=16+record['bank']*8192+(record['pointer']&8191);assert list(b['raw'][off:off+len(record['bytes'])])==record['bytes']
 assert len(c['body_sources'])==131
 for n in ['PnHudCells']:
  off=location(b,n);data=list(b['raw'][off:off+84]);assert c['hud_labels']=={str(i):data[(i-1)*28:i*28]for i in range(1,4)}
 assert(P/'source/chr/characters/parodius-hud.chr').read_bytes()==(D/'root-chip-hud-composed-v1/source/chr/characters/parodius-hud.chr').read_bytes()
 for h in c['early_timing']['hooks'].values():
  off=16+h['bank']*8192+(h['pc']&8191);assert list(b['raw'][off:off+len(h['bytes'])])==h['bytes']
 assert all(address(b,n)==v for n,v in c['early_timing']['ram'].items())
 dma=c['dma_protocol'];off=location(b,'PostDmaMaskEnable');assert dma['next_pc']==address(b,'PostDmaMaskEnable')==0xe005 and dma['complete_pc']==0xe008
 assert list(b['raw'][off:off+8])==dma['next_bytes']==[173,122,7,141,1,32,162,1]
 # Keep the full historical observer/controller chunk byte-exact modulo paths and the first metadata line.
 menu=O/'menu';out=menu/'baseline-early';out.mkdir(parents=True);controller=menu/'controller';shutil.copytree(OLD_MENU/'menu/controller',controller)
 for f in controller.glob('*.lua'):
  old=f.read_text();new=old.replace(OLD_MENU.as_posix(),O.as_posix());f.write_text(new,encoding='utf-8',newline='\n');assert f.read_text().replace(O.as_posix(),OLD_MENU.as_posix())==old
 original=script.read_text();tail=original.split('\n',1)[1];newtail=tail.replace(OLD_MENU.as_posix(),O.as_posix());assert newtail.replace(O.as_posix(),OLD_MENU.as_posix())==tail
 c.update(ROM_sha256=FINAL,output=out.as_posix()+'/');text='PARODIUS_VISIBILITY='+menu_lua(c)+'\n'+newtail
 assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',text)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copyfile(P/('candidate'+ext),out/('candidate'+ext))
 (out/'run.lua').write_text(text,encoding='utf-8',newline='\n');put(out/'config.json',c)
 deps=dict(oldmenu['dependencies']);deps.update({str(Path(__file__).resolve()):sha(__file__),str(source_ready):sha(source_ready)})
 menu_prep=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=FINAL,kind='menu',mode=0,variant=1,limit=1800,script=str((out/'run.lua').resolve()),script_sha256=sha(out/'run.lua'),dependencies=deps,original_script=str(script),original_script_sha256=sha(script),parent_preparation_sha256=sha(OLD_MENU/'menu/preparation.json'),all_original_controller_tail_and_six_guard_bodies_exact=True,no_emulated_writes=True,changed_hook_metadata=changes,config_deltas=[n for n in c if c[n]!=before.get(n)],source_note='Combined3b intentionally includes source-qualified9ee robot-shot code; this is not an original3cee-shot-source assertion. Menu controller and all art/131body/5376HUD guards remain unchanged.')
 put(menu/'preparation.json',menu_prep)
 # Hard1F preserves the entire qualified731 body including its exact E008 protocol.
 hard=O/'hard1f';hard.mkdir();oldcfg=get(OLD_HARD/'configuration.json');cfg=copy.deepcopy(oldcfg);hook_changes=[]
 assert cfg['mode']==1 and cfg['expected_cue']==6 and cfg['cases']==[{'name':'pressure-fireball-hard','profile':'pressure','mode':1,'sub':0,'event':31,'kind':'fireball','updates':240}]
 for name,h in cfg['hooks'].items():
  was=copy.deepcopy(h)
  if name=='NmiReturn':
   off=16+h['physical_bank']*8192+(h['address']&8191);assert h['bytes']==[64]and b['raw'][off]==64;continue
  proc,sep,leaf=name.partition('::');pc=labels[(proc,leaf)]if sep else address(b,name);off=location(b,proc)+pc-address(b,proc)
  assert(off-16)//8192==h['physical_bank'];h['address']=pc;h['bytes']=list(b['raw'][off:off+3])
  if h!=was:hook_changes.append(dict(name=name,before=was,after=h))
 assert all(address(b,n)==v for n,v in cfg['ram'].items())
 for writer in cfg['queue_writers'].values():
  off=16+writer['bank']*8192+(writer['pc']&8191);assert list(b['raw'][off:off+len(writer['opcode'])])==writer['opcode']
 for sample in cfg['samples']:
  off=16+sample['bank']*8192+(sample['address']&8191);assert list(b['raw'][off:off+len(sample['payload'])])==sample['payload']
 assert cfg['dma_completion_guard']=={'pc':0xe005,'bank':127,'bytes':[173,122,7,141,1,32,162,1]}
 oldtext=(OLD_HARD/'run.lua').read_text();assert sha(OLD_HARD/'run.lua')=='b5fcbd454b2e1c0041f044682df8f896fbe5beca6a97e4a6275b47bdde036fa6'
 oldbody=oldtext.split('\n',1)[1];body=oldbody.replace(OLD_HARD.as_posix(),hard.as_posix());assert body.replace(hard.as_posix(),OLD_HARD.as_posix())==oldbody
 hardscript=hard/'run.lua';hardscript.write_text('CV3_REMAINING_NATIVE_CONFIG='+hard_lua(cfg)+'\n'+body,encoding='utf-8',newline='\n');put(hard/'configuration.json',cfg);shutil.copyfile(ROM.with_suffix('.lbl'),hard/'candidate.lbl')
 put(hard/'preparation.json',dict(prepared=True,native_executed=False,ROM=str(ROM),ROM_sha256=FINAL,script=str(hardscript),script_sha256=sha(hardscript),configuration_sha256=sha(hard/'configuration.json'),same_input_baseline=str(OLD_HARD),original_script_sha256=sha(OLD_HARD/'run.lua'),controller_seed_workload_exact=True,all_semantic_count_hardware_timing_guards_exact=True,changed_hook_metadata=hook_changes,scope='Same qualified731 Hard1F240 pressure control, exact controller/mechanics/guards/caps; metadata only, no native grant/run.'))
 depsroot=D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
 commands=[('menu-static','parodius_visibility_menu59_static_v1.py',['--preparation',str(O)]),('menu-DMA-mock','parodius_visibility_menub0_dma_mock_v1.py',['--preparation',str(O)]),('menu-timing-mock','parodius_visibility_menu59_timing_mock_v1.py',['--preparation',str(O)]),('hard-startup','cv3_remaining_sfx_queue_native_startup_v2.py',['--fixture',str(hard)]),('hard-observer','cv3_remaining_sfx_legacy_wrapper_observer_v1.py',['--fixture',str(hard)])]
 controls=[]
 for name,tool,args in commands:
  output=O/name;command=[sys.executable,'-B',str(ROOT/'tools/audit'/tool),*args,'--lua-root',str(depsroot),'--output',str(output)];r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(O/(name+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8')
  assert r.returncode==0,(name,r.stdout[-1500:],r.stderr[-1500:]);assert get(output/'proof.json')['passed'];controls.append(dict(name=name,command=command,proof_sha256=sha(output/'proof.json')))
 put(O/'preparation.json',dict(passed=True,source_only=True,native_run=False,native_grant=False,ROM_sha256=FINAL,ROM=str(ROM),source_ready=str(source_ready),source_readiness_sha256=sha(source_ready),menu_preparation_sha256=sha(menu/'preparation.json'),hard_preparation_sha256=sha(hard/'preparation.json'),menu_tail_controller_six_guards_timing_exact=True,hard_tail_controller_mechanics_source_hardware_cadence_exact=True,menu_metadata_deltas=menu_prep['config_deltas'],menu_hook_changes=changes,hard_hook_changes=hook_changes,controls=controls,baseline_menu_proof=str(D/'parodius-menu-clean731-native-final-v1/proof.json'),baseline_Hard1F_proof=str(OLD_HARD/'proof.json'),baseline_menu_completed_full256_DMAs=1300,baseline_Hard1F_total_draws=168,scope='ONLY unrun same-input menu1800 and Hard1F240 regression preparation on3b. No new ROM/source/settings, native grant or current-hash outcome.'))
 print(json.dumps(dict(passed=True,preparation=str(O/'preparation.json'),sha256=sha(O/'preparation.json'),menu_script=sha(out/'run.lua'),hard_script=sha(hardscript),menu_hook_changes=changes,hard_hook_changes=hook_changes),indent=2))
if __name__=='__main__':main()
