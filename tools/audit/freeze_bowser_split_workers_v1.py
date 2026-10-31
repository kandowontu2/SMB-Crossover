"""Freeze the real split transport milestone, retaining explicit non-readiness."""
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
P=R/'build/coherent62-lives-fixes-v1'
O=R/'build/bowser-split-workers-v2'
J=O/'joint'
C=R/'docs/qa/checkpoints/2026-10-30/bowser-split-loader-router-source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not(O/'handoff.json').exists() and not C.exists()
    q=json.loads((O/'source-stage.json').read_text())
    assert q['candidate']=='30eb1d479d5bdc5998d5082a20672e001f4f07017870dea0f0eafee09a33de68'
    files={Path(p)for p in json.loads((P/'handoff.json').read_text())['bindings']}
    files|={P/'handoff.json',R/'build/bowser-source-core-v5/handoff.json',
            R/'build/bowser-resource-closure-v1/proposal.json'}
    for name in ['loader-controls.json','loader-vectors-v1.json','public-ABI-controls.json']:
        control=json.loads((O/name).read_text());assert control['passed']
        for p,h in control['bindings'].items():assert sha(p)==h,p
    # Original v1 candidate has identical bytes. Its global Restore label
    # shadowed a private old DBG name only; v2 removes this reporting collision.
    old=R/'build/bowser-split-workers-v1'
    assert sha(old/'joint/candidate.nes')==q['candidate']
    negative=dict(status='RETAINED_PRE_FREEZE_FAILURES',
        first_link=dict(error="Old-symbol dictionary assertion: Restore",ROM_bytes_equal_v2=True,
                       explanation='Unprefixed private label collided in DBG name lookup. New private labels are Bw-prefixed; every old parsed symbol now exact.'),
        ABI_v1=dict(error='SyntaxError before execution: missing space in else167',product_executed=False))
    try:ast.parse((R/'tools/audit/bowser_split_abi_controls_v1.py').read_text())
    except SyntaxError as e:negative['ABI_v1'].update(line=e.lineno,message=e.msg)
    else:raise AssertionError('Expected retained ABI parser negative')
    (O/'retained-negatives.json').write_text(json.dumps(negative,indent=2)+'\n')
    for n in ['common.inc','load.s','copy.s','check.s','retire.s','router.s','preview.s','image.s','image.cfg','stream.s','body.chr','cookie.bin']:
        files.add(old/'joint/bowser'/n)
    for n in ['candidate.nes','candidate.dbg','candidate.lbl','private.cfg','bowser.bin']:
        files.add(old/'joint'/n)
    files|={p for p in O.glob('*')if p.is_file()}
    files|={p for p in (J/'bowser').glob('*')if p.is_file()}
    files|={J/n for n in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.cv3-mirror.json',
                           'private.cfg','source-stage.json','bowser.bin','ram3.bin','ff-cookie.bin','code.bin','data.bin']}
    link=json.loads((O/'actual-host-link.json').read_text())['command']
    files|={Path(x)for x in link if x.endswith('.o')}
    toolnames=['prepare_bowser_split_workers_v1.py','prepare_bowser_split_workers_v2.py',
               'bowser_split_loader_controls_v1.py','bowser_split_loader_vectors_v1.py',
               'bowser_split_abi_controls_v1.py','bowser_split_abi_controls_v2.py',
               'freeze_bowser_split_workers_v1.py','private_build_outputs_v1.py',
               'arthur_cache_host_controls_v1.py','ff_wram_host_controls_v7.py',
               'ff_host_pickups_vectors_v2.py','ff_ram3_execution_controls_v2.py',
               'verify_native_relocation.py','check_tmnt_render_oa.py','prepare_cv3_dmc_mirror.py']
    files|={R/'tools/audit'/n for n in toolnames}
    # Some longstanding tools live directly in tools rather than audit.
    files={p if p.exists()else R/'tools'/p.name for p in files}
    assert all(p.exists()for p in files),[str(p)for p in files if not p.exists()]
    note='''Bowser split-loader/router SOURCE milestone. Both characters remain pending.

Parent is installed dfdb194a62WIP, sourcefae1ec38. All old native symbols,
header, existing62 PRG/CHR outside the exact new grants, and FF/Quick/Arthur
payloads/cookies remain exact. No shared/menu/native gameplay ingress changed.

Actual allocated1281B A-view ROM now uses913B: loader178, copy/PPUrestore179,
cookie/eligibility156, retirement43, typedrouter209, originalstanding148.
368B remains inside these same six owned islands; no additional lease.
Body824..<827 and carrier927..<935 are the exact granted physicalCHR ranges.
Workers execute in A only while C selects rawRAM3 for copy/verification.
No writes to5102/5103/5113, no new globalRAM/ZP, no permanent protection change.

The full8KB source-built transport image is genuinely copied through buffered
2007 and read back before valid-last16B family27/version/fingerprint cookie.
Warm/rejected calls do not copy. Retirement invalidates only family27 before
future selected-owner publication. All36 cache services currently C-clear
decline: real source physics/contact/combat/render/lifecycle are NOT joined.
The separately frozen688B authentic source core is not replaced by an invented
floor callback to create a passing host. This is not a playable/admission ROM.

CPU controls:12cold/warm palette/CHR-context cases,9rejection/write-protection/
readback negatives,1088all-cookie/all64flags checks;4736valid/invalidrow ABI
cases,64warm+64busyreject+384retirement flag cases.1347actual normal/lag/pause
NMI/legalIRQ cuts preserve all33SMC/livepage1/AXYP/rawmaps/borrowedpairs; native
AudioUpdate runs once/NMI. Coldcopy257156CPU is forcedblank work, not cadence.
No Mesen/native tests or installation. Existing FF419 deadline remains open.

Retained negatives: first source link had a private Restore DBG-name collision
only (ROM identical); new Bw-prefixed labels restore actual symbol comparison.
An ABI fixture typo failed parsing before execution; corrected v2 passes.
Reproduction recipes are actual-host-link.json and per-object build JSON,
validated by private_build_outputs_v1 before every compiler/link invocation.
Do not replay inherited outputs without that guard.
'''
    (O/'HANDOFF.txt').write_text(note)
    files.add(O/'HANDOFF.txt')
    archive=O/'source-only.zip';members=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(files):
            if p.suffix.lower()in['.s','.asm','.inc','.py','.cfg','.dep','.json','.txt','.chr']or p.name in['cookie.bin','ff-cookie.bin']:
                rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
    files.add(archive)
    result=dict(status='FROZEN_REAL_SPLIT_LOADER_ROUTER_NOT_PLAYABLE',source=True,
        candidate=q['candidate'],parent=q['parent'],native=False,admitted=False,ready=62,
        source_physics_host_joined=False,all36_services_decline=True,
        resident_used=913,resident_granted=1281,resident_headroom=368,
        real_vector_cases=1347,typed_allflag_cases=4736,archive_members=len(members),
        bindings={str(p.resolve()):sha(p)for p in sorted(files)})
    (O/'handoff.json').write_text(json.dumps(result,indent=2)+'\n')
    for p,h in result['bindings'].items():assert sha(p)==h,p
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None
        for p in z.namelist():assert hashlib.sha256(z.read(p)).hexdigest()==sha(R/p),p
    C.mkdir(parents=True)
    for n in ['handoff.json','source-only.zip','HANDOFF.txt','source-stage.json','root-grant-and-partition.json','retained-negatives.json']:
        shutil.copyfile(O/n,C/n)
    for n in ['loader-controls.json','loader-vectors-v1.json','public-ABI-controls.json']:
        x=json.loads((O/n).read_text())
        x={k:v for k,v in x.items()if k not in['rows','checks','routes','warm','rejected','retirement']}
        x['full_receipt_sha256']=sha(O/n)
        (C/n).write_text(json.dumps(x,indent=2)+'\n')
    receipt=dict(status=result['status'],handoff=sha(O/'handoff.json'),candidate=q['candidate'],
        verified_bindings=len(files),archive_members=len(members),
        bindings={str(p.resolve()):sha(p)for p in sorted(C.iterdir())})
    (C/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    owned=[(R/'tools/audit'/n).relative_to(R).as_posix()for n in toolnames[:7]]
    owned += [p.relative_to(R).as_posix()for p in sorted(C.iterdir())]
    owned += [(C/'owned-files.txt').relative_to(R).as_posix()]
    (C/'owned-files.txt').write_text('\n'.join(owned)+'\n')
    print(json.dumps(dict(handoff=str(O/'handoff.json'),SHA=sha(O/'handoff.json'),
                         bindings=len(files),members=len(members),checkpoint=str(C),
                         checkpoint_SHA=sha(C/'receipt.json'),native=False,admitted=False)))


if __name__=='__main__':main()
