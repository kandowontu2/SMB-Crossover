"""Prepare HUD-only df515 lifecycle controls; no native launch."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
SHA='df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BRIDGE=(ROOT/'tools/audit/parodius_visibility_hud_lifecycle_bridge_v3.lua').read_text()

def records(bundle,manifest):
 sources={};aliases={}
 for pool in manifest['pools']:
  variant=pool['variant'];base=location(bundle,'PnPool'+str(pool['index'])+'Lo');hi=location(bundle,'PnPool'+str(pool['index'])+'Hi');indices=location(bundle,'PnFrameIndexV'+str(variant));bank=(base-16)//8192
  for frame,parts in pool['records'].items():
   index=bundle['raw'][indices+int(frame)];assert index;ptr=bundle['raw'][base+index]+256*bundle['raw'][hi+index];key=f'{bank}:{ptr}';at=16+bank*8192+ptr%8192;data=bytes([len(parts)*4]+[v for p in parts for v in p]);assert bundle['raw'][at:at+len(data)]==data
   ref=dict(pool=pool['index'],variant=variant,phase=pool['phase'],frame=int(frame),body=int(frame)in pool['body_frames']);aliases.setdefault(key,[]).append(ref)
   if ref['body']:
    label=next((n for n in bundle['syms']if re.fullmatch(r'PnRecordV\d+N\d+',n)and address(bundle,n)==ptr and(location(bundle,n)-16)//8192==bank),None);assert label;sources[key]=dict(bank=bank,pointer=ptr,label=label,parts=parts,bytes=list(data),refs=[])
 for key,v in sources.items():v['refs']=aliases[key];assert all(ref['body']for ref in aliases[key]),key
 return sources,aliases


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--combined',type=Path,required=True);p.add_argument('--parent-profile',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--parser-root',type=Path,required=True);a=p.parse_args();assert sha(a.combined/'candidate.nes')==SHA;a.output.mkdir(parents=True,exist_ok=False)
 frozen=a.output/'frozen';frozen.mkdir()
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(a.combined/('candidate'+ext),frozen/('candidate'+ext))
 for name in ['src','inc','audio','chr','reference/parodius-nes']:
  shutil.copytree(a.combined/'source'/name,frozen/'source'/name)
 for name in ['build_options.ini','smb1base.cfg','smb1base-mmc5-expanded.cfg','tools/reference/prepare_parodius_art.py','tools/reference/parodius_sprite_packing.py']:
  target=frozen/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a.combined/'source'/name,target)
 shutil.copy2(a.combined/'proof.json',frozen/'composition-proof.json');ledger={f.relative_to(frozen).as_posix():sha(f)for f in frozen.rglob('*')if f.is_file()};(a.output/'frozen-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
 bundle=scoped_load(frozen/'candidate.nes');manifest=json.loads((frozen/'source/reference/parodius-nes/art/packed/manifest.json').read_text());sources,aliases=records(bundle,manifest);assert len(sources)==131
 (a.output/'body-aliases.json').write_text(json.dumps(dict(all_records=aliases,body_sources=sources,mixed_body_nonbody_aliases=[]),indent=2)+'\n',encoding='utf-8')
 oldprep=json.loads((a.parent_profile/'preparation.json').read_text());oldrun=Path(oldprep['script']).parent;oldcfg=json.loads((oldrun/'config.json').read_text());assert oldcfg['mode']==0 and oldcfg['variant']==1
 static=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua';hud=ROOT/'tools/audit/parodius_visibility_hud_native_v1.lua';scroll=ROOT/'tools/audit/parodius_visibility_hud_scroll_native_v2.lua';module=ROOT/'tools/audit/parodius_visibility_hud_lifecycle_v3.lua';profiles=[]
 sys.path.insert(0,str(a.parser_root));from luaparser import ast
 for kind,limit,start in [('menu',1800,150)]:
  packet=a.output/kind;packet.mkdir();out=packet/'baseline-early';out.mkdir();controller=packet/'controller';controller.mkdir();oldcontroller=a.parent_profile/'controller'
  for f in oldcontroller.iterdir():
   if f.is_file():shutil.copy2(f,controller/f.name)
  policy=controller/'policy.lua';text=policy.read_text().replace(oldcontroller.as_posix(),controller.as_posix());policy.write_text(text,encoding='utf-8')
  harness=controller/'harness.lua';text=harness.read_text();assert text.count('local function menu()')==1
  if kind!='crowd':
   text=text.replace("local choose=assert(dofile(cfg.policy),'Policy must return function(context)')", "local baseChoose=assert(dofile(cfg.policy),'Policy must return function(context)')\nlocal choose=function(c)local b=PARODIUS_LIFECYCLE_POLICY(c);if b~=nil then return b end;return baseChoose(c)end")
   text=text.replace('local function menu()', 'local function menu()\n if cfg.lifecycleMenu then local b=PARODIUS_LIFECYCLE_MENU(context());if b~=nil then return b end end')
   text=text.replace(" if selectionDone and r('OperMode')==3 then finish(false,'game over');return end", " if selectionDone and r('OperMode')==3 then finish(false,'unexpected game over during single-life fixture');return end")
   harness.write_text(text,encoding='utf-8')
  c=json.loads(json.dumps(oldcfg));c.update(ROM_sha256=SHA,output=out.as_posix()+'/',body_sources=sources,limit=limit,start_frame=start,capture_start=start,capture_end=limit,hud_capture_start=start,hud_capture_end=limit,lifecycle=dict(kind=kind,source_only=True,natural_controls=True,area_pending_Buffer2_overlap_unproved=True if kind=='area'else False))
  names=['SelectedCharacter','VvVariant','CrossoverBehaviorVersion','OperMode','OperMode_Task','GameEngineSubroutine','NumberofLives','AreaPointer','InvHudActive','InvHudPhysical','X5HudChrUpper','VvHudDirty','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','VRAM_Buffer_AddrCtrl','SavedJoypadBits','CrossoverMenuState','CrossoverMenuIndex'];c['lifecycle_ram']={n:address(bundle,n)for n in names};c['lifecycle_hooks']={}
  for n in ['VvReset','VvDeathStart','PnHudNewLife','KillPlayer','GameLoop','SamusFreezeUpdateScreen','NmiReturn']:
   if n=='NmiReturn':c['lifecycle_hooks'][n]=c['hooks'][n]
   else:at=location(bundle,n);c['lifecycle_hooks'][n]=dict(address=address(bundle,n),bank=(at-16)//8192,bytes=list(bundle['raw'][at:at+3]))
  for n in ['MoveAllSpritesOffscreen','X5PortraitRender']:
   at=location(bundle,n);c['hooks'][n]=dict(address=address(bundle,n),bank=(at-16)//8192,bytes=list(bundle['raw'][at:at+3]))
  for family in ['hooks','hud_hooks']:
   for n,h in c[family].items():at=16+h['bank']*8192+h['address']%8192;assert list(bundle['raw'][at:at+len(h['bytes'])])==h['bytes'],n
  for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(frozen/('candidate'+ext),out/('candidate'+ext))
  cfg=dict(name='octopus',slot=17,character=18,variant=1,variantSymbol='VvVariant',menuName='OCTOPUS',mapper='mmc5',behavior='easy',limit=18000,out=out.as_posix()+'/',record=False,allowDeaths=kind=='death',segmented=False,capture=0,policy=(controller/'policy.lua').as_posix(),replay=(controller/'inputs.csv').as_posix()if kind=='crowd'else None,policyAllModes=kind!='crowd',lifecycleMenu=kind=='menu')
  script=out/'run.lua';script.write_text('PARODIUS_VISIBILITY='+lua(c)+'\nROSTER_CONFIG='+lua(cfg)+'\n'+module.read_text()+'\n'+scroll.read_text()+'\n'+hud.read_text()+'\n'+static.read_text()+'\n'+BRIDGE+'\ndofile('+lua((controller/'harness.lua').as_posix())+')\nPARODIUS_STATIC_INSTALL_RETURNS()\n',encoding='utf-8');(out/'config.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8');ast.parse(script.read_text())
  assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',script.read_text()),'No staged emulator writes'
  deps={str(f.resolve()):sha(f)for f in [Path(__file__),static,hud,scroll,module,ROOT/'tools/audit/parodius_visibility_hud_lifecycle_bridge_v3.lua',ROOT/'tools/audit/parodius_visibility_run.py',ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/run_mesen.py']};snap=packet/'dependency-snapshots';snap.mkdir()
  for n,digest in deps.items():shutil.copy2(n,snap/Path(n).name);assert sha(snap/Path(n).name)==digest
  q=dict(prepared=True,native_passed=False,goal_complete=False,ROM_sha256=SHA,mode=0,variant=1,script=str(script),script_sha256=sha(script),observer_sha256=sha(static),dependencies=deps,controller={f.name:sha(f)for f in controller.iterdir()if f.is_file()},scope='SOURCE PREPARATION ONLY. '+kind+' fixture; strict original guards/static dispatcher retained, literal original body records, HUD-only df515, natural buttons only. Lifecycle init-owner/retained-current-epoch bridge is a new observation proposal requiring ROOT review; natural completion and area Buffer2/pending overlap are not yet qualified.',input_mode='exact frozen historical OctEasy input stream'if kind=='crowd'else'new legal adaptive lifecycle controller, UNRUN',record_aliases_sha256=sha(a.output/'body-aliases.json'),frozen_ledger_sha256=sha(a.output/'frozen-ledger.json'))
  (packet/'preparation.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');profiles.append(dict(kind=kind,limit=limit,packet=str(packet),preparation_sha256=sha(packet/'preparation.json'),script_sha256=sha(script)))
 proof=dict(prepared=True,native_run=False,native_granted=False,goal_complete=False,ROM_sha256=SHA,body_records=len(sources),all_record_aliases=len(aliases),mixed_body_nonbody_aliases=0,profiles=profiles,frozen_ledger_sha256=sha(a.output/'frozen-ledger.json'),body_aliases_sha256=sha(a.output/'body-aliases.json'),tool_sha256=sha(Path(__file__)),limits='Prepared Lua parses and actual compiled records/hooks match. No lifecycle reachability/coverage is claimed; no body-order proposal is included. Source-only review needed for init blank/portrait/draw generations and natural pending/Buffer2 overlap. Existing receipts unchanged; no native launch.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof,indent=2))

if __name__=='__main__':main()
