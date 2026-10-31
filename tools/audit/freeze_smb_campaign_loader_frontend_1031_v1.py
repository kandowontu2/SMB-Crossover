"""Freeze the private three-campaign frontend/data loader and precise limits."""
from pathlib import Path
import hashlib,json,zipfile

R=Path(__file__).resolve().parents[2]
S=R/'build/smb2j-cache-loader-source-1031-v3'
DATA=R/'build/smb2j-campaign-data-1031-v2'
N=R/'build/smb2j-cache-loader-native-1031-v1/peach'
CHECKS=[R/'build/smb2j-cache-loader-controls-1031-v2/controls.json',
        R/'build/smb2j-campaign-menu-controls-1031-v5/controls.json']
D=R/'docs/qa/checkpoints/2026-10-31/smb-campaign-loader-frontend-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert not D.exists()
    stage=json.loads((S/'source-stage.json').read_text())
    result=json.loads((N/'capture/result.json').read_text())
    assert stage['passed']and result['passed']and not result['SMB2J_implemented']
    assert stage['candidate']==result['ROM_sha256']=='6f9f2936d9b859f81b1965d1c43022027f53220be878d79a902aa0bd86b9fbf3'
    bound={}
    receipts=[S/'source-stage.json',DATA/'data-stage.json',*CHECKS,N/'ready.json',N/'capture/binding.json']
    for p in receipts:
        q=json.loads(p.read_text())
        if'passed'in q:assert q['passed']
        for name,expected in q['bindings'].items():
            assert sha(name)==expected,name
            bound[name]=expected
    assert json.loads((N/'capture/binding.json').read_text())['exit_code']==0
    assert len(list((N/'capture').glob('*.png')))==4
    refs=[Path(__file__),*receipts,DATA/'catalog.json',N/'controller.lua',N/'run.py',
          *sorted((N/'capture').glob('*')),S/'joint/entrypoint.s',S/'joint/candidate.cfg',S/'joint/carrier.s',
          *sorted((S/'joint/src').glob('*.s')),*sorted((S/'joint/src').glob('*.inc')),
          *sorted(S.glob('*.json'))]
    names=['pack_smb2j_campaign_data_1031_v1.py','pack_smb2j_campaign_data_1031_v2.py',
           'check_smb2j_cache_decoder_1031_v1.py',
           'prepare_smb2j_cache_loader_1031_v1.py','prepare_smb2j_cache_loader_1031_v2.py','prepare_smb2j_cache_loader_1031_v3.py',
           'qualify_smb2j_cache_loader_1031_v1.py',
           'check_smb2j_cache_loader_1031_v1.py','check_smb2j_cache_loader_1031_v2.py',
           'check_smb2j_campaign_menu_1031_v4.py','check_smb2j_campaign_menu_1031_v5.py']
    refs += [R/'tools/audit'/name for name in names]
    refs += [R/'tools/reference'/name for name in ['smb2j_cache_decoder_1031_v1.inc',
             'smb2j_cache_loader_1031_v1.inc','smb2j_cache_loader_1031_v2.inc',
             'smb2j_campaign_menu_1031_v6.inc','smb2j_campaign_menu_1031_v7.inc']]
    refs += [R/'build/smb2j-cache-decoder-1031-v1/controls.json',
             R/'build/smb2j-cache-loader-qualified-1031-v1/source-stage.json',
             R/'build/smb2j-cache-loader-controls-1031-v1/controls.json',
             R/'build/smb2j-campaign-menu-controls-1031-v4/controls.json',
             R/'build/smb2j-cache-loader-source-1031-v1/main-build.json']
    refs=sorted(set(refs))
    assert all(p.suffix.lower()not in ['.nes','.fds','.chr','.bin','.o','.exe','.dbg']for p in refs)
    D.mkdir(parents=True)
    save(D/'scope.json',dict(status='ACTIVE_INCOMPLETE',passed=True,installed=False,
         candidate=stage['candidate'],choices=['SUPER MARIO BROS.','SUPER MARIO BROS 2J','ALL NIGHT NIPPON'],
         actual_frontend='All three names/cursor positions render. B preserves selected character/alternate. Only SMB1 launches gameplay.',
         data='Four lossless original2J data caches include71 reachable profile-areas/93 world-area pairs,80 active-world pipe links and all52 numbered stages.',
         source_checks='All86 menu identities,74 ready,12 pending;2048 continue/reset/guard cases each;340 queue bounds.',
         loader_checks='24 actual source-linked buffered-PPU loader cases across4profiles/control increments/wide CHR; every8192bytes and full16byte cookie; six rejection/readback cases.',
         native='Cold controller-only Peach: all3 choice screens, real forcedblank profile0 load into physicalRAM4 with every byte checked, blocked ANN launch, B return and180actual SMB1 Main updates. Four reviewed PNGs, no RAM pokes/video.',
         private_resources=stage['root_private_grant'],private_header_WRAM_KiB=64,
         actual_resident_bytes=452,remaining_resident_bytes=2060,
         new_campaigns_playable=False,save_persistence=False,
         required_next=['Connect cache-backed world/area and terrain/enemy parser entrypoints.',
                        'Port2J-specific objects/contact/graphics, wind/poison/plants/springs, progression/warps and endings.',
                        'Implement original9/A-D/star/save rules and campaign-aware cheats/lifecycle.',
                        'Add ANN original data/art/protocol and progression, preserving its differences from2J.',
                        'Verify complete campaigns and guest compatibility.'],
         negatives=['Loader-v1 had an out-of-range branch and never linked.',
                    'Loader-v2 linked correctly but its diff assertion omitted the genuine frontend farcall operand rebind; the separate qualification proves the exact change.',
                    'Menu-controls-v4 expected15 glyphs for ALL NIGHT NIPPON; its actual auto-sized command is16. v5 uses the string length.',
                    'No failed candidate was installed.'],
         storage='Native preflight measured60,056,414,496 workspace bytes under70,000,000,000. No capture movies or frame forests.'))
    refs.append(D/'scope.json')
    members={p.relative_to(R).as_posix():sha(p)for p in refs}
    with zipfile.ZipFile(D/'source-and-native.zip','x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in refs:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(D/'source-and-native.zip')as z:
        for n,h in members.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    save(D/'source-members.json',members)
    save(D/'handoff.json',dict(passed=True,source=True,bounded_native=True,installed=False,
         campaign_complete=False,candidate=stage['candidate'],parent=stage['parent'],
         archive_bytes=(D/'source-and-native.zip').stat().st_size,archive_members=len(members),
         archive_sha256=sha(D/'source-and-native.zip'),
         bindings={**bound,**{str(p.resolve()):sha(p)for p in refs}}))
    (D/'README.md').write_text(
        '# Three-campaign frontend and data loader\n\n'
        'The private candidate displays SMB1, SMB2J and All Night Nippon.86 menu identities '
        'remain unchanged. A cold controller-only emulator sequence verifies the three '
        'screens, a full8KiB original2J data transfer into separate physicalRAM4, return '
        'to the selected Peach alternate and normal SMB1 startup/gameplay. All four '
        'data profiles also pass the source-linked buffered-PPU decoder/loader checks.\n\n'
        'This candidate is not installed. SMB2J and ANN gameplay remain deliberately '
        'unavailable: their parsers, additional mechanics, progression, saves and '
        'endings still need integration and native checks. The private candidate '
        'uses64KiB volatile WRAM; persistent saves are not implemented. It does not '
        'claim physical-cartridge compatibility from emulator tests alone.\n',encoding='utf-8',newline='\n')
    owned=[p.relative_to(R).as_posix()for p in refs if p.is_relative_to(R/'tools')]
    owned += [p.relative_to(R).as_posix()for p in D.iterdir()if p.is_file()]
    owned.append((D/'owned-files.json').relative_to(R).as_posix())
    save(D/'owned-files.json',dict(files=sorted(set(owned))))
    print(json.dumps(dict(passed=True,installed=False,candidate=stage['candidate'],
         handoff_sha256=sha(D/'handoff.json'),archive_bytes=(D/'source-and-native.zip').stat().st_size)))


if __name__=='__main__':main()
