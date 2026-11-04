"""Assemble a Mini-only native transport packet without emitting any ROM."""
import argparse
import json
from pathlib import Path
import subprocess

from prepare_selected_native_packet_v1 import R, sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=True)
    spans = [('RARE_CLASS', 0xa8c7, 15), ('RARE_TABLE', 0xa95e, 15),
             ('RARE_PREPARE', 0xab3d, 15), ('RARE_PREPARE_TAIL', 0xabd7, 13),
             ('DIRECT_BODY', 0xb420, 173), ('DIRECT_RETURN', 0xb5f0, 16),
             ('DIRECT_FINISH', 0xb3dd, 15), ('DIRECT_BOX', 0xa754, 5)]
    cfg = out/'direct.cfg'
    cfg.write_text('MEMORY {\n'+''.join(
        f'{name}: start=${pc:04x}, size={size}, file="{(out/(name+".bin")).as_posix()}";\n'
        for name, pc, size in spans)+'}\nSEGMENTS {\n'+''.join(
        f'{name}: load={name}, type=ro;\n' for name, *_ in spans)+'}\n')
    cc = R/'tools/Windows/cc65/bin'
    src = R/'tools/reference/mini_mario_direct_native_1103.s'
    subprocess.run([cc/'ca65.exe', src, '-o', out/'direct.o'], check=True)
    subprocess.run([cc/'ld65.exe', '-C', cfg, out/'direct.o', '-o', out/'unused.bin',
                    '-Ln', out/'direct.lbl'], check=True)
    result = dict(source_SHA256=sha(src), ROM_written=False,
                  native_ABI='GmNrRare Found retains original X in Y and caller Y/P under two local JSR bytes. Native A remains SafecallA $016A. Direct prep discards only that JSR and uses original GmNrFinish $A60D to restore input X/Y/P before FarCall+3. Worker uses four stack bytes P/X/Y/oldC, no R0..7 or permanent scratch. Returned P/A/X/Y replace that saved frame after restoring oldC. Standard FarCall SMC operands remain volatile across public calls; actual IRQ/FF handlers preserve every live SMC operand at interrupted seams.',
                  service_rows=[0,1,2,17,4,5,6,7,8,9,10,11,12,13,14],
                  portrait='Native rare index3 deliberately keeps the original authenticated chain.',
                  funding=[
                      dict(bank=84,start=0xb420,end=0xb4cd,fill='EA',
                           source='src/cv3_remaining_source_fx.s Cv3FxSpawn: retained191B span minus18B executable prefix; .res191-(*-Cv3FxSpawn). Next Cv3FxQueueIDs atB4CD.'),
                      dict(bank=84,start=0xb3dd,end=0xb3ec,fill='EA',
                           source='src/cv3_source_audio.s Cv3SpawnAudioType JMP3 then explicit .res15,$EA. Next Cv3DmcPrimaryQueue B3EC.'),
                      dict(bank=84,start=0xa754,end=0xa759,fill='EA',
                           source='src/cv3_combat.s Cv3FreezeTick JMP FrozenActors then explicit .res5,$EA. FrozenActors A759.'),
                      dict(bank=84,start=0xb5f0,end=0xb600,fill='FF',
                           source='Frozen Bowser current64 BW_ROM_CHECK beginsB529, used199 bytes/endB5F0 with exactB600 partition bound. Next ROGUE_AUDIO_PAGES_13 beginsB600. freeze-proof.json and current native DBG confirm; B600 audio and BB27 audio data are untouched.')],
                  source_bindings={str(p.relative_to(R)):sha(p)for p in[
                      src,Path(__file__),R/'src/cv3_remaining_source_fx.s',
                      R/'src/cv3_source_audio.s',R/'src/cv3_combat.s',
                      R/'docs/qa/checkpoints/2026-10-31/bowser-current64-functional-source/freeze-proof.json',
                      R/'build/roster-combined-1101-v3/candidate.dbg']},
                  spans=[dict(name=name, pc=pc, bytes=(out/(name+'.bin')).stat().st_size)
                         for name, pc, _ in spans])
    (out/'assembly.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
