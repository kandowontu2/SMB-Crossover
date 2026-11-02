"""Compose frozen Ex repair with the installed disjoint Arthur wall/policy fixes."""
from pathlib import Path
import hashlib,json,os,sys,re
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_excitebike_dispatch_1101_v1 import O,save,sha,labels
from prepare_excitebike_host_1101_v1 import BASE,PIN


def main():
    source=O/'current2.nes';base=R/'build/arthur-side-clamp-1101-v8/maturity-candidate.nes'
    assert sha(source)=='23086fbfa3daa0f4b5b850166c51362eb6a7e8908230bd01cb1a679eadb15616'
    assert sha(base)=='b9e685ffd0620a213a2fc05219e2bae415ee81aa07ab0e994db79455792ef6c4'
    assert sha(BASE)==PIN
    assert json.loads((O/'native3/capture/binding.json').read_text())['exit_code']==1
    old=BASE.read_bytes();ex=source.read_bytes();arthur=base.read_bytes();raw=bytearray(arthur)
    assert len(old)==len(ex)==len(arthur)
    exdelta={i for i,(a,b)in enumerate(zip(old,ex))if a!=b}
    ardelta={i for i,(a,b)in enumerate(zip(old,arthur))if a!=b}
    assert len(ardelta)==198 and not exdelta&ardelta
    assert all(82592<=i<82807 or i in [580950,580951]for i in ardelta)
    manifest=json.loads((O/'current2-composition.json').read_text())
    for p in manifest['patches']:
        at=p['offset'];before=bytes.fromhex(p['old']);after=bytes.fromhex(p['new'])
        assert raw[at:at+len(before)]==before,(p['role'],hex(at))
        raw[at:at+len(after)]=after
    assert all(raw[i]==ex[i]for i in exdelta)
    assert all(raw[i]==arthur[i]for i in range(len(raw))if i not in exdelta)
    assert {i for i,(a,b)in enumerate(zip(arthur,raw))if a!=b}==exdelta
    dest=O/'current3.nes';dest.write_bytes(raw)
    overrides={n:a for file in ['scene.lbl','host.lbl','shot-owner.lbl']for n,a in labels(O/file).items()}
    lines=[]
    for line in base.with_suffix('.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line)
        if not m or m[2]not in overrides:lines.append(line)
    lines.extend(f'al {a:06X} .{n}'for n,a in sorted(overrides.items()))
    dest.with_suffix('.lbl').write_text('\n'.join(lines)+'\n')
    dbg=dest.with_suffix('.dbg')
    if not dbg.exists():os.link(base.with_suffix('.dbg'),dbg)
    assert dbg.read_bytes()==base.with_suffix('.dbg').read_bytes()
    save('current3-composition.json',dict(passed=True,private_candidate=True,
        ROM_SHA256=sha(dest),base_ROM_SHA256=sha(base),Ex_counterpart_SHA256=sha(source),
        previous_common_base_SHA256=PIN,Ex_changed_bytes=len(exdelta),Arthur_retained_changed_bytes=len(ardelta),
        exact_disjoint_delta=True,all_other_b9_bytes_preserved=True,
        Arthur_wall_file_half_open=[82592,82807],Arthur_policy_file_offsets=[580950,580951],
        native_verified=False,installed=False,
        scope='Byte-exact disjoint composition only. Ex native3 hardware pass retained as input evidence, its gameplay negative preserved. Combined native Ex and Arthur flower regressions remain mandatory.',
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),BASE,source,base,
            base.with_suffix('.json'),base.parent/'candidate.json',O/'current2-composition.json',
            O/'native3/capture/result.json',O/'native3/capture/diagnosis.json',O/'native3/capture/binding.json']}))
    print(json.dumps(dict(passed=True,ROM=str(dest),ROM_SHA256=sha(dest),Ex_delta=len(exdelta),Arthur_delta=len(ardelta))))


if __name__=='__main__':main()
