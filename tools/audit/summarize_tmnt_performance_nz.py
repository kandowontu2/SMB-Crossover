"""Bind equal-update native performance comparisons without inferring60Hz."""
from pathlib import Path
import csv, hashlib, json, statistics
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-performance-nz')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 old=OUT/'performance-baseline-v5';new=OUT/'performance-candidate-v5'
 a=json.loads((old/'results.json').read_text());b=json.loads((new/'results.json').read_text())
 assert a['passed']and b['passed']and a['driver_sha256']==b['driver_sha256']and a['observer_sha256']==b['observer_sha256']
 assert sha(ROOT/'tests/tmnt-performance.lua')==a['driver_sha256']
 assert sha(ROOT/'tools/audit/tmnt_performance_observer.lua')==a['observer_sha256']
 results={}
 for name in ['leonardo','donatello']:
  before=old/name;after=new/name
  assert(before/'gameplay.csv').read_bytes()==(after/'gameplay.csv').read_bytes()
  state=list(csv.DictReader((before/'gameplay.csv').open()));assert len(state)==600
  assert all(sum(q['phase']==phase for q in state)==120 for phase in ['idle','walk','enemies','primary','secondary'])
  assert sum(q['phase']=='enemies'and(int(q['enemy0'])>0 or int(q['enemy1'])>0)for q in state)==120
  item=dict(gameplay_byte_exact=True,game_updates=600,phases={},gameplay_sha256=sha(before/'gameplay.csv'))
  for phase in ['idle','walk','enemies','primary','secondary']:
   row={}
   for tag,folder in [('old',before),('new',after)]:
    calls=[q for q in csv.DictReader((folder/'tmnt-performance-calls.csv').open())if q['phase']==phase]
    frames=[q for q in csv.DictReader((folder/'tmnt-performance-frames.csv').open())if q['phase']==phase]
    row[tag]=dict(lag_NMIs=sum(int(q['lagNmis'])for q in frames),draws=sum(q['name']=='DrawAllMetasprites'for q in calls))
    for n,p in [('DrawAllMetasprites','draw'),('GameLoop','loop'),('TnDrawEquipment','equipment')]:
     values=[int(q['cpuCycles'])for q in calls if q['name']==n];assert values
     row[tag][p+'_CPU_mean']=statistics.mean(values)
   assert row['new']['equipment_CPU_mean']<row['old']['equipment_CPU_mean']
   row['draw_CPU_saved_pct']=100*(row['old']['draw_CPU_mean']-row['new']['draw_CPU_mean'])/row['old']['draw_CPU_mean']
   item['phases'][phase]=row
  results[name]=item
 proof=dict(passed=True,parent_ROM_sha256=a['ROM_sha256'],ROM_sha256=b['ROM_sha256'],driver_sha256=a['driver_sha256'],observer_sha256=a['observer_sha256'],runs=results,
  scope='Two representative identities, explicitly arranged native600-update arenas. Full gameplay traces identical. ISR entry/exit and body cycles excluded from routine spans. Routine spans nest and are not summed. Native triple-fire lag remains52NMIs/120updates in both versions; no constant60Hz or all-campaign speed claim.')
 (OUT/'candidate-v2/performance-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,ROM_sha256=proof['ROM_sha256'],gameplay_exact=True,phases={name:{p:round(v['draw_CPU_saved_pct'],2)for p,v in r['phases'].items()}for name,r in results.items()})))
if __name__=='__main__':main()
