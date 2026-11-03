"""Observe authentic direct pit ingress while qualifying current full respawn."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_respawn_1102_v100 as V
O=V.O


def main():
 source=Path(V.__file__);text=source.read_text().replace('v100','v101')
 marker=' # A real Prince cold';assert marker in text
 injection=''' text=text.replace("'KillPlayer','PlayerLoseLife','MegaManDeathUpdate'","'KillPlayer','MegaManDeathStart','UnionDeathStartCore','PlayerLoseLife','MegaManDeathUpdate'")
 text=text.replace("assert events['KillPlayer']==events['PlayerLoseLife']==1 and life_epoch is not None and resumed is not None","assert events['KillPlayer']==(1 if case=='contact'else 0)and events['MegaManDeathStart']==events['UnionDeathStartCore']==events['PlayerLoseLife']==1 and life_epoch is not None and resumed is not None")
'''
 text=text.replace(marker,injection+marker)
 env=dict(__file__=str(Path(__file__)),__name__='prince_current_respawn_v101');exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'post-return-respawn-CPU-v101.json';q=json.loads(path.read_text());q.update(native_contact_and_pit_initializers_once=True,retained_observer_negative='v100 completed real pit cold/respawn/control, then the inheritedv93 observer incorrectly required KillPlayer on the direct native pit path. v101 traces the unchanged MegaManDeathStart/UnionDeathStartCore once in each scenario.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,O/'post-return-respawn-negative-v100.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
