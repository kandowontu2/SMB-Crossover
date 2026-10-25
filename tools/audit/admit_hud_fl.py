"""Admit the reviewed immediate numeric producer and freeze both ROMs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
C=V/'hud-fast-fc/source'
O=V/'hud-admission-fl'
CP=R/'build/checkpoints/hud-numbers-fl'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists() and not CP.exists()
    O.mkdir()
    receipts={n:json.loads((V/n/'summary.json').read_text()) for n in
              ('hud-fast-ff','hud-fast-ports-fn','hud-fast-regressions-fj','hud-fast-publish-fh')}
    assert receipts['hud-fast-ff']['status']=='PASS_COMPILED_RAW_REQUESTS_AND_FOREIGN_ORDER_PRIVATE_CANDIDATE'
    assert receipts['hud-fast-ports-fn']['status']=='PASS_NATIVE_EXACT_AND_IMMEDIATE_HUD_PARENT_CONSUMERS'
    assert receipts['hud-fast-regressions-fj']['passed']
    assert receipts['hud-fast-publish-fh']['all_sampled_composed_calls_no_slower']
    parent=R/'build/checkpoints/water-visible-cw/manifest.json'
    previous=json.loads(parent.read_text())
    prep=json.loads((V/'hud-fast-fc/build.json').read_text())
    assert all(sha(R/f'build/smb-crossover-{m}.nes')==value for m,value in previous['ROMs'].items())
    changed,new=[],[]
    for name,value in prep['source_hashes'].items():
        assert sha(C/name)==value
        if not (R/name).exists():
            new.append(name)
        elif sha(R/name)!=value:
            changed.append(name)
    assert set(changed)=={'smb1base.cfg','src/entrypoint.s','src/screen_render.s'} and new==['src/hud_tail.s'], (changed,new)
    before={name:sha(R/name)for name in changed}
    expected={m:sha(C/f'build/smb-crossover-{m}.nes')for m in ('mmc3','mmc5')}
    layouts=[]
    for mapper in expected:
        a=(R/f'build/smb-crossover-{mapper}.nes').read_bytes()
        b=(C/f'build/smb-crossover-{mapper}.nes').read_bytes()
        assert len(a)==len(b) and a[:16]==b[:16] and a[16+512*1024:]==b[16+512*1024:]
        banks=sorted({(i-16)//8192 for i,(x,y)in enumerate(zip(a,b))if x!=y})
        assert banks==[3], banks
        assert sha(C/f'build/smb-crossover-{mapper}-baseline.nes')==sha(R/f'build/smb-crossover-{mapper}-baseline.nes')
        layouts.append(dict(mapper=mapper,changed_PRG_banks=banks,header_CHR_baseline_unchanged=True))
    preparation=dict(status='ADMITTING_REVIEWED_HUD',utc=datetime.now(timezone.utc).isoformat(),
        parent_checkpoint_sha256=sha(parent),before_source_hashes=before,expected_ROMs=expected,
        verification={n:sha(V/n/'summary.json')for n in receipts},new_RAM_bytes=0,layouts=layouts,goal_complete=False)
    (O/'preparation.json').write_text(json.dumps(preparation,indent=2)+'\n')
    for name in changed+new:
        shutil.copyfile(C/name,R/name)
    for mapper in expected:
        with (O/f'build-{mapper}.log').open('wb')as log:
            result=subprocess.run([sys.executable,str(R/'tools/build.py'),'--mapper',mapper],cwd=R,stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0
        assert sha(R/f'build/smb-crossover-{mapper}.nes')==expected[mapper]
        print('admitted',mapper,expected[mapper],flush=True)
    CP.mkdir()
    names=changed+new+[f'build/smb-crossover-{m}.{ext}'for m in expected for ext in('nes','lbl','dbg','map')]
    for name in names:
        dst=CP/name
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(R/name,dst)
    manifest=dict(status='IMMEDIATE_HUD_NUMERIC_OPTIMIZATION_ADMITTED_FULL_GOAL_ACTIVE',
        parent_checkpoint=parent.relative_to(R).as_posix(),parent_checkpoint_sha256=sha(parent),ROMs=expected,
        hashes={n:sha(CP/n)for n in names},new_RAM_bytes=0,layouts=layouts,
        verification={n:sha(V/n/'summary.json')for n in receipts},goal_complete=False)
    (CP/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    doc=R/'docs/qa/hud-immediate-numbers-2026-10-22.md'
    doc.write_text('''# Immediate numeric HUD optimization

The playable builds now use a local copy of the native numeric producer in the existing renderer bank. UpdateNumber retains its original19-byte public span. The original direct PrintStatusBarNumbers entry remains unchanged. No SRAM bytes, CHR data or header changes are needed; only PRG bank3 changes, and both baseline ROMs remain literal.

Repeated score/coin requests replace a complete final pair only after checking its headers, terminator and actual packet boundary. Numeric data is written immediately at the original position. Foreign horizontal, vertical, mirrored, RLE and partial writes keep their last-writer order. The previously rejected deferred queue is not installed.

Compiled checks cover1024 raw request/flags/selector cases per mapper,40 foreign-order cases and six repeated-request patterns per mapper. Fresh ordinary-controller captures provide373 numeric calls per version on MMC3 and41 per version on MMC5. All828 captured calls reproduce every register,10240RAM bytes, hardware read and ordered write. No ISR occurred inside these particular calls. Separate actual leaf NMI/IRQ recordings exercise all256 incoming X values per handler/version/mapper, totaling2048 cases. The only ignored data value is the unchanged MMC3 IRQ acknowledge write, whose data byte has no hardware effect; its actual STA producer and both raw traces are retained. [MMC3 register reference](https://www.nesdev.org/wiki/MMC3#IRQ_disable_($E000-$FFFE,_even)).

Matched old/new calls then execute their real parent GameLoop suffix. Changed scratch/private/stack cells are checked for use before replacement; shorter-queue Y and end-frame X differences have explicit consumer checks. Final PPU images and parent hardware port effects match. Both5200-frame native endpoint images match in RGB. These are bounded component/continuation checks, not all-character clear claims.

The first immediate candidate had a valid long-prefix case whose producer plus full queue publication cost79 extra CPU cycles. The faster validator removes redundant bounds comparisons: target<=70 and every packet advances at least4 bytes, so overshoot is safely rejected on the next iteration. All seven sampled coalesced MMC3 cases now reduce that composed cost, by58 to340 cycles. Normal empty-queue player updates save186 CPU cycles on MMC3 and116 on MMC5. Five repeated requests use14 queue bytes instead of70. This is not a claim that all gameplay lag is gone.

The final parser passes eight fresh native regressions covering Cheats, score positions, terrain publication and the full Bill flagpole/castle transition on both mappers. The first immediate candidate also passed18 related regressions before the parser-only optimization. Raw request/order and exact native-caller checks were repeated on the final parser. Main rebuilds match the reviewed private ROMs byte for byte.

Evidence: build/verification/hud-fast-ff, hud-fast-ports-fn, hud-fast-native-fg, hud-fast-publish-fh and hud-fast-regressions-fj. Checkpoint: build/checkpoints/hud-numbers-fl/manifest.json. All failed attempts and lossless captures remain retained. The all-character through2-2 routes, every ability/upgrade, remaining palette/fidelity fixes and final native recordings remain unfinished.
''')
    preparation.update(status=manifest['status'],checkpoint_sha256=sha(CP/'manifest.json'),report_sha256=sha(doc))
    (O/'summary.json').write_text(json.dumps(preparation,indent=2)+'\n')


if __name__=='__main__':
    main()
