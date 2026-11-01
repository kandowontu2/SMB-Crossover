"""Preserve exact compact-roster source components without old proof forests."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/wwf-roster-source-checkpoint-1101'
D=R/'docs/qa/checkpoints/2026-11-01/wwf-roster-compact-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    assert not O.exists()and not D.exists()
    roots=[R/'build/wwf-roster-package-1101-v1',R/'build/wwf-roster-decoder-1101-v1',R/'build/wwf-audio-source-1101-v1',R/'build/wwf-audio-private-1101-v2']
    receipts=[]
    for root,name in zip(roots,['source-package.json','source-controls.json','source-controls.json','source-controls.json']):
        path=root/name;q=json.loads(path.read_text());assert q['passed']and q.get('native')is False
        for p,h in q['bindings'].items():assert sha(p)==h,p
        receipts.append(dict(path=str(path.relative_to(R)),sha256=sha(path)))
    audio=json.loads((roots[3]/'source-controls.json').read_text())
    assert audio['driver_and_scratch_bytes']==8088
    files={Path(__file__)}
    files|={R/'tools/audit'/n for n in['prepare_wwf_roster_package_bounded_v1.py','check_wwf_roster_decoder_bounded_v1.py','port_wwf_audio_source_bounded_v1.py','port_wwf_audio_private_bounded_v2.py']}
    files|={R/'tools/reference'/n for n in['wwf_roster_pose_decoder_v1.s','wwf_audio_virtual_read_v1.s','wwf_audio_virtual_read_v2.s']}
    for root in roots:files|={p for p in root.iterdir()if p.is_file()}
    assert len(files)<64 and sum(p.stat().st_size for p in files)<2_000_000
    O.mkdir();D.mkdir(parents=True)
    with zipfile.ZipFile(D/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    summary=dict(passed=True,source_CPU=True,native=False,installed=False,parent_nightly='28693c0bf61926f5bef62511b5da0b71f97543170d27d0e03e59bb5e70edf0ca',
                 pose_rasters=195,face_rasters=390,decoder_cases_with_clamps=688,decoder_bytes=211,pose_buffer_bytes=69,private_C2_growth=5,
                 metadata_and_cookie_slot_bytes=8182,largest_metadata_bytes=1685,existing_metadata_slot=1687,
                 audio=dict(bytes=8088,private_bank_scratch_bytes=10,native_pointer_bytes_borrowed_and_restored=2,host_global_or_ZP_growth=0,themes=6,ticks_per_theme=2400,max_original_cycles=max(r['original_cycles'][1]for r in audio['rows']),max_private_port_cycles=max(r['private_cycles'][1]for r in audio['rows'])),
                 storage=dict(available_owner_pages=115,body_pages=84,common_C2_nonzero_pages=5,common_A3_pages=8,audio_pages=8,metadata_pages=8,total=113,spare=2,zero_C2_pages=[0,1,3],optional_shared_zero_page_uses_one_spare=True),
                 receipts=receipts,archive=dict(path=str((D/'source.zip').relative_to(R)),sha256=sha(D/'source.zip'),bytes=(D/'source.zip').stat().st_size,members=len(files)),
                 limits=['No change to installed76-character ROM or menu admission','Final loader, per-variant cookies, graphics page mapping, palettes, HUD names and menu/lives portraits still need integration','Actual69-byte conditional C2 allocation and all referring source objects must be linked together; current standalone decoder uses its new source layout','Audio bank proof does not establish nativeNMI/SFX mixing, audible playback or60Hz; its worst-case CPU cost must be measured after integration','All original goal characters, full1-1/shortcut and every-powerup tests remain required'])
    save(D/'handoff.json',summary);save(O/'result.json',summary)
    (D/'README.md').write_text('''# Complete WWF roster: compact source components

This is preparation for all six wrestlers. The installed nightly remains the
76-character28693c0b build; the other five wrestlers are still coming soon.

The new source package preserves all195 original poses and both facings. Its
group directory supports all original frames, including the six-frame groups.
Packed tile/role bytes and implicit group counts reduce all six metadata sets
plus reserved cookie slots to8182 bytes. The largest individual metadata set
is1685 bytes, fitting the existing1687-byte selected slot.

The actual6502 decoder passes688 pose/facing/clamp cases. Those tests caught
Bam Bam's17-cell poses overwriting the old64-byte buffer. A69-byte buffer fixes
the overwrite and grows the conditional WWF layout by five bytes. This changed
layout is source-tested; it is not yet linked into the host ROM.

The original music driver is relocated as actual6502 code. All16 command
handlers are recovered from source control flow. All six themes pass2400ticks
each with identical ordered APU writes, channel state and return registers.
The current8088-byte version keeps its ten scratch bytes in its own RAM bank,
restoring the host's two borrowed pointer bytes after every indirect read.
It leaves104 bytes in its8KiB bank. NativeNMI routing, sound-effect priorities,
audible playback and performance remain unverified. Worst-case source timing
is in the handoff; do not describe this as a60Hz result.

The measured storage plan uses113 of115 existing owner pages, preserving
Thomas's16 pages. Three common C2 pages are zeros. A single shared zero page
can simplify the loader while still leaving one spare page. This is a storage
fit, not a completed loader or a native playable-roster qualification.

Next: source-link the conditional layout, shared sparse cache, per-wrestler
metadata/cookies, cold portraits, palette/HUD tables and original theme routing
onto28693c0b. Retain the character-select timing repair. Validate every real
Select/Start transition, original-source movement/attacks and native graphics,
interrupts, scrolling and contacts before enabling the five menu alternates.
Then replace the one Downloads nightly without a backup and push the results.
''',encoding='utf-8')
    note=R/'docs/qa/continuation-current.json';q=json.loads(note.read_text())
    q['previous_goal_turn_classification']='progress'
    q['current_priority']='Integrate the complete source-tested WWF roster package,69-byte pose buffer and8088-byte original theme driver onto current28693c0b; validate before unlocking the five remaining WWF alternates.'
    q['WWF_roster_source_next']=dict(checkpoint=str(D.relative_to(R)),checkpoint_sha256=sha(D/'handoff.json'),output_roots=[str(p.relative_to(R))for p in roots],installed=False,summary=summary)
    save(note,q)
    print(json.dumps(dict(checkpoint=str(D.relative_to(R)),source_only=True,installed_nightly_unchanged=True,archive_bytes=(D/'source.zip').stat().st_size)))


if __name__=='__main__':main()
