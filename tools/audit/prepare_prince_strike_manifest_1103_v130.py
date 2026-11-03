"""Final strike backing/cookies over the exact installed Bub87 parent; no ROM."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_current_post_return_1102_v97 as M
O=M.O
BASE=R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
OLD=R/'build/bub-upgrades-root-candidate-1102-v72/bub-original-upgrades.nes'
COOKIE='a72701f3691d419fd9ae7473840ce393'


def parent():
 old=OLD.read_bytes();raw=BASE.read_bytes();assert M.sha(old)==M.PARENT and M.sha(raw)==PIN
 q=json.loads((M.BUB/'proposal.json').read_text());M.validate(q)
 current=json.loads((BASE.parent/'proposal.json').read_text());M.validate(current)
 assert current['ROM_SHA256']==PIN and current['cookie']==COOKIE
 pages=q['pages'];image=(BASE.parent/'private-image.bin').read_bytes();assert len(image)==8192
 allowed=set(range(q['cookie_offset'],q['cookie_offset']+16))
 for i,page in enumerate(pages):
  at=1048592+1024*page;allowed.update(range(at,at+1024));assert raw[at:at+1024]==image[i*1024:(i+1)*1024]
 changes={i for i,(a,z)in enumerate(zip(old,raw))if a!=z};assert len(changes)==145 and changes<=allowed
 assert raw[q['cookie_offset']:q['cookie_offset']+16]==bytes.fromhex(COOKIE)
 # Root's head/initial-tier successor leaves the concrete native retirement
 # leaf intact. Shared code, source bodies of every other owner, joint rare
 # gate, Sunny and menu therefore retain the exact b7 parent bytes.
 assert q['labels']['BbNativeRetire']==0xbb7a
 off=0xbb7a-0xa000;assert image[off:off+16]==(M.BUB/'private-image.bin').read_bytes()[off:off+16]
 q=dict(q,new_cookie=COOKIE)
 native=M.scoped_load(M.L.BASE);return dict(native,raw=raw),q


def image():
 q=json.loads((O/'strike-manifest-v130.json').read_text());M.validate(q);base,_=parent();assert M.sha(base['raw'])==q['parent_memory_SHA256'];raw=bytearray(base['raw'])
 for row in q['patches']:
  at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
 assert M.sha(raw)==q['expected_memory_only_SHA256'];return dict(base,raw=bytes(raw)),q


def main():
 source=Path(M.__file__);text=inspect.getsource(M.bundle).replace('v97','v130').replace('v78','v122').replace('v87','v129').replace('len(payload)==44472','len(payload)==44476')
 env=dict(M.__dict__,parent=parent);exec(compile(text,str(Path(__file__)),'exec'),env)
 base,new,patches,details=env['bundle']()
 assert details['manager_bytes']==531 and details['extra_bytes']==94 and details['selector_bytes']==156
 assert details['physical_spare']==580 and details['Bub_cookie']==COOKIE
 files=[Path(__file__),source,BASE,BASE.parent/'proposal.json',BASE.parent/'private-image.bin',O/'post-return-manifest-v97.json',O/'deferred-strike-measurement-v122.json',O/'deferred-strike-CPU-v123.json',O/'strike-lifetime-CPU-v126.json',O/'native-drop-policy-CPU-v119.json',O/'cold-link-storage-v129.json',O/'cold-pool-v129.bin',O/'native-labels-v122.json',*[O/f'native-{n}-v122.bin'for n in ['runtime','metadata','state']],O/'post-owner-v130.s',O/'post-owner-v130.bin',O/'post-owner-extra-v130.bin',O/'post-selector-v130.s',O/'post-selector-v130.bin',R/'docs/qa/allocations/prince-post-return-lifetime-1102-v70.json',R/'docs/qa/allocations/joint-native-rare-gate-1102-v70.json']
 q=dict(passed=True,private_source_composition_only=True,ROM_written=False,menu_admitted=False,installed=False,parent_input=BASE.relative_to(R).as_posix(),parent_memory_SHA256=M.sha(base['raw']),expected_memory_only_SHA256=M.sha(new['raw']),patches=patches,details=details,source_runtime_version=122,cold_backing_version=129,no_new_resources=True,current_Bub145_byte_delta_retained=True,native_no_drop_acknowledgement='Authenticated owner preserves actual native InvDropEnemy=X after full actor revalidation, then invokes unchanged original fixed126:9AF8 suffix. No native/shared defeat instructions changed.',required='Actual changed-image complete Ex37/Prince38/Bub39 cold/headers/retirement, foreign hot ABI, earned-strike, full death/respawn and IRQ/FF-lag/nested qualification. Prototype source proofs are separate. No ROM/menu/native admission authorized.',bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in files})
 (O/'strike-manifest-v130.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','patches']}))


if __name__=='__main__':main()
