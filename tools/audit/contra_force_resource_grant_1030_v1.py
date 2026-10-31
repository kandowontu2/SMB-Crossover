"""Record reviewed CF source evidence and selected-owner resource bounds."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
S=R/'build/contra-force-source-kernel-qualified-v1'
P=R/'build/peach-palette-fix-1030-v1'
D=R/'docs/qa/checkpoints/2026-10-30/contra-force-source-kernel-resource-review'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    h=json.loads((S/'handoff.json').read_text())
    assert sha(S/'handoff.json')=='e64181c1bf3dd5be271becc620b591f6f01dd207ae4dcdd91fd4417cfe707750'
    for p,s in h['bindings'].items():assert sha(p)==s,p
    source=Path(h['archive']['path']);assert sha(source)==h['archive']['sha256']
    with zipfile.ZipFile(source)as z:
        assert len(z.namelist())==178
        for n in z.namelist():
            assert Path(n).suffix.lower()not in ['.nes','.exe','.o'],n
            assert z.read(n)==(R/n).read_bytes(),n
    raw=(P/'joint/candidate.nes').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='f56e55cd69b93821e66548848305cf9822e2ac0e8a25752d7192332cded53b78'
    preimage=raw[16+128*8192+935*1024:16+128*8192+969*1024]
    assert preimage==bytes(34*1024)
    cfg=(P/'joint/private.cfg').read_text()
    assert 'UNALLOCATED_CHR_MEM:start=$e1400,size=$1ec00' in cfg
    d=dict(status='REVIEWED_PRIVATE_CF_RESOURCE_GRANT_NOT_ADMISSION',source=True,native=False,installed=False,
        source_bindings_verified=len(h['bindings']),source_archive_members_verified=178,
        source_handoff_sha256=sha(S/'handoff.json'),proposal_sha256=sha(S/'host-resource-proposal.json'),
        current_parent_sha256=hashlib.sha256(raw).hexdigest(),
        selected_owner=dict(raw=31,slot=30,alternate_bits='FmGroups bits3..4'),
        approved_private_resources=dict(
            RAM='Exclusive raw31 temporal A1+A3 code phases with always-mapped C2 state/transport; preserve RAM0.',
            CHR_pages=dict(begin=935,end_exclusive=969,carrier_max=24,body_max=9,shot_max=1),
            original_CHR_preimage=dict(bytes=len(preimage),fill=0,sha256=hashlib.sha256(preimage).hexdigest(),
                source_owner='Existing UNALLOCATED_CHR_MEM; explicit new bound after Benj/BT/Bowser leases.'),
            cookie='Family1F/alternate0..3 at shared C2 DFE0..<DFF0, valid cleared first/published last.'),
        required_before_host_adoption=[
            'Produce actual source/link/packed images within all three bank bounds, with no unexplained ROM islands.',
            'Retire existing Quick/Arthur/BT/Bowser images and invalidate RAM3 cookie before A3 overwrite; preserve native RAM0.',
            'Keep the A1/A3 phase trampoline in always-mapped C2 or owned ROM; restore the originating code bank before returning.',
            'No new global RAM/ZP/resident or mapper-control lease: choose existing host scratch only with full saved native state and measured ISR seams.',
            'Preserve5FFF busy contract, all33SMC/live-register interrupt restores, native raw maps and actual forced-blank loader/readback rules.',
            'Coordinate genuine raw31 service ingress with the27/33 dispatcher owners; no shared table edits without measured proposal.',
            'Do not recolor native world objects to obtain missing weapon colors; qualify palette/OAM fairness and exact native restore.',
            'Preserve current64 source, Benj5/6 and all other explicitly granted resource spans.',
            'Native64px-pipe and actual gameplay checks still required; source apex alone does not prove traversal.'
        ],
        not_granted=['Additional resident ROM islands','Additional global scratch or RAM0','Any roster readiness or public unlock'],
        bindings={str(p):sha(p)for p in [Path(__file__),S/'handoff.json',S/'host-resource-proposal.json',source,
            P/'handoff.json',P/'joint/candidate.nes',P/'joint/private.cfg']})
    D.mkdir(parents=True)
    (D/'resource-grant.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
    shutil.copy2(source,D/'source-only.zip')
    shutil.copy2(S/'handoff.json',D/'source-handoff.json')
    shutil.copy2(S/'host-resource-proposal.json',D/'proposal.json')
    (D/'README.md').write_text('Reviewed230 source bindings and all178 archive members. The measured Contra Force kernel cannot fit a16KB guest. This grants a private raw31-only three-bank implementation and CHR935..<969, preserving all existing leases; it does not mark any Contra Force character playable. The native donor services in the CPU fixtures remain explicit original-ROM oracles until real SMB adapters replace them. Phase return safety, retirement, mapper/interrupt rules, authentic palettes, gameplay and traversal remain implementation requirements. No full ROM or executable is archived.\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(reviewed=True,source_bindings=len(h['bindings']),archive_members=178,
        grant=str(D/'resource-grant.json'),grant_sha256=sha(D/'resource-grant.json'))))


if __name__=='__main__':main()
