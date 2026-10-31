"""Preserve source-recovered forms and native donor selection observations."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/smb3plus-original-characters-1030-v1'
D=R/'docs/qa/checkpoints/2026-10-30/smb3plus-original-toad-peach-source'
P=R/'build/peach-palette-fix-1030-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    h=json.loads((O/'source-proof.json').read_text())
    assert sha(O/'source-proof.json')=='acb8d6bc184e76d6e037f12cb04f6e93acf2afb497ca29a092ca329aafc18034'
    for p,s in h['bindings'].items():assert sha(p)==s,p
    assert h['CHR_pages_required']==50 and h['draw_cases']==3402 and not h['installed']
    parent=(P/'joint/candidate.nes').read_bytes()
    before=parent[16+128*8192+969*1024:16+128*8192+1019*1024]
    assert before==bytes(50*1024)
    cfg=(P/'joint/private.cfg').read_text()
    assert 'UNALLOCATED_CHR_MEM:start=$e1400,size=$1ec00' in cfg
    files={p for p in O.iterdir()if p.is_file()}
    files|={Path(__file__),R/'tools/audit/recover_smb3plus_characters_1030_v1.py'}
    for i in range(1,6):files.add(R/f'tools/audit/prepare_smb3plus_donor_native_1030_v{i}.py')
    files|={R/'tools/reference/smb3plus_donor_discovery_1030_v1.lua',R/'tools/reference/smb3plus_donor_discovery_1030_v2.lua'}
    for name in ['toad','peach']:
        folder=Path(h['native_donor_selection'][name]['packet'])
        files|={p for p in folder.rglob('*')if p.is_file()}
    # Keep the ineffective-input and first parse-error evidence as limitations,
    # rather than presenting those earlier observation runs as valid controls.
    for name in ['smb3plus-donor-native-1030-v1','smb3plus-donor-native-1030-v4']:
        folder=R/'build'/name/'discovery'
        files|={folder/'ready.json',folder/'controller.lua'}
        files|={p for p in (folder/'capture').iterdir()if p.suffix in ['.log','.csv']}
    assert all(p.resolve().is_relative_to(R)and p.suffix.lower()not in ['.nes','.exe','.o','.dbg','.lbl','.map']for p in files)
    assert sum(p.stat().st_size for p in files)<8*1024*1024
    D.mkdir(parents=True)
    archive=D/'source-and-donor-observations.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    shutil.copy2(O/'source-proof.json',D/'source-proof.json')
    shutil.copy2(O/'source-forms.png',D/'source-forms.png')
    d=dict(source=True,host=False,native_host=False,installed=False,
        current_installed_ROM_sha256=hashlib.sha256(parent).hexdigest(),playable_unchanged=64,
        source_proof_sha256=sha(O/'source-proof.json'),draw_cases=3402,
        geometry_pairs=2268,palette_cases=72,original_body_CHR_pages=50,
        private_root_resource_bound=dict(begin=969,end_exclusive=1019,
            prior_owner='Existing UNALLOCATED_CHR_MEM',original_fill=0,original_bytes=len(before),
            original_sha256=hashlib.sha256(before).hexdigest(),
            preserves='Benj901..<915, Battletoads915..<927, Bowser927..<935, ContraForce935..<969.'),
        remaining_unassigned_tail='1019..<1024',
        archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
        members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)},
        limits=h['limits'])
    (D/'receipt.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
    (D/'README.md').write_text('Infidelity SMB3+ Toad/Peach source recovery, not an unlock. Native controller-only observations confirm the donor\'s real character state at0119/011E, Toad2 andPeach3. The source renderer executes3402 controlled form/frame/facing cases;2268 Toad/Peach geometry pairs match the donor Mario records. Its genuine palette helper executes72 character/player/form cases. All original regular body pages plus five explicit special-page readers per character are retained:50CHR pages total, not the initial40-page estimate. The contact sheet uses source pixels and numeric palette roles; RGBs are display approximations.\n\nThe first Lua fixture had a parse error. Early startFrame-only input was ineffective; these observation runs are not accepted as controller evidence. The later inputPolled fixture reaches and changes the actual donor selection; relevant failures and ineffective-input logs are retained. No new video, savestate patch or per-frame capture forest.\n\nThe private root resource bound969..<1019 follows the separately reviewed ContraForce935..<969 grant. No current ROM/menu is changed. Translation of the source kick/float, growth and special-form behavior, native terrain/combat/lifecycle, menu admission and full campaign/powerup checks remain. The installed build is still64 playable identities.\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(checkpoint=str(D),archive_bytes=archive.stat().st_size,
        members=len(files),receipt_sha256=sha(D/'receipt.json'),installed=False)))


if __name__=='__main__':main()
