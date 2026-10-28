"""Finite actual assembled statue/OAM chronology; never launches an emulator."""
from pathlib import Path
import csv, hashlib, inspect, json, sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_smb3_powerups_prepare_v1 as prior
from current_smb3_hammer_aim_prepare_v4 import SOURCE_OLD,SOURCE_NEW
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ROM=R/'build/roster-20261028-fixes.nes'

def main():
 assert sha(ROM)=='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
 b=scoped_load(ROM);rows=[];events=[]
 names=['M3Graphics','M3SetFrame','M3DrawWorld','M3PublishBody','MetaspriteRenderLoop','DrawMetasprite','RosterOamReady']
 hooks={(address(b,n),(location(b,n)-16)//8192):n for n in names}
 def state(q):
  names=['M3Poof','M3RenderFrame','M3RenderForm','ObjectMetasprite','SmChrBank','M3SpritePageHi','PlayerChrBank','CurrentOAMOffset','RgOamPlayerStart','RgOamRotation','GuestOamRotationActive']
  z={n:q.get(n)for n in names};z.update(statue=q.get(prior.N['Statue']),native_frame=q.get(prior.N['Frame']),pointer=q.get('R0')+256*q.get('R1'),pose_pointer=q.get('SmPosePtr')+256*q.get('SmPosePtr',1),bankC=q.m.banks[2]);return z
 def observe(cpu,q,rec):
  if rec is None or rec['kind']!='statue' or not 28<=rec['age']<=36:return
  pc=cpu.pc;k=q.m.banks[(pc-32768)//8192]if pc>=32768 else -1;n=hooks.get((pc,k))
  if n:
   z=state(q);z.update(age=rec['age'],hook=n,pc=pc,bank=k,x=cpu.x,y=cpu.y)
   if n=='MetaspriteRenderLoop':z['actual_record']=list(q.m[z['pointer']:z['pointer']+21])
   events.append(z)
 def after(q,rec):
  if rec['kind']=='statue'and 28<=rec['age']<=36:
   z=state(q);z.update(age=rec['age'],OAM=list(q.m[512:768]));rows.append(z)
 source=inspect.getsource(prior.campaign);assert source.count(SOURCE_OLD)==1;source=source.replace(SOURCE_OLD,SOURCE_NEW)
 source=source.replace('        origin(cpu)','        observe(cpu,q,rec)\n        origin(cpu)')
 key='                writes=main(button);music.extend';assert source.count(key)==1
 source=source.replace(key,'                writes=main(button);after(q,rec);music.extend')
 source=source.replace("elif kind=='statue':complete=rec['statue']and rec['protected']and q.get(N['Statue'])==0 and quiet(q)and age>=100", "elif kind=='statue':complete=age>=40 # Diagnostic stop, not a completed component verdict.")
 env=dict(vars(prior));env.update(observe=observe,after=after,PLAN=prior.PLAN[:17]);exec(compile(source,str(__file__)+'::finite_original_campaign','exec'),env)
 result=env['campaign'](b,1,0)
 raw=b['raw'];records={n:dict(pc=address(b,n),bank=(location(b,n)-16)//8192,bytes=list(raw[location(b,n):location(b,n)+17]))for n in['M3Frame1ERight','M3Frame1ELeft','M3Poof0']}
 native=[]
 for identity in['mario3','luigi3']:
  p=R/f'build/current-ee1152-{identity}-hard-items-v5/native';z=json.loads((p/'result.json').read_text());native.append(dict(identity=identity,result_sha256=sha(p/'result.json'),picture_sha256=sha(p/'05-statue.png'),statue=next(r for r in z['records']if r['kind']=='statue')))
 proof=dict(scope='One complete source HardMario earned prefix through statue age40; diagnostic stop, no native execution or component verdict. All source RAM/OAM below are CPU observations, not missing native snapshots.',ROM_sha256=sha(ROM),script_sha256=sha(__file__),calls=result['complete_GameLoop_calls'],native_records=native,source_events=events,source_Main_after_NMI=rows,compiled_records=records,bindings={str(p):sha(p)for p in[ROM,ROM.with_suffix('.dbg'),Path(__file__),R/'src/smb3_mario_render.s',R/'src/smb3_mario_world.s',R/'tests/current-smb3-powerups-v5.lua']})
 out=R/'build/current_smb3_statue_picture_review_v1.json';assert not out.exists();out.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
 for z in rows:print({k:v for k,v in z.items()if k!='OAM'},flush=True)
 print(str(out),sha(out),flush=True)
if __name__=='__main__':main()
