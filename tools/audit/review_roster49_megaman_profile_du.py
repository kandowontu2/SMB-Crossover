"""Classify real audio-in-NMI samples instead of assuming every scope is main code."""
from pathlib import Path
import collections,csv,hashlib,json,statistics
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-megaman-h-profile-ds'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=J/'review-du.json';assert not out.exists()
 prep=json.loads((J/'preparation.json').read_text());old=R/'tools/audit/profile_roster49_megaman_h_ds.py';assert sha(old)==prep['script_sha256']
 d=R/'build/roster-through-2-2/root49-h-megaman-profile-ds-1-v0-mmc3';source=R/'build/roster-through-2-2/root49-h-megaman-dg-1-v0-mmc3';m=json.loads((d/'manifest.json').read_text())
 assert m['result']['failure']=='frame limit'and m['result']['frames']==8850 and m['rom_sha256']=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'
 rr=lambda p:list(csv.DictReader(p.open(newline='')));literal={}
 for n in['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']:
  a,b=rr(d/n),rr(source/n);literal[n]=a==b[:len(a)];assert literal[n],n
 groups=collections.defaultdict(list)
 for line in(d/'ordinary-profile.jsonl').open():
  z=json.loads(line);assert z['exclusive_cycles']>=0 and z['entry_ISR_depth']in[0,1]
  assert z['entry_ISR_depth']==int(z['name']in['AudioUpdate','MegaManAudioUpdate','MegaManAudioNativeUpdate'])
  groups[(z['name'],z['entry_ISR_depth'])].append(z)
 result={}
 for(name,depth),a in groups.items():
  cycles=sorted(z['exclusive_cycles']for z in a);result[name]=dict(actual_ISR_depth=depth,calls=len(a),median=statistics.median(cycles),p95=cycles[int((len(cycles)-1)*.95)],maximum=max(cycles),total=sum(cycles),interrupt_cycles_excluded=sum(z['interrupted_cycles']for z in a))
 negative=dict(original_script_sha256=sha(old),reason='DS native and all nine prefix comparisons passed. Host summary then incorrectly required every scope at ISR depth0. Actual MegaManAudioNativeUpdate/MegaManAudioUpdate/AudioUpdate execute at native NMI depth1; all other scopes0. No negative exclusive cycles. DU retains and separates actual depths without changing observations or native execution.')
 (J/'host-depth-negative-du.json').write_text(json.dumps(negative,indent=2)+'\n')
 report=dict(status='PASS_ACTUAL_H_MEGAMAN_UNDERGROUND_PROFILE_WITH_EXPLICIT_NMI_AUDIO',script_sha256=sha(__file__),preparation_sha256=sha(J/'preparation.json'),manifest_sha256=sha(d/'manifest.json'),raw_profile_sha256=sha(d/'ordinary-profile.jsonl'),profile_rows=sum(len(a)for a in groups.values()),native_prefixes=literal,scopes=result,host_negative_sha256=sha(J/'host-depth-negative-du.json'),limits=['Exclusive means child IRQ/NMI duration removed at each actual entry depth. Parent function scopes still include their ordinary child functions; do not add parent and child totals.','Actual unchanged H6600..8800 underground baseline Buster route, not WaterShield/other weapon stress or total FPS optimization.'],goal_complete=False)
 out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(review_sha256=sha(out),scopes=result)),flush=True)
if __name__=='__main__':main()
