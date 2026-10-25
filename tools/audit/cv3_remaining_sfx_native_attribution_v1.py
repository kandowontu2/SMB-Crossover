"""Bind first per-case native cadence differences to actual nested CPU intervals."""
from pathlib import Path
import argparse,csv,hashlib,json

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return[{k:int(v)if v.lstrip('-').isdigit()else v for k,v in r.items()}for r in csv.DictReader(p.open())]
def lookup(p):
 result={}
 for r in read(p/'native-cycles.csv'):result[(r['audioEpoch'],r['name'])]=r
 return result

def main():
 pa=argparse.ArgumentParser(description=__doc__);pa.add_argument('--native',type=Path,required=True);pa.add_argument('--output',type=Path,required=True);a=pa.parse_args();a.output.mkdir(parents=True,exist_ok=False);cases=[]
 for p in sorted(a.native.glob('candidate-*')):
  q=a.native/p.name.replace('candidate-','baseline-',1)
  if not(p/'native-proof.json').exists()or not(q/'native-proof.json').exists():continue
  cj,bj=[json.loads((x/'native-proof.json').read_text())for x in[p,q]]
  if not cj.get('passed')or not bj.get('passed'):continue
  cr,br=[read(x/'cadence.csv')for x in[p,q]];cu=bu=cd=bd=0;firstDraw=firstUpdate=None
  for i in range(min(len(cr),len(br))):
   cu+=cr[i]['updates'];bu+=br[i]['updates'];cd+=cr[i]['draws'];bd+=br[i]['draws']
   if firstDraw is None and cd<bd:firstDraw=dict(offset=i,candidate=cr[i],baseline=br[i])
   if firstUpdate is None and cu<bu:firstUpdate=dict(offset=i,candidate=cr[i],baseline=br[i])
  cp,bp=[lookup(x)for x in[p,q]];intervals=[]
  for event in[firstUpdate,firstDraw]:
   if event is None:continue
   wall=event['candidate']['wall']
   for (epoch,name),nr in cp.items():
    if name!='AudioUpdate'or nr['wall']not in[wall-1,wall]or(epoch,name)not in bp:continue
    old=bp[(epoch,name)];music=cp.get((epoch,'CvAudioPlay'));oldmusic=bp.get((epoch,'CvAudioPlay'));service=cp.get((epoch,'Cv3FxService'))
    assert music and oldmusic and nr['entryCycle']<=music['entryCycle']<=music['exitCycle']<=nr['exitCycle']
    assert old['entryCycle']<=oldmusic['entryCycle']<=oldmusic['exitCycle']<=old['exitCycle']
    if service:assert music['exitCycle']<=service['entryCycle']<=service['exitCycle']<=nr['exitCycle'],'Disjoint music/service CPU intervals'
    mc=music['cycles'];om=oldmusic['cycles'];sc=service['cycles']if service else 0
    row=dict(wall=nr['wall'],audioEpoch=epoch,candidate_age=nr['age'],baseline_age=old['age'],wholeAudioUpdate_candidate=nr['cycles'],wholeAudioUpdate_baseline=old['cycles'],whole_delta=nr['cycles']-old['cycles'],original_music_candidate=mc,original_music_baseline=om,original_music_delta=mc-om,added_source_service_inclusive=sc,other_disjoint_audio_delta=(nr['cycles']-mc-sc)-(old['cycles']-om),actual_candidate_audio_interval=[nr['entryCycle'],nr['exitCycle']],actual_source_service_interval=[service['entryCycle'],service['exitCycle']]if service else None)
    assert row['whole_delta']==row['original_music_delta']+sc+row['other_disjoint_audio_delta']
    if row not in intervals:intervals.append(row)
  cases.append(dict(name=p.name,profile=cj['profile'],mode=cj['mode'],event=cj['event'],candidate_proof_sha256=sha(p/'native-proof.json'),baseline_proof_sha256=sha(q/'native-proof.json'),first_actual_update_prefix_deficit=firstUpdate,first_actual_draw_prefix_deficit=firstDraw,actual_nested_CPU_intervals_near_first_differences=intervals,candidate_frames=cj['cases'][0]['frames'],baseline_frames=bj['cases'][0]['frames'],candidate_draws=cj['draws'],baseline_draws=bj['draws'],scope='Actual CPU interval attribution; nested music and service spans verified disjoint before subtraction. Inclusive source spans can contain real IRQ/NMI or DMC stalls. Engine scheduling and draw prefixes remain distinct from source fidelity.'))
 r=dict(passed=True,accepted=False,cases=cases,case_count=len(cases),tool_sha256=sha(__file__),scope='Read-only attribution of frozen actual native cases; no automatic acceptance or assertion that helper CPU savings recover per-case draw deficits.')
 (a.output/'proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(cases),actual_draw_deficit_cases=[r['name']for r in cases if r['candidate_draws']<r['baseline_draws']]),indent=2))
if __name__=='__main__':main()
