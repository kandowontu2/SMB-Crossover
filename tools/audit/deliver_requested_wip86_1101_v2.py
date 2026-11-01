"""Deliver the user's requested current selectable WIP, without completion claims."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from build_storage_guard_v1 import preflight

R=Path(__file__).resolve().parents[2]
J=R/'build/karnov-host-resource-base-1101-v1'
O=R/'build/karnov-requested-wip-native-1101-v2'
DEST=R/'docs/qa/checkpoints/2026-11-01/requested-wip86-native-v2'
EXPECTED='be751275d00757ecaa51defcd2ccd5ea235921aa4b1f34337fa6c5c6e1877962'
PREVIOUS='e40109ff598e060a4ad384a7cf77bafccfefbe2efa79599f817f832c93fca019'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def validate(q):
    for n,h in q.get('bindings',{}).items():
        p=Path(n);p=p if p.is_absolute() else R/p
        assert sha(p)==h,p


def pack(path,files):
    manifest={n:dict(sha256=sha(p),bytes=p.stat().st_size,original=str(p.resolve())) for n,p in files.items()}
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,p in sorted(files.items()):z.writestr(n,p.read_bytes())
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert path.stat().st_size<600000
    return dict(path=path.relative_to(R).as_posix(),sha256=sha(path),bytes=path.stat().st_size,members=len(files)+1)


def main():
    preflight(private_root=O,reserved_bytes=1600000,reserved_files=7,fresh=True)
    assert not DEST.exists() and not (O/'binding.json').exists()
    assert sha(J/'candidate.nes')==EXPECTED
    assembly=json.loads((J/'terrain-assembly.json').read_text())
    carry=json.loads((J/'compact-carry-controls.json').read_text())
    for q in [assembly,carry]:
        assert q['passed'] and q['ROM_sha256']==EXPECTED
        validate(q)
    assert carry['all_other_private_ROM_bytes_exact'] and carry['delivered_compact_menu_exact']
    child=O/'opening'
    ready=json.loads((child/'ready.json').read_text());validate(ready)
    binding=json.loads((child/'capture/binding.json').read_text())
    native=json.loads((child/'capture/result.json').read_text())
    assert binding['exit_code']==0 and binding['ready_sha256']==sha(child/'ready.json')
    assert native['passed'] and native['ROM_sha256']==binding['ROM_sha256']==EXPECTED
    assert native['Main']==288 and native['jumped'] and native['landed'] and native['background_checks']==422
    assert native['ISR_returns']>=1200 and native['source_weapons']==288
    captures=[p for p in child.rglob('*') if p.is_file()]
    assert len(captures)<=64 and sum(p.suffix=='.png' for p in captures)<=4
    assert sum(p.stat().st_size for p in captures)<128000000
    # Read only the immediate source manifest; never expand dependency graphs.
    prior=R/'docs/qa/checkpoints/2026-11-01/karnov-menu-native-component-v1/source-proof.zip'
    with zipfile.ZipFile(prior) as z:old_manifest=json.loads(z.read('files.json'))
    # Historical CPU receipts target f1fade, so they are not proofs of this ROM.
    sources={n:Path(q['original']) for n,q in old_manifest.items() if not n.endswith('.json')}
    for n in ['main-build.json','link.json','terrain-main-build.json','terrain-kernel-build.json','terrain-first-link.json','terrain-images-build.json','terrain-final-link.json','ingress-union-build.json','terrain-assembly.json','compact-carry-before.json','compact-carry-controls.json']:
        sources['host/'+n]=J/n
    for n in ['carry_karnov_compact_menu_1101_v2.py','deliver_requested_wip86_1101_v2.py']:
        sources['tools/audit/'+n]=R/'tools/audit'/n
    sources['host/render-art.json']=J/'render-art.json'
    DEST.mkdir()
    source=pack(DEST/'source.zip',sources)
    native_packet=pack(DEST/'native-results.zip',{'opening/'+p.relative_to(child).as_posix():p for p in captures})
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    previous=sha(nightly);assert previous==PREVIOUS
    # Explicit user request: replace this file directly and create no backup.
    shutil.copyfile(J/'candidate.nes',nightly)
    assert sha(nightly)==EXPECTED
    result=dict(passed=True,installed=True,backup_created=False,user_requested_WIP=True,
        destination=str(nightly),output_sha256=EXPECTED,replaced_sha256=previous,
        selectable_identities=86,previously_verified_identities=85,total_menu_identities=90,
        new_identities=['Karnov'],selection='Rygar -> Select -> Karnov -> Start',
        complete=False,complete_character=False,source=source,native=native_packet,
        checkpoint=DEST.relative_to(R).as_posix(),
        verification=dict(ROM_sha256=EXPECTED,scope='Exact-candidate controller boot/menu/lives/game opening, body pixels, jump/landing, source projectile updates, camera, backdrop and ISR returns. All old private bytes outside menu+cookies exact; compact menu code exact to prior delivered repair.',
            Main=native['Main'],video_frames=native['frames'],ISR_returns=native['ISR_returns'],
            source_movement=native['source_movement'],source_weapons=native['source_weapons'],
            maximum_camera=native['maximum_camera'],maximum_projectiles=native['maximum_projectiles'],
            background_checks=native['background_checks'],jumped=True,landed=True),
        pending=['Karnov enemy/block combat, injury/death, pickups, stomp rebound, equipment and original audio are incomplete.','Metal Storm, Shinobi and Excitebike are isolated source components, not selectable ROM characters yet.','No full1-1/shortcut/all-powerup, full-roster campaign or constant60Hz claim.'],
        delivery_policy='The user explicitly requests access to the same selectable WIP used for testing. Publish integrated WIP without withholding it for complete-character qualification.',
        storage=preflight(fresh=True))
    (DEST/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (DEST/'README.md').write_text('''# Requested current WIP: 86 selectable identities

Downloads now contains the same selectable Karnov WIP used for testing, with
the latest compact WWF menu repair carried over. On Rygar, press Select to
choose Karnov, then Start. The previous 85 identities remain selectable.

The exact installed ROM passed a controller-only opening with 288 Main updates,
original body display, jump/landing, source shots, camera movement, backdrop
restoration and 1,275 interrupt returns. The menu bytes match the previously
tested compact repair; every other byte of the prior Karnov WIP is unchanged
except its two authentication cookies.

Karnov is unfinished. Enemy/block combat, injury/death, pickups, stomp rebound,
equipment and original audio remain incomplete. This is access to work in
progress, not a complete-character or full-stage qualification. Metal Storm,
Shinobi and Excitebike have source components but no selectable host integration.

The native result's older wording says "not nightly admission": that describes
its limited test scope. The user has now explicitly requested this WIP despite
those limits. Downloads was replaced directly, with no backup. Start fresh
rather than loading a save state from an earlier ROM.

The source packet contains current sources/build recipes and only current build
receipts. Older CPU matrices target f1fade and remain historical in their prior
checkpoint; they are not relabeled as tests of this candidate.
''',encoding='utf-8')
    (O/'binding.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    state_path=R/'docs/qa/continuation-current.json'
    state=json.loads(state_path.read_text(encoding='utf-8'))
    old=state['installed_nightly']
    state['current_priority']='User explicitly requests the same selectable WIP as testing. Delivered merged86 Karnov+compact menu be7512... directly to Downloads, no backup. Karnov is selectable via Rygar/Select; combat, injury/death, pickups, rebound, equipment/audio remain incomplete. Three agents are implementing isolated health/pickup/combat components. Continue source integration and publish subsequent integrated WIP promptly; do not withhold it for complete-character qualification. Preserve remaining roster/campaign/playthrough objectives.'
    state['installed_nightly']=result
    state['previous_qualified_nightly']=old
    state['WIP_access_policy']=result['delivery_policy']
    state_path.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['storage']}))


if __name__=='__main__':main()
