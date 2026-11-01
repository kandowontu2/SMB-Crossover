"""Freeze compact source/component Main evidence, without a ROM snapshot."""
from pathlib import Path
import hashlib,json,zipfile

R=Path(__file__).resolve().parents[2];O=R/'build/karnov-combat-main-1101-v6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not(O/'source-stage.json').exists()
    main=json.loads((O/'Main-controls.json').read_text());unit=json.loads((O/'combat-CPU-controls.json').read_text())
    assert main['passed']and unit['passed']and main['explicit_component_RAM_overlay']
    assert main['Main']['minimum_Main_ISR_SP']>=135
    files=[Path(__file__),R/'tools/audit/check_karnov_combat_main_1101_v6.py',
           R/'tools/audit/prepare_karnov_combat_stack_1101_v3.py',R/'tools/audit/build_karnov_combat_component_1101_v2.py',
           R/'tools/audit/check_karnov_combat_component_1101_v2.py',R/'tools/reference/karnov_combat_1101_v2.inc']
    files += [O/n for n in ['Main-controls.json','unparked-negative.json','combat-CPU-controls.json','assembly-stage.json',
                           'combat-stack-v3.inc','component.s','component.cfg','bindings.s','component.lbl','kernel.bin','resident.bin']]
    path=O/'source-proof.zip'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    q=dict(passed=True,complete_component_only=True,installed=False,native=False,ROM_carrier=False,
           parent_ROM_sha256=main['ROM_sha256'],parent_image_location='Downloads/SMB-Crossover-Latest-WIP-MMC5.nes before a later nightly replacement',
           source_proof=dict(sha256=sha(path),bytes=path.stat().st_size,members=len(files)),
           actual_Main_ISR_cuts=sum(len(x['interrupts'])for x in main['Main']['cases']),
           minimum_Main_ISR_SP=main['Main']['minimum_Main_ISR_SP'],
           isolated_calls=unit['counters']['calls'],isolated_ISR_cuts=unit['real_ISR_cuts'],
           negative='Earlier unparked actual Main receipt retained as diagnostic; no ROM or historical Python snapshot is included.',
           limits=['Executable overlay is explicit. Actual loader/carrier/native emulator integration remains separate.',
                   'The17-byte parked frame is private C2 C868..C879. Every copied byte and both SP boundaries are interrupt-tested.',
                   'Source projectile motion/lifetime and unchanged native enemy/block effects remain their original owners.'])
    (O/'source-stage.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
