"""Exact private153/154 proposal over cf7, preserving all current owners."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_live_manifest_1103_v151 as V
C,O,sha=V.C,V.O,V.sha


def image():
 q=json.loads((O/'live-manifest-v155.json').read_text());C.M.validate(q);base,_=C.parent();raw=bytearray(base['raw'])
 for row in q['patches']:
  at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
 assert sha(raw)==q['expected_memory_only_SHA256'];return dict(base,raw=bytes(raw)),q


def main():
 text=inspect.getsource(V.main).replace('v151','v155').replace('cold-pool-v150','cold-pool-v154').replace('cold-link-storage-v150','cold-link-storage-v154').replace('post-owner-v149','post-owner-v153').replace('post-owner-extra-v149','post-owner-extra-v153').replace('post-selector-v149','post-selector-v153').replace('native-labels-v149','native-labels-v153').replace('live-policies-measurement-v149','live-installer-measurement-v153').replace('(531,98,177)','(531,98,175)').replace('selector_bytes=177','selector_bytes=175').replace('runtime_version=149,backing_version=150','runtime_version=153,backing_version=154')
 old="(O/f'native-{n}-v149.bin').read_bytes()";assert old in text;text=text.replace(old,"(O/('native-'+n+('-v149.bin'if n=='metadata'else'-v153.bin'))).read_bytes()")
 old="O/f'native-{n}-v149.bin'";assert old in text;text=text.replace(old,"O/('native-'+n+('-v149.bin'if n=='metadata'else'-v153.bin'))")
 text=text.replace("(O/'post-owner-v153.cfg').read_text().replace('post-owner-extra-v153.bin','post-owner-extra-v155.bin')","(O/'post-owner-v130.cfg').read_text().replace('post-owner-extra-v130.bin','post-owner-extra-v155.bin')")
 env=dict(V.__dict__,__file__=str(Path(__file__)));exec(compile(text,str(Path(V.__file__)),'exec'),env);env['main']()
 path=O/'live-manifest-v155.json';q=json.loads(path.read_text());q['details'].update(installer_half_open=[0xc766,0xc77f],manager_executed_padding_unchanged=True,selector_spare=3)
 q['bindings'].update({p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'native-installer-v153.bin',O/'native-final-v153.bin']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
