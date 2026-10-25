"""Build read-only controller guidance from a retained successful movie trace."""
from pathlib import Path
import argparse,csv,hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from workspace_storage import locate
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--character',type=int,required=True);p.add_argument('--variant',type=int,default=0);args=p.parse_args()
    O=R/'build/verification'/f'retime-movie-dg-{args.character}-{args.variant}';assert not O.exists();O.mkdir()
    source=locate(R/'build/roster-through-2-2'/f'claude-final-video-{args.character}-v{args.variant}-mmc3')
    rows=list(csv.DictReader((source/'trace.csv').open(newline='')))
    masks={int(z['frame']):int(z['mask'])for z in csv.DictReader((source/'inputs.csv').open(newline=''))}
    fields=('frame','world','level','area','areaType','x','y','yHigh','state','vx','vy','power')
    reference=O/'reference.lua'
    chosen=[z for z in rows if int(z['frame'])>=540 and(z['engine'],z['mode'],z['task'])==('8','1','3')]
    reference.write_text('return{\n'+''.join('{'+','.join(str(int(z[n]))for n in fields)+','+str(masks.get(int(z['frame']),int(z['buttons'])))+'},\n'for z in chosen)+'}\n',encoding='utf-8')
    guide=(R/'build/verification/specialist-rygar-hud-h-a/guide-w.lua').read_text()
    start=guide.index('local cursor,')
    guide='local ref=dofile('+json.dumps(reference.as_posix())+')\n'+guide[start:]
    guide=guide.replace('actual-pose-guidance-w.csv','retime-guidance.csv')
    guide=guide.replace("q[5]~=c.areaType", "q[5]~=c.areaType or q[4]~=c.area")
    guide=guide.replace("if c.world==0 and c.level==1 and c.x>=1024 then return{left=not c.grounded and signed(c.vx)>0}end\n",'')
    guide=guide.replace('if c.world==0 and c.level==1 and c.x>=760 and c.x<900 then','if c.char==7 and c.world==0 and c.level==1 and c.x>=760 and c.x<900 then')
    guide=guide.replace("local key=c.world..'-'..c.level..'-'..c.areaType", "local key=c.world..'-'..c.level..'-'..c.areaType..'-'..c.area")
    guide=guide.replace('Bounded H actual pose proposal, no copied state','Bounded full-movie guidance, no copied state')
    (O/'policy.lua').write_text(guide,encoding='utf-8')
    (O/'binding.json').write_text(json.dumps(dict(source_manifest_sha256=sha(source/'manifest.json'),source_trace_sha256=sha(source/'trace.csv'),source_inputs_sha256=sha(source/'inputs.csv'),
        active_reference_rows=len(chosen),reference_sha256=sha(reference),policy_sha256=sha(O/'policy.lua'),
        scope='Read-only telemetry and ordinary buttons. Source trace supplies guidance, never emulated state. Discovery is unverified until independently replayed; no powers/positions/terrain/ammo are granted.',goal_complete=False),indent=2)+'\n',encoding='utf-8')
    print(O,flush=True)
if __name__=='__main__':main()
