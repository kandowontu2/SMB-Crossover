"""Prepare one UNRUN4285 natural pipe profile; no emulator outcome/state writes."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
ROOT=Path(__file__).resolve().parents[2]
SHA='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','parent-profile','composition-ready','parser-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(a.candidate/'candidate.nes')==SHA
 assert sha(a.composition_ready)=='9609d87ad0545251fd19408baa6994ce09cd788f79f734ae336c1983e80d7749'
 z=json.loads((a.parent_profile/'preparation.json').read_text());old=Path(z['script']);assert sha(old)==z['script_sha256']
 c=json.loads(old.with_name('config.json').read_text());b=scoped_load(a.candidate/'candidate.nes')
 out=a.output/'area/baseline-early';out.mkdir(parents=True);controller=a.output/'area/controller';shutil.copytree(a.parent_profile/'controller',controller)
 harness=controller/'harness.lua';text=harness.read_text();harness.write_text(text.replace((a.parent_profile/'controller').as_posix(),controller.as_posix()))
 policy=controller/'policy.lua';policy.write_text(policy.read_text().replace((a.parent_profile/'controller').as_posix(),controller.as_posix()))
 for family,count in [('body_sources',131),('death_sources',13)]:
  assert len(c[family])==count
  for key,s in c[family].items():
   assert key==str(s['bank'])+':'+str(s['pointer']);at=16+s['bank']*8192+s['pointer']%8192
   assert list(b['raw'][at:at+len(s['bytes'])])==s['bytes']
 for family in ['hooks','hud_hooks','lifecycle_hooks']:
  for name,h in c[family].items():
   at=16+h['bank']*8192+h['address']%8192;assert list(b['raw'][at:at+len(h['bytes'])])==h['bytes'],name
 c.update(ROM_sha256=SHA,output=out.as_posix()+'/',limit=2600,capture_end=2600,hud_capture_end=2600,
          lifecycle=dict(kind='area',source_only=True,natural_controls=True,area_pending_Buffer2_overlap_unproved=True))
 rc=dict(name='octopus',slot=17,character=18,variant=1,variantSymbol='VvVariant',menuName='OCTOPUS',mapper='mmc5',behavior='easy',
         limit=18000,out=out.as_posix()+'/',record=False,allowDeaths=False,segmented=False,capture=0,
         policy=policy.as_posix(),replay=None,policyAllModes=True,lifecycleMenu=False)
 names=['parodius_visibility_area_controller_v3.lua','parodius_visibility_hud_transition_v3.lua',
        'parodius_visibility_hud_scroll_native_v2.lua','parodius_visibility_hud_native_v1.lua',
        'parodius_visibility_hud_static_observer_v2.lua','parodius_visibility_hud_lifecycle_bridge_v4.lua',
        'parodius_visibility_hud_lease_native_v2.lua']
 layers=[(ROOT/'tools/audit'/n).read_text()for n in names]
 # Only this additional finalizer slot moves ahead of the existing native
 # stop. Original five registration/body ordering stays unchanged.
 early='emu.addEventCallback(function()PARODIUS_HUD_LEASE_FINISH()end,emu.eventType.endFrame)\n'
 script=out/'run.lua';text='PARODIUS_VISIBILITY='+lua(c)+'\nROSTER_CONFIG='+lua(rc)+'\n'+'\n'.join(layers[:4])+ '\n'+early+'\n'.join(layers[4:])+ '\ndofile('+lua(harness.as_posix())+')\nPARODIUS_STATIC_INSTALL_RETURNS()\n'
 assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',text)
 script.write_text(text,encoding='utf-8');(out/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(text)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(a.candidate/('candidate'+ext),out/('candidate'+ext))
 dependencies=dict(z['dependencies']);dependencies.update({str(f.resolve()):sha(f)for f in [Path(__file__),a.composition_ready]+[ROOT/'tools/audit'/n for n in names]})
 snapshot=a.output/'area/dependency-snapshots';snapshot.mkdir()
 for name,h in dependencies.items():
  f=Path(name);assert sha(f)==h
  if f.suffix in ['.lua','.py']:shutil.copy2(f,snapshot/f.name)
 q=dict(prepared=True,native_passed=False,native_granted=False,ROM_sha256=SHA,mode=0,variant=1,kind='area',limit=2600,
        script=str(script.resolve()),script_sha256=sha(script),dependencies=dependencies,
        controller={f.name:sha(f)for f in controller.iterdir()if f.is_file()},
        composition_ready_sha256=sha(a.composition_ready),parent_preparation_sha256=sha(a.parent_profile/'preparation.json'),
        body_records=131,death_records=13,all_actual_hook_bytes_exact=True,
        input_mode='Cold real selection, then new ordinary-button adaptive target-ahead/align/nativeDown controller. No staged native actor, queue, resources, RNG, position or outcome writes.',
        scope='SOURCE-ONLY UNRUN2600 actualEasy0Oct1 area fixture. Same strict five guards; controller-only transition delta and extra actual HUD-pair check with corrected pre-stop finalization. Actual loaded-area change/nativepipe/45freshupdates/nonemptyBuffer2pendinghold/catchup all remain required; absent natural overlap is a coverage failure.')
 (a.output/'area/preparation.json').write_text(json.dumps(q,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(script_sha256=q['script_sha256'],preparation_sha256=sha(a.output/'area/preparation.json'),dependencies=len(dependencies)),indent=2))


if __name__=='__main__':main()
