"""Stage, verify and deliver the source-qualified Giant impact repair."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import check_mega_giant_impact_1110 as Q
import prepare_mega_giant_f33_native_1110 as G
from deliver_manual_title_1110 import ips_for, ASSET, REPO
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import prepare, sha

R=Q.R
NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
OLD_MINI=R/'build/manual-title-delivery-v2-1110/mini'
SMALL=R/'tools/audit/run_small_mesen_packet_1110.py'
COMBAT=R/'tools/audit/prepare_giant_combat_native_1110.py'
SYMBOLS=(G.BASE.with_suffix('.lbl'),G.BASE.with_suffix('.dbg'))


def read(p): return json.loads(p.read_text())


def qualified(proof):
    q=read(proof)
    assert q['passed'] and not q['ROM_written'] and q['parent_SHA256']==Q.PIN
    for path,digest in q['bindings'].items(): assert sha(R/path)==digest,path
    raw=bytearray(Q.BASE.read_bytes()); assert hashlib.sha256(raw).hexdigest()==Q.PIN
    touched=set()
    for row in q['patches']:
        at=row['file_offset']; old=bytes.fromhex(row['old_hex']); new=bytes.fromhex(row['new_hex'])
        assert len(old)==len(new) and raw[at:at+len(old)]==old
        extent=set(range(at,at+len(old))); assert not touched&extent; touched.update(extent)
        raw[at:at+len(old)]=new
    digest=hashlib.sha256(raw).hexdigest()
    assert digest==q['expected_memory_only_SHA256']
    return bytes(raw),digest


def packet_result(packet,rom,digest):
    ready=read(packet/'ready.json'); binding=read(packet/'capture/binding.json')
    result=read(packet/'capture/result.json')
    assert Path(ready['ROM']).resolve()==rom.resolve() and not ready['emulated_writes']
    assert ready['ROM_sha256']==binding['ROM_sha256']==result['ROM_sha256']==digest
    assert binding['ready_sha256']==sha(packet/'ready.json') and binding['exit_code']==0 and result['passed']
    for path,h in ready['bindings'].items(): assert sha(Path(path))==h,path
    return result


def combat(out,rom,digest,proof):
    subprocess.run([sys.executable,'-B',str(COMBAT),'--output',str(out),'--rom',str(rom),
                    '--expected-sha',digest,'--proof',str(proof)],check=True)


def stage(out,proof):
    raw,digest=qualified(proof); out.mkdir(exist_ok=True)
    rom=out/'candidate.nes'; assert not rom.exists(); rom.write_bytes(raw)
    combat(out/'contact',rom,digest,proof)
    refs={Path(__file__),proof,Path(G.__file__),G.SOURCE,G.PROOF,G.ROUTE}
    prepare(out/'full11',rom,G.controller(digest),refs,expected=digest,timeout=240,
            allow_interactive=True,rom_symbols=SYMBOLS,scope='Existing full Giant controller-only 1-1 route after impact repair.')
    old=packet_result(OLD_MINI,Q.BASE,Q.PIN)
    assert old['passed']
    source=(OLD_MINI/'controller.lua').read_text()
    assert source.count(Q.PIN)==1
    prepare(out/'mini',rom,source.replace(Q.PIN,digest),refs|{OLD_MINI/'controller.lua',
            OLD_MINI/'ready.json',OLD_MINI/'capture/binding.json',OLD_MINI/'capture/result.json'},
            expected=digest,timeout=180,allow_interactive=True,rom_symbols=SYMBOLS,
            scope='Unchanged Mini 1-1 inputs; shared collision regression after Giant-only impact fix.')


def candidate_evidence(native,proof):
    raw,digest=qualified(proof); rom=native/'candidate.nes'; assert rom.read_bytes()==raw
    evidence={name:packet_result(native/name,rom,digest) for name in ('contact','full11','mini')}
    assert evidence['contact']['terminal']['lives']==2 and evidence['full11']['terminal']['lives']==2
    return raw,digest,evidence


def deliver(out,proof,native):
    raw,digest,evidence=candidate_evidence(native,proof)
    before=check(NIGHTLY); assert before['ROM_sha256']==Q.PIN
    out.mkdir(exist_ok=True); assert not (out/'verified-delivery.json').exists()
    try:
        NIGHTLY.write_bytes(raw); assert check(NIGHTLY)['ROM_sha256']==digest
        combat(out/'downloads-contact',NIGHTLY,digest,proof)
        subprocess.run([sys.executable,'-B',str(SMALL),'--files','12',str(out/'downloads-contact/run.py')],check=True)
        actual=packet_result(out/'downloads-contact',NIGHTLY,digest)
        assert actual['terminal']['lives']==2
        patch=out/ASSET; patch.write_bytes(ips_for(NIGHTLY.read_bytes()))
        receipt=dict(installed=True,Downloads_launch_verified=True,backup_created=False,IPS_roundtrip=True,
                     ROM_SHA256=digest,previous_ROM_SHA256=Q.PIN,IPS_SHA256=sha(patch),before=before,
                     after=check(NIGHTLY),proof=str(proof),proof_SHA256=sha(proof),native=str(native),
                     native_results={n:sha(native/n/'capture/result.json') for n in evidence},
                     Downloads_result_SHA256=sha(out/'downloads-contact/capture/result.json'))
        (out/'verified-delivery.json').write_text(json.dumps(receipt,indent=2)+'\n')
    except (Exception,KeyboardInterrupt):
        NIGHTLY.write_bytes(Q.BASE.read_bytes()); assert check(NIGHTLY)['ROM_sha256']==Q.PIN
        raise
    print('Downloads verified:',digest)


def publish(out,proof,native):
    raw,digest,_=candidate_evidence(native,proof)
    q=read(out/'verified-delivery.json'); patch=out/ASSET
    assert q['ROM_SHA256']==digest==check(NIGHTLY)['ROM_sha256'] and NIGHTLY.read_bytes()==raw
    assert q['proof_SHA256']==sha(proof) and q['IPS_SHA256']==sha(patch) and patch.read_bytes()==ips_for(raw)
    packet_result(out/'downloads-contact',NIGHTLY,digest)
    def release(endpoint):
        return json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/{endpoint}'],encoding='utf-8'))
    current=release('tags/Current'); existing,=current['assets']; assert existing['name']==ASSET
    notes=out/'release-notes.txt'
    notes.write_text('Current MMC5 work-in-progress nightly.\n\nApply to clean headered Super Mario Bros. (World).\n'
                     'Mega Giant Mario now defeats enemies on body contact and shatters admitted question blocks and bricks. '
                     'Structural ground, pipes and exit objects retain donor behavior.\n'
                     'Verified: no-jump first-Goomba contact, native shattering, full Giant 1-1 traversal, '
                     'Mini regression, actual Downloads launch and IPS reconstruction.\n'
                     f'Patched ROM SHA-256: {digest}\n')
    subprocess.run(['gh','release','upload','Current',str(patch),'--clobber','--repo',REPO],check=True)
    subprocess.run(['gh','release','edit','Current','--latest','--notes-file',str(notes),'--repo',REPO],check=True)
    latest=release('latest'); asset,=latest['assets']
    assert latest['id']==current['id'] and latest['tag_name']=='Current'
    assert asset['name']==ASSET and asset['digest']=='sha256:'+sha(patch) and asset['size']==patch.stat().st_size
    q.update(release_tag='Current',release_is_latest=True,sole_asset=ASSET,release_asset_digest=asset['digest'])
    (out/'verified-delivery.json').write_text(json.dumps(q,indent=2)+'\n')
    print('Current sole IPS and Latest verified')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('stage','deliver','publish'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--proof',type=Path,required=True)
    p.add_argument('--native',type=Path)
    a=p.parse_args(); out=a.output.resolve(); proof=a.proof.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    if a.action=='stage': stage(out,proof)
    else:
        assert a.native
        (deliver if a.action=='deliver' else publish)(out,proof,a.native.resolve())


if __name__=='__main__': main()
