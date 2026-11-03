"""Native distinct contact-Kill and direct pit initializer paths, actual GameLoop."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_respawn_1102_v93 as V
O=V.O


def main():
 source=Path(V.__file__);text=source.read_text().replace('v93','v96').replace('post-return-respawn-','native-contact-pit-')
 changes={
  "'KillPlayer','PlayerLoseLife','MegaManDeathUpdate'":"'KillPlayer','MegaManDeathStart','UnionDeathStartCore','PlayerLoseLife','MegaManDeathUpdate'",
  "if life_epoch is not None and engine==8":"if life_epoch is not None:break\n    if life_epoch is not None and engine==8",
  "assert events['KillPlayer']==events['PlayerLoseLife']==1 and life_epoch is not None and resumed is not None":"assert events['KillPlayer']==(1 if case=='contact'else 0)and events['MegaManDeathStart']==events['UnionDeathStartCore']==events['PlayerLoseLife']==1 and life_epoch is not None",
  'resumed_epoch=resumed[0],resumed_x=resumed[1]':"resumed_epoch=None,resumed_x=None,native_pit_flag=N.get(m,'MmDeathPit'),source_pending=m.ram[2][0xac]",
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(__file__=str(Path(__file__)),__name__='prince_contact_pit_v96');exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'native-contact-pit-CPU-v96.json';q=json.loads(path.read_text())
 contact,pit=q['scenarios'];assert contact['case']=='contact'and pit['case']=='pit'
 assert contact['native_pit_flag']==0 and pit['native_pit_flag']==1 and contact['actual_calls']['MegaManDeathUpdate']==168 and pit['actual_calls']['MegaManDeathUpdate']==150
 assert all(s['source_pending']==1 and s['final_lives']==1 for s in q['scenarios'])
 q.update(respawn_qualified=False,source_code_injected=True,native_initializers_unchanged=True,pit_direct_death_path='Original PlayerCtrlRoutine→MegaManCheckPit→MegaManDeathStart→UnionDeathStartCore; thenMmDeathPit1/engine11. It intentionally does not call KillPlayer. Actual later row34 acknowledges queued2→1 without duplicating native death when engine already11.',scope='Actual complete GameLoop plus ordinary NMI advances original source contact or a real unsupported CPU-terrain edge through unchanged native initializers,168contact/150pit death updates and exactly one life decrement. Stop at decrement before InitializeArea cold. No engine/death-age/life outcome writes; full changed-image cold/auth/respawn remains pending. v94 negative was an observer assuming pit must call KillPlayer; native source proves the distinct pit ingress.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,R/'src/player.s',R/'src/megaman_death.s',O/'post-return-life-negative-v94.json',O/'post-return-respawn-negative-v93.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
