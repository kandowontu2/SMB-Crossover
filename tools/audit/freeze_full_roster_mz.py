"""Publish the verified32-identity MMC5 roster and honest feature limits."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification/final-roster-mz';O=R/'build/checkpoints/full-roster-mz'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def main():
    assert not O.exists()
    parent=read(R/'build/checkpoints/level-roster-mx/manifest.json');rom=V/'full-roster.nes';digest=sha(rom)
    assert digest=='043b1368b7ff41ca7d61d830c5d19b29bea69f37be657a594878711cbcc39764'
    matrix=read(V/'roster-v2/results.json');features=read(V/'feature-native-results.json');adapters=read(V/'adapter-native-results.json')
    assert matrix['identities']==32 and matrix['rom_sha256']==digest and all(x['exit']==0 for x in matrix['results'].values())
    assert features['sha256']==digest and len(features['results'])==14 and all(x==0 for x in features['results'].values())
    assert adapters=={'bounce':0,'outline-mike':0,'outline-samus':0}
    abi=read(V/'public-ABI.json');outline=read(V/'outline/outline-cpu-proof.json');bounce=read(V/'bounce/component-proof.json');nativebounce=read(V/'bounce/build/verification/full-roster-bounce.json')
    assert abi['passed'] and abi['sha256']==digest and outline['candidate_sha256']==digest and bounce['passed'] and bounce['ROM_sha256']==digest
    assert nativebounce['passed'] and nativebounce['arenas']==30
    mac=read(V/'mac/component-proof.json');mike=read(V/'mike/native-owner-terrain.json')
    assert mac['sha256']==digest and mike['candidate_sha256']==digest
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')};paths['mmc5-expanded']=rom
    assert all(sha(paths[m])==parent['ROMs'][m] for m in ('mmc3','mmc5'))
    # Level packet's complete cold bank and its original C wrapper are exact.
    old=(R/'build/checkpoints/level-roster-mx/build/smb-crossover-mmc5-expanded.nes').read_bytes();raw=rom.read_bytes()
    assert old[16+26*8192:16+27*8192]==raw[16+26*8192:16+27*8192]
    proof=dict(ROM_sha256=digest,identities=32,portraits=19,rows=[6,6,7],matrix=matrix,feature_results=features['results'],native_adapters=adapters,native_spring_stomp=nativebounce,public_ABI=abi,outline_cases=outline['cases'],bounce_components=bounce['counts'],Mac_components=mac,Mike_components=mike,level_cold_PRG26_exact_MX=True,video_work_deferred=True,campaign_verified=False,
      harness_revisions=[
       'Bass strict physical-entry C-bank assertion was too strong when NMI fell between shadow publication and the hardware write. The retained witness proves it; final matrix decodes the pending write and checks restoration of the logical bank and all shared operands. ROM unchanged.',
       'Kirby fixed-frame approach ended at332 instead of334. Final fixture checks the actual question-column bounds, records the stopped origin, and asserts no movement throughout ceiling contact; physical emergence and palette assertions retained. ROM unchanged.',
       'Platform fixture inferred mapper from filename; final neutral name incorrectly selected MMC3 tiles. Final fixture explicitly checks the MMC5 tile, preserving width/carry assertions. Rejected syntax revision retained. ROM unchanged.'],
      scope='Focused source, compiled-component and native emulator checks. Seeded arenas stay labeled. No full-campaign, physical-cartridge or video-review certification.')
    (V/'completion-evidence.json').write_text(json.dumps(proof,indent=2)+'\n')
    text=(R/'README.md').read_text().replace('build/checkpoints/level-roster-mx','build/checkpoints/full-roster-mz')
    anchor='The workspace has a **30 GB limit**.'
    pos=text.index(anchor)
    text=text[:pos]+'All **32 identities** pass cold controller selection, alternate persistence, highlighted-name checks and bounded World 1-1 movement. The final combined build also passes focused character-specific pickup/combat/death checks, 30 real spring/stomp arenas, and native platform carrying with Mac and Mike. New character IDs use a bounded outline lookup; Mac uses the native world palette for blocks and mushrooms. The frozen manifest records exact ROM hashes, test scope and remaining differences.\n\n'+text[pos:]
    (R/'README.md').write_text(text)
    changes=[read(R/'build/verification/outline-adoption-my/adoption.json'),read(R/'build/verification/bounce-adoption-my/adoption.json')]
    names=set(parent['source_files'])
    for a in changes:names.update(a['after']);names.update(a.get('owned',{}))
    names.update(['tools/audit/adopt_outline_my.py','tools/audit/adopt_bounce_my.py','tools/audit/check_final_adapters_mz.py','tools/audit/check_character_features_mz.py','tools/audit/freeze_full_roster_mz.py','tools/audit/archive_capture_headroom_na.py','docs/qa/expanded-bounce-adapter-private-2026-10-23.md','tests/full-roster-entry.lua','tools/audit/check_full_roster_entry.py'])
    # Current source is packaged after documentation updates; compiled sources
    # and prepared assets were unchanged throughout the final admission.
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for mapper,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext);dest.parent.mkdir(exist_ok=True);shutil.copyfile(path.with_suffix(ext),dest);shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(parent,status='ALL_REQUESTED_CHARACTER_IDENTITIES_ADDED_AND_VERIFIED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint='level-roster-mx',ROMs={m:sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},source_zip_sha256=sha(O/'source.zip'),remaining_profiles=[],completion_evidence=proof,scope=proof['scope'])
    report['limitations']=[x for x in parent['limitations'] if not x.startswith(('New-profile spring/stomp adapter','CV3 original36px'))]
    report['limitations'].append('All32 identities are playable; source-game equivalence remains limited by the declared audio, graphics, equipment and SMB adaptations. This release does not claim complete campaigns or original-game perfection.')
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');(R/'build/verification/root-current60-complete-mz.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],source_zip_sha256=report['source_zip_sha256'],identities=32,portraits=19)))

if __name__=='__main__':main()
