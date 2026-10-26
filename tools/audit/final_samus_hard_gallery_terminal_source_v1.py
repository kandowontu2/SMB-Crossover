"""Source-only check of Samus's genuine DrawAll return/publication owner."""
from pathlib import Path
import argparse,hashlib,json
from final_samus_hard_gallery_source_v1 import D,SHA,TraceArena,OWNER_NAMES
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True)
 rom=D/'root-current-roster-composition-v1/candidate.nes';assert sha(rom)==SHA;b=scoped_load(rom)
 for name in ['RosterOamReady','DrawAllMetasprites','SamusFreezeDrawAll']:
  if name not in OWNER_NAMES:OWNER_NAMES.append(name)
 rows=[]
 for owned in [0,129,131,133,137,145,161,193]:
  q=TraceArena(b);q.set('InvOwnedLo',owned,2);q.put(PlayerStatus=0 if owned==0 else 1,PlayerOutlinesOff=1)
  q.invoke('PlayerGfxHandler');q.invoke('SamusFreezeDrawAll');names=[z['owner']for z in q.calls[-1]['entries']]
  assert 'DrawAllMetasprites'in names and 'RosterOamReady'not in names and q.get('GuestOamRotationActive')==0
  rows.append(dict(owned=owned,rotation=0,RosterOamReady_seen=False,calls=q.calls))
 files=[Path(__file__),rom,rom.with_suffix('.dbg'),D/'root-current-roster-composition-v1/source/src/metasprite_engine.s']
 proof=dict(passed=True,source_only=True,ROM_sha256=SHA,rows=rows,conclusion='Samus selected2 takes the nonrotated legacy tail. RosterOamReady is the rotated-tail RTS and never publishes Samus. The old shared publication counter/bodyDisplayed chain therefore cannot establish Samus publication coverage.',bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in files])
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(sha(a.output/'proof.json'))
if __name__=='__main__':main()
