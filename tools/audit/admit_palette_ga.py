"""Admit verified Rygar world-palette ownership; preserve every other character."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';C=V/'world-palette-fv/source';O=V/'world-palette-admission-ga';CP=R/'build/checkpoints/rygar-world-palette-ga'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not O.exists()and not CP.exists();O.mkdir()
    receipts={n:json.loads((V/n/'summary.json').read_text())for n in('world-palette-abi-gb','world-palette-native-fx','world-palette-pixels-gc')}
    assert receipts['world-palette-abi-gb']['status']=='PASS_RYGAR_WORLD_PALETTE_AND_OTHER_CHARACTER_CALLER_IDENTITY'
    assert receipts['world-palette-native-fx']['passed']
    assert receipts['world-palette-pixels-gc']['status']=='PASS_PIXEL_CHANGES_BOUNDED_TO_PALETTE3_WORLD_SPRITE_RECTANGLES'
    assert not receipts['world-palette-pixels-gc']['changes_outside_world_sprite_rectangle_union']
    video=R/'build/roster-through-2-2/root-rygar-palette-av-fy-7-v0-mmc3';vm=json.loads((video/'manifest.json').read_text())
    assert vm['verified_through_2_2']and vm['recording_verified']and vm['result']['deaths']==0
    parent=R/'build/checkpoints/hud-numbers-fl/manifest.json';old=json.loads(parent.read_text());build=json.loads((V/'world-palette-fv/build.json').read_text())
    assert all(sha(R/f'build/smb-crossover-{m}.nes')==v for m,v in old['ROMs'].items())
    changed=[];new=[]
    for n,v in build['source_hashes'].items():
        assert sha(C/n)==v
        if not(R/n).exists():new.append(n)
        elif sha(R/n)!=v:changed.append(n)
    assert set(changed)=={'src/characters.s','src/entrypoint.s','smb1base.cfg'}and new==['src/world_sprite_palette.s'],(changed,new)
    expected={m:sha(C/f'build/smb-crossover-{m}.nes')for m in('mmc3','mmc5')};layouts=[]
    for mapper in expected:
        a=(R/f'build/smb-crossover-{mapper}.nes').read_bytes();b=(C/f'build/smb-crossover-{mapper}.nes').read_bytes()
        assert len(a)==len(b)and a[:16]==b[:16]and a[16+512*1024:]==b[16+512*1024:]
        banks=sorted({(i-16)//8192 for i,(x,y)in enumerate(zip(a,b))if x!=y});assert banks==[3]
        labels=[]
        for folder in(R,C):labels.append({n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\w+)$',(folder/f'build/smb-crossover-{mapper}.lbl').read_text(),re.M)})
        assert all(labels[1].get(n)==v for n,v in labels[0].items()),'All existing public labels stay fixed'
        assert sha(C/f'build/smb-crossover-{mapper}-baseline.nes')==sha(R/f'build/smb-crossover-{mapper}-baseline.nes')
        layouts.append(dict(mapper=mapper,changed_PRG_banks=banks,existing_public_labels_unchanged=True,header_CHR_baseline_unchanged=True))
    report=dict(status='ADMITTING_RYGAR_WORLD_PALETTE',utc=datetime.now(timezone.utc).isoformat(),parent_checkpoint_sha256=sha(parent),expected_ROMs=expected,
        previous_source_hashes={n:sha(R/n)for n in changed},verification={n:sha(V/n/'summary.json')for n in receipts},native_recording_manifest_sha256=sha(video/'manifest.json'),layouts=layouts,new_RAM_bytes=0,new_OAM_parts=0,new_CHR_bytes=0,goal_complete=False)
    (O/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    for n in changed+new:shutil.copyfile(C/n,R/n)
    for mapper,value in expected.items():
        with(O/f'build-{mapper}.log').open('wb')as log:p=subprocess.run([sys.executable,str(R/'tools/build.py'),'--mapper',mapper],cwd=R,stdout=log,stderr=subprocess.STDOUT)
        assert p.returncode==0 and sha(R/f'build/smb-crossover-{mapper}.nes')==value
        print('admitted',mapper,value,flush=True)
    CP.mkdir();names=changed+new+[f'build/smb-crossover-{m}.{e}'for m in expected for e in('nes','lbl','dbg','map')]
    for n in names:dst=CP/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,dst)
    manifest=dict(status='RYGAR_WORLD_PALETTE_ADMITTED_FULL_ROSTER_GOAL_ACTIVE',parent_checkpoint=parent.relative_to(R).as_posix(),parent_checkpoint_sha256=sha(parent),
        ROMs=expected,hashes={n:sha(CP/n)for n in names},verification=report['verification'],new_RAM_bytes=0,new_OAM_parts=0,new_CHR_bytes=0,layouts=layouts,goal_complete=False)
    (CP/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    doc=R/'docs/qa/rygar-world-palette-2026-10-22.md'
    doc.write_text('''# Rygar world palette repair

Rygar now retains the native area's sprite palette3. His underground bouncing bricks, debris and world actors use cyan again, while his own colors stay on palette0. His88 authored body/disk/chain parts use palette0, the drawing paths clear their palette modifiers, and neither behavior mode gives him a2.02 inventory icon. Other guests retain their existing face/special palette until their artwork and effects have their own verified allocation. Bass and the other face-palette consumers remain unfinished.

The existing palette selector's20-byte span calls a32-byte same-bank cold helper at BF91..BFB0. Every old public label stays fixed. No RAM, OAM parts, CHR data, header or baseline ROM bytes change. The common palette-queue path costs26 extra CPU cycles, native Mario23 and Rygar57; this only affects palette requests. The full recorded replay retains literal CPU/position/lag counters, OAM/CHR, render, inputs and audio-event logs from the previous FL run, so no extra lag or sprite load appears in this bounded replay.

Compiled comparisons cover15848 cases per mapper, including all64 physical input flag patterns for the internal palette queue, every identity, all four area types, and full GetPlayerColors calls through three power forms. Other characters' packets and the full public caller's registers, flags, scratch, stack frame and mapper outputs match. Rygar's internal queue Y changes because it now indexes the native palette table; the actual sole caller replaces it before use, checked instruction by instruction. The first FW oracle incorrectly required internal Y identity. FZ then assumed that the public GetPlayerColors farcall retained a foreign MMC3 selector; its original standard farcall actually selects7. Both failed receipts remain, and corrected GB compares the actual caller contract against the original ROM.

Twelve unchanged native checks pass on the final candidate: Rygar pickups/animation, original disk return and chain, walk phases, water/combat/block/audio/death lifecycle, Bass palette stability and outline rendering on both mappers. Both native pickup transitions still complete normally. Native controller-only replay and recording clear all six stages through2-2 with zero deaths and real control in2-3. This does not certify every character or every weapon upgrade.

All20680 old/new native video frames were compared. Color changes occur in5899 frames, with zero changed pixels outside the conservative union of prior/current committed palette3 sprite rectangles. Rygar's palette0 artwork and primary palette packet remain unchanged. The same underground debris sequence was inspected before and after: brown/orange fragments are now cyan, with the player and background intact. Native PCM has560 differing sample frames out of16516730, RMS difference-112.14dBFS; no waveform identity claim is made. Both lossless masters independently verify every RGB frame and PCM sample against their retained native captures.

The final assembler build had a ca65 local-label resolution error in FU; corrected FV builds both mappers and both literal baselines. All failures and original lossless media are retained. Main builds reproduce the reviewed FV ROM bytes exactly. Evidence: build/verification/world-palette-abi-gb, world-palette-native-fx, world-palette-pixels-gc and root-rygar-palette-av-fy-7-v0-mmc3. Checkpoint: build/checkpoints/rygar-world-palette-ga/manifest.json.

The overall source-fidelity, remaining character/weapon, performance and final-recording goal remains active. Rygar's corrected run is still a QA recording while those broader checks remain open.
''')
    report.update(status=manifest['status'],checkpoint_sha256=sha(CP/'manifest.json'),report_sha256=sha(doc));(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
