"""Actual GameLoop contact and original pit paths through life loss, before cold."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_respawn_1102_v93 as V
O=V.O


def main():
 source=Path(V.__file__);text=source.read_text().replace('v93','v94').replace('post-return-respawn-','post-return-life-')
 old="if life_epoch is not None and engine==8"
 assert old in text;text=text.replace(old,"if life_epoch is not None:break\n    "+old)
 old="and life_epoch is not None and resumed is not None";assert old in text;text=text.replace(old,'and life_epoch is not None')
 old="resumed_epoch=resumed[0],resumed_x=resumed[1]";assert old in text;text=text.replace(old,'resumed_epoch=None,resumed_x=None')
 env=dict(__file__=str(Path(__file__)),__name__='prince_post_return_life_v94');exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'post-return-life-CPU-v94.json';q=json.loads(path.read_text())
 q.update(scope='Actual complete GameLoop plus ordinary NMI publication advances original source contact or a real unsupported CPU-terrain edge through native pit/contact Kill, death update and one genuine life decrement. Stop at earned decrement before InitializeArea cold reload. This test does not qualify respawn; v93 old source-injected cold bound negative remains explicit. No engine/death-age/life outcomes written.',respawn_qualified=False,source_code_injected=True)
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,O/'post-return-respawn-negative-v93.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
