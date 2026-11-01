"""Freeze the two native rendering failures, their fixes, and nightly delivery."""
from pathlib import Path
import hashlib,json,zipfile,sys
R=Path(__file__).resolve().parents[2]
O=R/'build/thomas-native-render-review';D=R/'docs/qa/checkpoints/2026-10-31/thomas-native-pipe-graphics-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')


def bindings(value):
    for p,h in value['bindings'].items():assert sha(p)==h,p


def main():
    assert not O.exists()and not D.exists()
    native=R/'build/thomas-platform-native';component=R/'build/thomas-platform-chr';palette=R/'build/thomas-native-render'
    for p in [component/'source-stage.json',palette/'source-stage.json',palette/'boundaries/controls.json',palette/'source-route/controls.json',native/'ready.json']:
        bindings(read(p))
    result=read(native/'capture/result.json');record=read(native/'capture/binding.json')
    assert result['passed']and record['exit_code']==0
    assert record['ready_sha256']==sha(native/'ready.json')
    assert result['ROM_sha256']==sha(component/'candidate.nes')
    assert [p['pipe_X']for p in result['pipe_clears']]==[448,608,736,912]
    assert result['counters']['defeat']==3 and result['background_palette']==34 and result['inventory_HUD']==0
    assert result['body_DMA']['native_platform']['checks']>0
    assert result['counters']['vectors']>6000
    bad=read(R/'build/thomas-render-trace/capture/result.json');assert bad['background_palette']==15
    assert read(palette/'source-route/controls.json')['original_actor_frame_pairs']==2073
    nightly=read(R/'build/nightly-hogan75/installed.json')
    assert nightly['installed']and not nightly['backup_created']
    assert sha(nightly['destination'])==nightly['output_sha256']
    files=[Path(__file__)]
    for name in ['prepare_selected_native_packet_v1.py','prepare_thomas_native_bounded_v1.py',
                 'prepare_thomas_native_rendered_bounded_v1.py','prepare_thomas_native_platform_pixels_bounded_v1.py',
                 'prepare_thomas_render_trace_bounded_v1.py','fix_thomas_native_render_bounded_v1.py',
                 'fix_thomas_platform_chr_bounded_v1.py','check_thomas_render_boundaries_bounded_v1.py',
                 'check_thomas_render_route_snapshot_bounded_v1.py','publish_hogan_nightly_bounded_v1.py']:
        files.append(R/'tools/audit'/name)
    files.append(R/'tools/reference/thomas_native_bounded_v1.lua')
    for root,names in [
        (palette,['entrypoint.s','inventory.s','resident.s','tables.s','native-background-colors.bin','source-stage.json','final-link.json','boundaries/controls.json','source-route/controls.json','source-route/OAM.json']),
        (component,['resident.s','metadata.s','metadata.bin','carrier.s','carrier.chr','cookie.bin','native-background-colors.bin','source-stage.json','final-link.json']),
    ]:files += [root/n for n in names]
    for root in [R/'build/thomas-native-pipes',R/'build/thomas-render-trace',R/'build/thomas-render-fixed',R/'build/thomas-native-rendered-pipes',native]:
        files += [root/n for n in ['controller.lua','run.py','ready.json']]
        files += [p for p in (root/'capture').iterdir()if p.is_file()]
    files.append(R/'build/nightly-hogan75/installed.json');files=sorted(set(files))
    assert len(files)<120 and sum(p.stat().st_size for p in files)<4_000_000
    O.mkdir();D.mkdir(parents=True)
    archive=D/'evidence-and-sources.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    summary={k:v for k,v in result.items()if k not in ['body_DMA','poses']}
    q=dict(native=True,installed=False,candidate=sha(component/'candidate.nes'),native_summary=summary,
           original_pose_pixels_exact=42,native_platform_pixel_checks=result['body_DMA']['native_platform']['checks'],
           inventory_cases=1032,original_actor_pairs_on_palette_parent=2073,
           pixels_component_scope='Only pose metadata reindexing, one previously zero own art page and cookie digest differ from the actor-verified palette parent. Original actor/physics/kernel instruction bytes remain exact.',
           failures=['Original private build retained black lives background in gameplay and displayed legacy NORMAL inventory text.',
                     'After palette/inventory fixes, native platform tile5A still read Thomas art and appeared as six orange marks. Exact native OAM identified the owner.'],
           fixes=['Queue native universal background along with Thomas palette; use genuine area/background-control entries.',
                  'Decline legacy inventory for Thomas; other85 resolved identities preserve their previous predicate registers/flags in1032 total cases.',
                  'Derive three16row loader tables exactly to fund ROM space; resident1462/1478 and kernel6141/6144 remain within grants.',
                  'Keep native miscellaneous art in its own sprite window1. Original Thomas poses use windows0/2/3, at most three physical pages; all42 pixel/attribute/position inputs are exact.'],
           nightly=nightly,source_parent_checkpoint='docs/qa/checkpoints/2026-10-31/thomas-native-platform-source-v1/handoff.json',
           source_parent_sha256=sha(R/'docs/qa/checkpoints/2026-10-31/thomas-native-platform-source-v1/handoff.json'),
           archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
           members={p.relative_to(R).as_posix():sha(p)for p in files},
           limitations=['Thomas remains a private older-parent component, not yet composed alongside Hogan into the delivered nightly.',
                        'Four-pipe native opening route only; no full1-1, shortcut, all-powerup, original-audio or60Hz completion claim.',
                        'Other native objects/effects and all remaining characters still need the requested full gameplay audit.'])
    save(D/'handoff.json',q)
    (D/'README.md').write_text('''# Thomas: native pipe route and rendering repairs

The original controller-only run cleared four pipes but visual inspection
showed a black sky and the old Ryu inventory label. Thomas's palette callback
had left the universal background from the lives screen unchanged. The adapter
now queues the native area/background-control colour as well as Thomas's
original shades. Its inventory predicate declines the old Ryu equipment path;
the other85 resolved identities keep their previous registers and flags.

The next native run revealed six orange marks. A final real-code CPU OAM
inspection identified six ordinary platform parts, tile5A, whose window read
the new player's art. The fixed atlas reserves window1 for unchanged native
miscellaneous tiles. Original Thomas parts use windows0/2/3; every one of42
poses retains its exact original pixel bytes, attributes and positions.
Native platform physics, initialization, carry and collision are unchanged.

The final Mesen run checks the palette, HUD ownership, actual character and
native platform CHR/OAM/display pixels while clearing all four pipes and
defeating three enemies. Its exact counters and four screenshots are archived.
The palette-parent source run also matches2073 original donor actor frames.
The final graphics component changes only metadata, a granted zero art page
and its authentication digest; actor/kernel instructions remain unchanged.

The delivered Downloads nightly now has75 identities including Hogan. It was
replaced without a backup, as the user requested. Thomas is not yet merged
into that cartridge. Full1-1, shortcut, every powerup, original audio, other
native-object graphics and the remainder of the roster remain unfinished.
''',encoding='utf-8')
    receipt=D.parent.parent.parent/'nightly-2026-10-31-hogan75.json'
    assert receipt==R/'docs/qa/nightly-2026-10-31-hogan75.json'
    save(receipt,nightly)
    save(O/'freeze.json',dict(passed=True,checkpoint=str(D),handoff_sha256=sha(D/'handoff.json'),archive_bytes=archive.stat().st_size,members=len(files)))
    print((O/'freeze.json').read_text())


if __name__=='__main__':main()
