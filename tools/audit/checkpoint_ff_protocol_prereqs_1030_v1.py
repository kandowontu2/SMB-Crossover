"""Archive FF selector repair and retained sword/mailbox ownership findings.

This is a compact delta against the previously pushed native-flash source
checkpoint; it does not duplicate that complete source archive or add a ROM.
"""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
Q=R/'docs/qa/checkpoints/2026-10-30/ff-selector-and-palette-protocol-audit'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not Q.exists()
    packets=[('ff-graphics-bank-proposal-v2','handoff.json','39c9db81d773680680bad546d378f6ed5eda4a8e16363f1cadc08455d3020fa0'),
        ('ff-fx-sword-role-audit-v1','controls.json','b38d1c10e0c2b1fb6b97eb78691029617fc964d4311398bb0055f907f3afa071'),
        ('ff-fx-palette-mailbox-audit-v2','controls.json','2fd5b2e0f94a741ca88f1a94427ca849b84bb31a812296e00f5fac407d8a9f36')]
    files={Path(__file__)};summaries=[]
    for folder,name,want in packets:
        p=R/'build'/folder/name;assert sha(p)==want,p
        h=json.loads(p.read_text());assert h['passed']
        for n,v in h['bindings'].items():assert sha(n)==v,n
        own=[Path(n)for n in h['bindings']if any(t in Path(n).name for t in['ff_graphics_bank','ff_fx_sword_role','ff_fx_palette_mailbox'])]
        files|=set(own)|{f for f in p.parent.iterdir()if f.is_file()}
        summaries.append(dict(packet=str(p),sha256=sha(p),verified_bindings=len(h['bindings'])))
    Q.mkdir(parents=True);archive=Q/'delta-source-and-controls.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
        for p in sorted(files):
            assert p.suffix.lower()!='.nes'
            z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for n in z.namelist():assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
        members=len(z.namelist())
    receipt=dict(status='SOURCE_SELECTOR_FIX_AND_UNSAFE_MAILBOX_NEGATIVE_RETAINED',native=False,installed=False,
        selector_candidate_sha256='6fc2bb8e8a0cd0d3d88cb334b370b7ba31e8dc9f0b44258d2a2219649759fb3f',
        parent_native_flash_sha256='6798b7458a8fef799b0836a5baf4e5df61e0fc46f2e4b639d68f8e7e2186a6c5',
        parent_source_checkpoint='docs/qa/checkpoints/2026-10-30/ff-native-enemy-flash',packets=summaries,
        findings=['One-byte FF resident graphics row FF→DD:16384 actual selectors,64 complete Main pairs,28 real vector cuts pass; all other ROM bytes/PCs/header/CHR/RAM3/cookie exact.',
            '576 original iterator views prove body0,sword2 and ink3 separate complete records. Sword uses all3 indices with [0C,1C,2C], distinct from Ice/White; recoloring is not an exact port.',
            'Existing palette mailbox flushes after native queue before OAM DMA, even when the native queue is full; lag retains packet.',
            'Two retained real retirement negatives show stale FF colors flush into Mario/Samus after selection. Alias adoption remains unsafe until lifecycle repair.',
            'No scheduler producer, mailbox alias, roster admission or Downloads change is adopted by this checkpoint.'],
        archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,archive_members=members,
        all_delta_members_verified=True,no_ROM_files=True,
        root_tool_sha256=sha(__file__))
    (Q/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(packets=len(packets),members=members,bytes=archive.stat().st_size,
        bindings=sum(x['verified_bindings']for x in summaries))),flush=True)


if __name__=='__main__':main()
