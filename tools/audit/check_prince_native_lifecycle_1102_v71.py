"""Actual native death tree against the measured v70 RAM source fixture.

The old authenticated cold loader initializes genuine source state first; only
the measured code images are replaced in the CPU fixture. This is deliberately
not a qualified cold/auth/component image and never writes a ROM.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import check_prince_player_pipeline_1102_v67 as C
import check_prince_native_lifecycle_1102_v69 as D
O=C.O
original_loaded=C.loaded


def loaded():
 b,m,_=original_loaded()
 runtime=(O/'native-runtime-v70.bin').read_bytes()
 metadata=(O/'native-metadata-v70.bin').read_bytes()
 state=(O/'native-state-v70.bin').read_bytes()
 m.ram[3][:len(runtime)]=runtime
 m.ram[2][0x800:0x800+len(metadata)]=metadata
 m.ram[2][0x780:0x800]=state[-128:]
 return b,m,json.loads((O/'native-labels-v70.json').read_text())


def main():
 source=Path(D.__file__);text=source.read_text().replace('v69','v71')
 text=text.replace("b,m,lab=C.loaded()", "b,m,lab=loaded()")
 env=dict(__file__=str(Path(__file__)),__name__='prince_lifecycle_v71',loaded=loaded)
 exec(compile(text,str(source),'exec'),env)
 try:env['main']()
 finally:
  for stem in ['native-lifecycle-CPU-v71.json','native-lifecycle-negative-v71.json']:
   path=O/stem
   if not path.exists():continue
   q=json.loads(path.read_text())
   q.update(source_code_injected_after_cold=True,qualified_full_cold=False,packet_lifetime_amendment_ungranted=True,scope='Actual complete GameRoutines death/life tree using measured v70 source code inserted in the CPU fixture after original v65 cold initialization. This isolates the stack/lifecycle repair; old authentication is not a proof for changed code. No ROM/native emulator/outcome seeding or admitted component claim.')
   q['bindings']={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [source,Path(__file__),O/'native-runtime-v70.bin',O/'native-metadata-v70.bin',O/'native-state-v70.bin',O/'native-lifecycle-measurement-v70.json']}
   path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
