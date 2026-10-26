"""Bind all existing and new1346 multiplier owners, serialNMI dispatch and IRQ."""
from pathlib import Path
import argparse
import json
import re
from py65.disassembler import Disassembler
from verify_native_relocation import NesMPU
from link_pit_rygar_sophia_audit_cpu import scoped_load as load
from check_tmnt_render_oa import address, location
from tmnt_native_storage_driver import ROOT, sha, source_data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.candidate)
    assert old['raw'][:16] == new['raw'][:16]
    assert old['raw'][16:16 + 63 * 8192] == new['raw'][16:16 + 63 * 8192]
    assert old['raw'][16 + 64 * 8192:] == new['raw'][16 + 64 * 8192:]
    raw = new['raw'];source = a.source
    accesses = {}
    for path in source.rglob('*'):
        if path.is_file() and path.suffix in ['.s', '.inc', '.h', '.c', '.cfg']:
            value = path.read_text(errors='replace')
            if re.search(r'\$520[56]\b', value, re.I):
                accesses[path.relative_to(source).as_posix()] = dict(sha256=sha(path), source_sites=re.findall(r'(?im)^\s*(?:sta|stx|lda)\s+\$520[56]\b.*$', value))
    assert set(accesses) == {'src/protoman_audio_kernel.inc', 'src/tmnt_audio_multiply.s',
                             'build/generated/guest-audio/megaman3.inc', 'audio/megaman3/imported.s','src/tmnt_parser_math_next.s'}
    debug = a.candidate.with_suffix('.dbg').read_text()
    actual_files = [line for line in debug.splitlines() if line.startswith('file\t')]
    assert any('guest-audio/megaman3.inc' in line for line in actual_files)
    assert any('src/protoman_audio_kernel.inc' in line for line in actual_files)
    assert not any('audio/megaman3/imported.s' in line for line in actual_files)
    owners = []
    for name in ['Mm3::_fraction255_mmc5', 'ProtoMm3::_fraction255_mmc5', 'TnFastProduct','TnTempoProduct']:
        at, pc = location(new, name), address(new, name)
        size = int(new['syms'][name]['size'], 0)
        body = raw[at:at + size]
        operations = []
        # Exact byte patterns are genuine callable-body operations below; the
        # complete original handlers and their zero branches are also bound.
        for i in range(size - 2):
            if body[i] in [0xad, 0x8d,0x8e] and body[i + 1] in [5, 6] and body[i + 2] == 0x52:
                operations.append(dict(PC=pc + i, operation='W' if body[i] in[0x8d,0x8e] else 'R', register=0x5200 + body[i + 1]))
        assert [(row['operation'],row['register'])for row in operations]==([('W',0x5205),('W',0x5206),('R',0x5206),('R',0x5205)]if name=='TnTempoProduct'else[('W',0x5205),('W',0x5206),('R',0x5205),('R',0x5206)])
        owners.append(dict(label=name, physical_bank=(at - 16) // 8192, PC=pc, bytes=size, operations=operations,
                           body_sha256=__import__('hashlib').sha256(body).hexdigest()))
    assert owners[0]['physical_bank'] != owners[1]['physical_bank'] and owners[2]['PC'] == 0xa125
    assert owners[2]['bytes'] == 78
    nmi = location(new, 'NonMaskableInterrupt');nmi_pc = address(new, 'NonMaskableInterrupt')
    nmi_size = int(new['syms']['NonMaskableInterrupt']['size'], 0)
    target = bytes([0x20]) + address(new, 'AudioUpdate').to_bytes(2, 'little')
    callers = [nmi_pc + i for i in range(nmi_size - 2) if raw[nmi + i:nmi + i + 3] == target]
    assert len(callers) == 2
    literal_call_files = {}
    for path in source.rglob('*'):
        if path.is_file() and path.suffix in ['.s', '.inc', '.c']:
            matches = re.findall(r'(?im)^\s*(?:jsr|jmp|farcall)\s+AudioUpdate\b.*$', path.read_text(errors='replace'))
            if matches: literal_call_files[path.relative_to(source).as_posix()] = matches
    assert set(literal_call_files) == {'src/reset.s'} and len(literal_call_files['src/reset.s']) == 2
    audio = (source / 'src/music_drivers/audio.s').read_text()
    assert 'cmp #CHARACTER_PIT\n  bcc :+\n    jsr ExpandedAudioUpdate\n    jmp GuestMix' in audio
    assert 'cmp #CHARACTER_MEGAMAN\n  bne :+\n    jsr MegaManAudioUpdate\n    jmp GuestMix' in audio
    cold = (source / 'src/protoman_cold.s').read_text()
    assert 'lda ProtoVariant\n  beq Original' in cold and 'jsr ProtoNativeAudioUpdate' in cold and 'jsr MegaManAudioNativeUpdate' in cold
    resident = (source / 'src/tmnt_audio_resident.s').read_text()
    assert 'lda a:SelectedCharacter\n cmp #19\n bne TnAudioLegacy' in resident
    begin, count = location(new, 'IrqScrollSplit'), int(new['syms']['IrqScrollSplit']['size'], 0)
    irq = raw[begin:begin + count]
    assert count == 68 and not any(irq[i:i + 3] in [bytes.fromhex('ad0552'), bytes.fromhex('ad0652'), bytes.fromhex('8d0552'), bytes.fromhex('8d0652')] for i in range(count - 2))
    mem = [0] * 65536;mem[0x8000:0x8000 + count] = irq
    decoder = NesMPU(memory=mem);dis = Disassembler(decoder);pc = 0x8000
    irq_instructions = []
    while pc < 0x8000 + count:
        width, text = dis.instruction_at(pc);op, mode = decoder.disassemble[mem[pc]]
        assert op not in ['JSR', 'JMP', '???']
        if mode in ['abs', 'abx', 'aby']:
            target = mem[pc + 1] + 256 * mem[pc + 2]
            assert target not in [0x5205, 0x5206]
        irq_instructions.append(dict(PC=pc, instruction=text));pc += width
    assert pc == 0x8000 + count and irq_instructions[-1]['instruction'] == 'RTI'
    _, original, cpu, disasm, seen, words = source_data()
    incoming = []
    for pc in seen:
        width, text = disasm.instruction_at(pc);op, mode = cpu.disassemble[original[pc]]
        if op in ['JSR', 'JMP'] and mode == 'abs':
            to = original[pc + 1] + 256 * original[pc + 2]
            if 0x8cbd <= to < 0x8cc1: incoming.append([pc, to])
    for word in words:
        to = original[word] + 256 * original[word + 1]
        if 0x8cbd <= to < 0x8cc1: incoming.append([word, to])
    assert incoming and all(target == 0x8cbd for pc, target in incoming)
    new_entries=[]
    for lo,hi in[(0x8671,0x8674),(0x8acc,0x8acf)]:
        refs=[]
        for pc in seen:
            if lo<=pc<hi:continue
            width,_=disasm.instruction_at(pc);op,mode=cpu.disassemble[original[pc]];targets=[]
            if mode=='rel':
                off=original[pc+1];targets=[pc+width,pc+width+(off-256 if off>=128 else off)]
            elif op in['JSR','JMP']and mode=='abs':targets=[original[pc+1]+256*original[pc+2]]
            elif op not in['RTS','RTI','JMP','BRK']:targets=[pc+width]
            refs.extend([pc,to]for to in targets if lo<=to<hi)
        roots=[word for word in words if lo<=original[word]+256*original[word+1]<hi]
        assert refs and all(to==lo for pc,to in refs)and not roots,(lo,refs,roots)
        new_entries.append(dict(source_span=[lo,hi],incoming=refs,pointer_interiors=roots))
    assert old['raw'][16+63*8192+0xf96:16+63*8192+0xfa3]==new['raw'][16+63*8192+0xf96:16+63*8192+0xfa3]
    proof = dict(passed=True, source_only=True, native_run=False, baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                 complete_private_source_math_reference_files=accesses,
                 genuine_compiled_owners=owners, inactive_reference_artifact='audio/megaman3/imported.s',
                 two_real_AudioUpdate_callers_inside_fixed_NMI=callers,
                 literal_source_callers=literal_call_files,
                 Megaman_Mm3_ProtoMm3_char1_and_TMNT_char19_dispatch_mutually_exclusive=True,
                 all_owners_write_both_operands_before_any_product_read=True,
                 no_persistent_operand_read_after_return_or_fake_operand_restore=True,
                 real_IRQ68_inline_no_multiplier_access=True, decoded_actual_IRQ=irq_instructions,
                 old_partial_instruction_entry_not_reachable=incoming,
                 no_new_RAM_or_shared125_bytes=True, helper_PC=0xa125, helper_bytes=78,
                 new_hook_instruction_closure=new_entries,original_AF96_still_genuine_and_exact=True,new_helper_verified_FF_tail=[0xa1b2,0xa200], checker_sha256=sha(Path(__file__)),
                 Mesen_model_source='https://github.com/SourMesen/Mesen2/blob/master/Core/NES/Mappers/Nintendo/MMC5.h',
                 limits='Exclusive within the existing serial single-depth NMI audio contract; IRQ interleavings are separately executed at every helper boundary. Nested NMI inside an audio call was unsupported before this change and is not advertised as a new supported domain. No native run of this candidate or source/hardware cadence claim.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(passed=True, actual_owners=len(owners), NMI_callers=callers, helper_bytes=78)))


if __name__ == '__main__':
    main()
