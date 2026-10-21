"""Reproduce the first new H route contacts with actual native injury ownership."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-pit-rygar-h-contacts-ep'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 observer=V/'root49-current-g-samus-a/observer-g.lua';old=observer.read_text()
 anchor="if r('GameEngineSubroutine')==8 and(frame%2==0 or r('WorldNumber')==1)then"
 assert old.count(anchor)==1
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 assert workspace_bytes(R)+180000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),observer_sha256=sha(observer),phase_cap=180000000,reserve=50000000,global_cap=80000000000,scope='Readonly actual H injury exec eight-byte guards, six live actor/native collision boxes and RAM. Reproduce original EL ordinary input streams only, with sparse local EndFrame observations. No new accepted route or source-geometry conclusion.'),indent=2)+'\n')
 results=[]
 for ident,name,world,level,x in [(6,'pit',1,1,2300),(7,'rygar',0,1,850)]:
  parent=R/'build/roster-through-2-2'/f'root49-h-{name}-guided-el-{ident}-v0-mmc3';m=json.loads((parent/'manifest.json').read_text())
  s=old.replace(anchor,f"if r('GameEngineSubroutine')==8 and r('WorldNumber')=={world} and r('LevelNumber')=={level} and r('Player_X_Position')+256*r('Player_PageLoc')>={x} then")
  observer_path=J/(name+'-observer.lua');observer_path.write_text(s)
  policy=J/(name+'-policy.lua');policy.write_text('dofile('+json.dumps(observer_path.as_posix())+')\nreturn function(c)return{}end\n')
  out=R/'build/roster-through-2-2'/f'root49-h-{name}-contacts-ep-{ident}-v0-mmc3'
  args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(ident),'--mapper','mmc3','--rom',str(cp.parent/'smb-crossover-mmc3.nes'),'--tag','root49-h-'+name+'-contacts-ep','--policy',str(policy),'--prefix',str(parent/'inputs.csv'),'--frames',str(m['result']['frames']+2),'--timeout','900','--workspace-cap-gb','80','--discovery-fast']
  (J/(name+'-command.json')).write_text(json.dumps(args,indent=2)+'\n')
  with(J/(name+'-native.log')).open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  actual=json.loads((out/'manifest.json').read_text());assert actual['result']==m['result']
  streams={n:sha(out/n)==sha(parent/n) for n in ['inputs.csv','trace.csv','events.csv']};assert all(streams.values())
  z=dict(character=name,exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),original_EL_manifest_sha256=sha(parent/'manifest.json'),result=actual['result'],literal_streams=streams,injury_sha256=sha(out/'actual-injury-b.csv'),analysis_pending=True);results.append(z);print(json.dumps(z),flush=True)
 (J/'result.json').write_text(json.dumps(dict(results=results,goal_complete=False),indent=2)+'\n')
if __name__=='__main__':main()
