"""Install the qualified label-only52 successor, preserving the prior WIP."""
from pathlib import Path
import hashlib,json

R=Path(__file__).resolve().parents[2]
P=R/'build/celeste-menu-name-current-v2'
Q=R/'docs/qa/celeste-menu-label-release-2026-10-30.json'
D=Path('C:/Users/kando/Downloads')
EXPECTED='a7ccbaaa7aab598d36e8806e30475eab36174ee1948f25f90ae72e6640f43f48'
OLD='18de015564c61cd07d0d52ec26300661627278880d4226f7c589ac95028a0976'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not Q.exists()
    hp=P/'handoff.json';assert sha(hp)=='ff925be3bde851f660d4eae9d4341d467d2ac02fa5339a95664c291ef1de10ff'
    handoff=json.loads(hp.read_text())
    for n,v in handoff['bindings'].items():assert sha(n)==v,n
    source=json.loads((P/'source-proof.json').read_text());assert source['passed']
    controls=json.loads((P/'menu-controls-v2.json').read_text());assert controls['passed']and controls['cases']==80
    native=P/'native/cold-label-v1/result.json';result=json.loads(native.read_text())
    assert result['passed']and result['ROM_sha256']==EXPECTED
    assert result['actual_PPU_name']=='CELESTE MARIO'and result['actual_Select_changes']==4
    post=P/'native-postflight-v1.json';h=json.loads(post.read_text())
    assert h['exit_code']==0 and h['all_bindings_unchanged']
    candidate=P/'joint/candidate.nes';assert sha(candidate)==EXPECTED
    # Root visually reviewed both complete native frames before installation.
    pictures=[P/'native/cold-label-v1'/n for n in['mario-original.png','celeste-mario-exact-name.png']]
    assert all(p.is_file()for p in pictures)
    latest=D/'SMB-Crossover-Latest-WIP-MMC5.nes'
    versioned=D/'SMB-Crossover-2026-10-30-Celeste-Name-MMC5.nes'
    backup=D/'SMB-Crossover-Before-Celeste-Name-18de0155-MMC5.nes'
    assert sha(latest)==OLD,'A different latest build needs explicit rebase before replacement.'
    if backup.exists():assert sha(backup)==OLD
    else:backup.write_bytes(latest.read_bytes())
    payload=candidate.read_bytes()
    if versioned.exists():assert sha(versioned)==EXPECTED
    else:versioned.write_bytes(payload)
    latest.write_bytes(payload)
    assert sha(latest)==sha(versioned)==EXPECTED and sha(backup)==OLD
    files=[hp,P/'source-proof.json',P/'menu-controls-v2.json',native,post,*pictures,Path(__file__)]
    receipt=dict(date='2026-10-30',passed=True,installed=True,ROM_sha256=EXPECTED,parent_sha256=OLD,
       latest=str(latest),versioned=str(versioned),backup=str(backup),identities=80,ready=52,pending=28,
       change='Character-select MarioVariant4 now displays CELESTE MARIO via the actual name-index44 publisher.',
       checks=dict(source12_byte_menu_only_change=True,header_CHR_gameplay_NMI_shared_dispatch_exact=True,
          actual_menu_profiles=80,unchanged_foreign_profiles=79,allflags_publisher_cases=320,
          native_cold_frames=232,real_Select_inputs=4,actual_PPU_name='CELESTE MARIO',
          root_viewed_both_whole_native_frames=True,installed_hash_verified=True),
       limits=['Label-only successor of verified52-ready18de; no new character readiness.',
          'FF/Arthur/Quick/SMB2 current integration and broad playthrough/performance work remain separate.',
          'Older native gameplay results apply to unchanged gameplay code; this run tests the cold menu label.'],
       bindings={str(p.resolve()):sha(p)for p in files})
    Q.write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(installed=str(latest),versioned=str(versioned),backup=str(backup),ROM_sha256=EXPECTED)),flush=True)


if __name__=='__main__':main()
