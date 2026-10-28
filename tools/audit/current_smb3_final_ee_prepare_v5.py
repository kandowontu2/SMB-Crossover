"""Currentee actual source campaigns plus stable-statue image-only successor."""
from pathlib import Path
import inspect,json,re,sys
R=Path(__file__).resolve().parents[2];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
import current_smb3_powerups_prepare_v1 as prior
from current_smb3_hammer_aim_prepare_v4 import SOURCE_OLD,SOURCE_NEW
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import sha,lua
ROM=B/'roster-20261028-fixes.nes';EXPECTED='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def main():
 assert sha(ROM)==EXPECTED;b=scoped_load(ROM);oldrom=B/'current_smb3_timer.nes';old=scoped_load(oldrom)
 assert sha(oldrom)=='b01dcf080e07f5c7526fbf5ed177fe2131c6d5fcbbab5eed8773a66f6a34171d'
 raw,orig=ROM.read_bytes(),oldrom.read_bytes()
 for bank in[90,91,92,94,125,126,127]:assert raw[16+bank*8192:16+(bank+1)*8192]==orig[16+bank*8192:16+(bank+1)*8192],('Actual relevant whole bank',bank)
 assert raw[16+128*8192:]==orig[16+128*8192:],'AllCHR unchanged'
 frame=address(b,'M3Native::PF_STATUE');assert frame==30
 oldfixture=R/'tests/current-smb3-powerups-v4.lua';fixture=R/'tests/current-smb3-powerups-v5.lua';assert not fixture.exists();text=oldfixture.read_text()
 before="(phase=='statue'and nr('Statue')~=0 and rec.protected)"
 after="(phase=='statue'and nr('Statue')~=0 and rec.protected and r('M3Poof')==0 and nr('Frame')==C.statue_frame)"
 assert text.count(before)==1;altered=text.replace(before,after)
 oldtake=" if want then imagePending={name=t.picture,source=mainImage(),record=rec,wall=wall,update=updates,form=r('M3Form'),render=rec.render}end"
 newtake=" if want then if phase=='statue'then rec.statue_picture={update=updates,poof=r('M3Poof'),native_frame=nr('Frame'),render_frame=r('M3RenderFrame'),object_metasprite=r('ObjectMetasprite')}end;imagePending={name=t.picture,source=mainImage(),record=rec,wall=wall,update=updates,form=r('M3Form'),render=rec.render}end"
 assert altered.count(oldtake)==1;altered=altered.replace(oldtake,newtake)
 assert altered.replace(newtake,oldtake).replace(after,before)==text
 marker='-- All callback registration is startup-static. No callback adds/removes callbacks.';end="hook('DmaComplete',function()\n if not imagePending"
 assert text[text.index(marker):text.index(end)]==altered[altered.index(marker):altered.index(end)],'Literal unchanged all hardware guards'
 fixture.write_text(altered,newline='\n')
 src=inspect.getsource(prior.campaign);assert src.count(SOURCE_OLD)==1;src=src.replace(SOURCE_OLD,SOURCE_NEW)
 anchor="                if kind=='flight'and age<150"
 check="""                if kind=='statue'and q.get(N['Statue'])and q.get('M3Poof')==0 and q.get(N['Frame'])==STATUE_FRAME:
                    assert q.get('M3RenderFrame')==STATUE_FRAME and q.get('ObjectMetasprite')!=0,'Actual stable statue body published'
                    rec.setdefault('stable_statue_picture_admission',dict(age=age,poof=q.get('M3Poof'),native_frame=q.get(N['Frame']),render_frame=q.get('M3RenderFrame'),object_metasprite=q.get('ObjectMetasprite')))
"""
 assert src.count(anchor)==1;src=src.replace(anchor,check+anchor)
 original_return="            rec.update(updates=age,form_after="
 assert src.count(original_return)==1;src=src.replace(original_return,"            if kind=='statue':assert 'stable_statue_picture_admission'in rec\n"+original_return)
 env=dict(vars(prior));env['STATUE_FRAME']=frame;exec(compile(src,str(Path(__file__))+'::actual_ee_source','exec'),env)
 campaigns=[]
 for mode in[0,1]:
  for var in[0,1]:
   c=env['campaign'](b,mode,var);campaigns.append(c);print(json.dumps(dict(source_PASS=True,mode=mode,variant=var,cases=c['cases'],Main=c['complete_GameLoop_calls'],statue=next(r['stable_statue_picture_admission']for r in c['records']if r['kind']=='statue'))),flush=True)
 proof=B/'current_smb3_final_ee_v5_source.json';assert not proof.exists()
 put(proof,dict(passed=True,source_CPU_only=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,PF_STATUE=dict(value=frame,symbol='M3Native::PF_STATUE',origin='Actual scoped linked DBG equate + originalNES source constant'),
  cases=24,modes=[0,1],variants=[0,1],complete_GameLoop_calls=sum(c['complete_GameLoop_calls']for c in campaigns),campaigns=campaigns,
  image_change='Only native statue picture admission: M3Poof0/native PF_STATUE. Added actual recorded native/render frame+ObjectMetasprite values; no extra callbacks, game/scene/input/resource/assertion/cap changes.',
  inheritance='Whole actual relevant SMB3 logic/native/art banks90/91/92/94, fixed125/126/127 and entireCHR match native-tested b01. Old isolated injury/IRQ/foreign receipts retain original ROM scope; these four complete Main+NMI campaigns are NEW on exactee.',
  bindings={str(p):sha(p)for p in[Path(__file__),oldfixture,fixture,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),oldrom,oldrom.with_suffix('.dbg'),R/'tools/audit/current_smb3_powerups_prepare_v1.py',R/'tools/audit/current_smb3_hammer_aim_prepare_v4.py',R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py']}))
 outputs=[]
 for identity,var in[('mario3',0),('luigi3',1)]:
  parent=B/('current-smb3-timer-'+identity+'-hard-items-v4');rp=parent/'prepared-not-run.json';oldready=json.loads(rp.read_text());assert all(sha(Path(f['path']))==f['sha256']for f in oldready['bindings'])
  out=B/('current-ee1152-'+identity+'-hard-items-v5');assert not out.exists();out.mkdir()
  cfg=json.loads((parent/'config.json').read_text());assert cfg['variant']==var and cfg['mode']==1;cfg.update(ROM_sha256=EXPECTED,statue_frame=frame)
  for n,v in cfg['ram'].items():assert address(b,n)==v,('ActualEE RAM',n)
  refs=set(re.findall(r"(?<![A-Za-z_])[rw]\('([A-Za-z_][A-Za-z_0-9:]*)'",altered))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',altered))
  for n in refs:cfg['ram'][n]=address(b,n)
  for name,h in cfg['hooks'].items():
   symbol=h['source_symbol'];delta=h['source_delta'];assert address(b,symbol)+delta==h['pc'];bank=(location(b,symbol)-16)//8192;assert bank in h['banks']
   for k in h['banks']:assert list(raw[16+k*8192+(h['pc']&8191):16+k*8192+(h['pc']&8191)+len(h['bytes'])])==h['bytes'],('ActualEE hook bytes/copy',name,k)
  put(out/'config.json',cfg);put(out/'source-controls.json',dict(passed=True,native_run=False,source_CPU_only=True,ROM_sha256=EXPECTED,proof=str(proof),sha256=sha(proof),complete_GameLoop_calls=sum(c['complete_GameLoop_calls']for c in campaigns),stable_statue_frame=frame))
  run=(parent/'run.lua').read_text();m=re.search(r'CURRENT_SMB3_POWERUPS=(\{.*\})\n',run);assert m;run=run[:m.start(1)]+lua(cfg)+run[m.end(1):];assert run.count(oldfixture.as_posix())==1;run=run.replace(oldfixture.as_posix(),fixture.as_posix());assert not re.search(r'\\u[0-9a-fA-F]{4}',run);(out/'run.lua').write_text(run,newline='\n')
  cmd=json.loads((parent/'command.json').read_text());cmd['argv']=[str(out/'native')if s==str(parent/'native')else str(out/'run.lua')if s==str(parent/'run.lua')else str(ROM)if s==str(oldrom)else s for s in cmd['argv']];put(out/'command.json',cmd)
  paths={Path(f['path'])for f in oldready['bindings']if Path(f['path'])not in{oldfixture,parent/'run.lua',parent/'config.json',parent/'source-controls.json',parent/'command.json',oldrom,oldrom.with_suffix('.dbg'),oldrom.with_suffix('.lbl')}}
  paths|={Path(__file__),oldfixture,fixture,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),proof,rp,parent/'run.lua',parent/'config.json',parent/'source-controls.json',parent/'command.json'};paths|={out/n for n in['run.lua','config.json','source-controls.json','command.json']}
  z=dict(oldready);z.update(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,goal_complete=False,ROM_sha256=EXPECTED,parent_readiness_sha256=sha(rp),change='CurrentEE real compiled metadata/four fresh full source campaigns; only stable-statue picture gate+read-only actual pose metadata. Same v4 controller/mechanics/source seeds/all strict hardware assertions/caps. Old v4 actual PASS24 on b01 retained as historical, never retagged.',source_qualification='24 actual complete GameLoop+fullNMI cases, bothmodes/variants, fresh onexactee. Not native PPU/deadline or standaloneLua proof.',bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)])
  put(out/'prepared-not-run.json',z);assert all(sha(Path(f['path']))==f['sha256']for f in z['bindings']);outputs.append(dict(identity=identity,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths),command=str(out/'command.json')))
 put(B/'current_smb3_final_ee_v5_handoff.json',dict(native_run=False,game_change=False,old_v4_unchanged=True,readies=outputs,source_proof=str(proof),source_sha256=sha(proof),owned_files=[str(Path(__file__)),str(fixture)]));print(json.dumps(outputs),flush=True)

if __name__=='__main__':main()
