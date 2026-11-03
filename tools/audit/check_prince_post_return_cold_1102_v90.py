"""Actual44-carrier cold/readback/reset for the deferred-death source images."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_collision_cold_1102_v58 as V
import check_prince_collision_services_1102_v56 as C
O=C.O


def host(base):
 h=C.host(base);runtime=(O/'native-runtime-v78.bin').read_bytes();meta=(O/'native-metadata-v78.bin').read_bytes()
 h.m.ram[3][:len(runtime)]=runtime;h.s[0x800:0x800+len(meta)]=meta
 h.s[0x766:0x800]=(O/'native-state-v78.bin').read_bytes()[-154:]
 h.lab.update(json.loads((O/'native-labels-v78.json').read_text()));h.source('PpNativeFresh');assert not h.callbacks
 return h


def environment():
 source=Path(V.__file__);text=source.read_text();changes={
  "'cold-pool-v57.bin'":"'cold-pool-v87.bin'",
  "'cold-worker-v57'":"'cold-worker-v87'",
  "'cold-link-storage-v57.json'":"'cold-link-storage-v87.json'",
  "'native-runtime-v49.bin'":"'native-runtime-v78.bin'",
  "'native-metadata-v49.bin'":"'native-metadata-v78.bin'",
  'HOST_SUCCESSOR=C.host':'HOST_SUCCESSOR=NEW_HOST',
  'collision-cold-CPU-v58.json':'post-return-cold-CPU-v90.json',
  'collision-cold-negative-v58.json':'post-return-cold-negative-v90.json',
  '0xc65f<=c.pc<0xc678':'0xc65f<=c.pc<0xc67a',
  "('audio-prefix-destination-readback',(2,0x780),'audio-prefix')":"('audio-prefix-destination-readback',(2,0x766),'audio-prefix')",
  'live_metadata_end=0xdfce':'live_metadata_end=0xdfcf',
  '[0xc65f,0xc678]':'[0xc65f,0xc67a]',
  '[0xc780,0xc800]':'[0xc766,0xc800]',
  "native-state-v49.bin":"native-state-v78.bin",
  'C65F prefix copies/readbacks128B C780':'C65F prefix copies/readbacks154B C766',
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 # These two paths occur in the inherited binding list outside the replacement
 # string dictionary, so bind the actual successor images as well.
 text=text.replace("O/'native-runtime-v49.bin'","O/'native-runtime-v78.bin'").replace("O/'native-metadata-v49.bin'","O/'native-metadata-v78.bin'")
 env=dict(__file__=str(Path(__file__)),__name__='prince_post_return_cold_v90',NEW_HOST=host)
 exec(compile(text,str(source),'exec'),env);return env


def main():
 environment()['main']();path=O/'post-return-cold-CPU-v90.json';q=json.loads(path.read_text())
 assert q['positive']['distinct_staged_prefix_instruction_PC']>0 and q['physical_spare']==584
 q.update(private_proposal_only=True,changed_typed_cold_executed=True,shared_manager_cold_not_claimed=True,new_execution_granted=False,prefix_copy_bytes=154,staged_prefix_PC_half_open=[0xc65f,0xc67a],source_live_C700_zero_half_open=[0xc700,0xc766],live_audio_half_open=[0xc766,0xc800],metadata_end=0xdfcf,scope='Actual current16a9 host/peripheral instructions execute all44-carrier cold streams,27B staged prefix154B copy/readback and genuine original constructor with complete source/code comparison. Five corruption failures and nine guard rejections remain fail-closed. Both auth headers remain unpublished. Shared descriptor rows are input; full shared manager/header/cookie/auth/current9cf rebase and native admission remain pending. No ROM or emulator execution.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(V.__file__),O/'cold-link-storage-v87.json',O/'native-state-v78.bin',O/'post-return-measurement-v78.json',O/'native-stack-CPU-v89.json']})
 path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
