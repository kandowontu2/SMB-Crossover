"""Detached214-byte carry/camera funding and reader census; no CPU/ROM overlay."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

import replay_dkjr_fourth_first_loss_bc5_1115 as Current
import compose_dkjr_helper_retire_1113 as Source

R = Path(__file__).resolve().parents[2]
PIN = Current.PIN
START, END = 0xb6a5, 0xb77b
REASON = 0xc8f6
SOURCE_PATH = R/'build/dkjr-native-source-1102-v2/native-entrance-v89.s'
LABEL_PATH = SOURCE_PATH.with_suffix('.lbl')
SOURCE_SHA = '82cca72d6091ca2569093e7fd35aba55f43e0d191de06224d8b2335e316c839d'
LABEL_SHA = '0d3926e7791164c76f3727a35b748ebddf5357d58b28891473fbd05dcb1998be'
H = lambda value: sha256(value).hexdigest()


def source_inputs():
    # Both exact inputs are retained in place. No archive/dependency restore.
    data, label_data = SOURCE_PATH.read_bytes(), LABEL_PATH.read_bytes()
    assert H(data) == SOURCE_SHA and H(label_data) == LABEL_SHA
    text = data.decode().replace('\r\n', '\n')
    labels = {name: int(value, 16) for value, name in
              re.findall(r'^al ([0-9a-fA-F]+) \.(\w+)$', label_data.decode().replace('\r\n', '\n'), re.M)}
    for name in set(re.findall(r'\bDData_c[0-9a-f]{3}\b', text)):
        labels[name] = labels['DkjrSourceData']+int(name[6:], 16)-0xc2cd
    aliases = re.findall(r'^(\w+)\s*=\s*(\w+)\s*$', text, re.M)
    for _ in range(len(aliases)):
        for alias, target in aliases:
            if alias in labels and target not in labels:labels[target] = labels[alias]
    return text, labels


def image(raw):
    assert isinstance(raw, bytes) and H(raw) == PIN
    Current.bindings(raw)
    old = Current.F.Prior.Early.Old
    return b''.join(raw[old.CHR+p*1024:old.CHR+(p+1)*1024] for p in old.PAGES)


def numeric(text):
    return ''.join(f'{name}={value}\n' for name, value in re.findall(
        r'^(\w+)\s*=\s*(\$[0-9a-fA-F]+|[0-9]+)\s*$', text, re.M))


def assemble_fragment(source, whole, labels):
    local = set(re.findall(r'^(\w+):', source, re.M))
    pre = numeric(whole)+''.join(f'{name}=${value:x}\n' for name, value in labels.items()
                                 if name not in local)
    return Source.T.assemble(pre+'.segment "CARRY"\n'+Source.expand_branches(source),
                             dict(CARRY=(START, END-START)))


def measured(raw):
    body = image(raw)
    whole, labels = source_inputs()
    # Delivered1110 pending-transition correction is later than retainedv89.
    # It must run before the original pre-snap fall-distance comparison.
    assert body[0xb7bb-0xa000:0xb7c1-0xa000] == bytes.fromhex('2010a24ce1a8')
    labels['DkCarryPendingTransition'] = 0xb7bb
    begin = whole.index('DkjrNativeCarryEvent:')
    finish = whole.index('DkjrNativeLifeReset:', begin)
    old_source = whole[begin:finish]
    old_source = Source.once(old_source, ' jsr DkjrFallDistance\n',
                             ' jsr DkCarryPendingTransition\n')
    old = assemble_fragment(old_source, whole, labels)
    assert old['used']['CARRY'] == END-START
    assert old['images']['CARRY'] == body[START-0xa000:END-0xa000], [
        (hex(START+i), a, b) for i, (a,b) in enumerate(zip(
            old['images']['CARRY'], body[START-0xa000:END-0xa000])) if a != b]
    new_source = old_source
    # Reuse the existing unconditional reject JMP in the preceding long
    # guard. Its instruction bytes and the public reject anchor are retained.
    new_source = Source.once(new_source, '''DkShortCandidate179:
 jne CarryReject
''', '''DkShortCandidate179:
 beq Carry179Admitted
CarryRejectTrampoline:
 jmp CarryReject
Carry179Admitted:
''')
    new_source = Source.once(new_source, '''DkShortCandidate180:
 jne CarryReject
''', '''DkShortCandidate180:
 bne CarryRejectTrampoline
''')
    new_source = Source.once(new_source, ' sta CarryReason\n', '')
    new_source = Source.once(new_source, '''CarrySafeLanding:
 jsr DkjrNativeImportAnchor
''', '''CarrySafeLanding:
 jsr CarryGround
''')
    new_source = Source.once(new_source, '''CarryGround:
 jmp DkjrNativeImportAnchor
CarryReject:
''', '''CarryGround:
 jsr DkjrNativeShiftCamera
 bcc CarryReject
 jmp DkjrNativeImportAnchor
 .byte $ea ; Unreachable one-byte balance inside this exact214-byte proposal.
CarryReject:
''')
    new = assemble_fragment(new_source, whole, labels)
    assert new['used']['CARRY'] == END-START
    assert old['symbols']['CarryReject'] == new['symbols']['CarryReject'] == 0xb779
    assert old['symbols']['DkjrNativeCarryEvent'] == new['symbols']['DkjrNativeCarryEvent'] == START
    assert old['images']['CARRY'][-2:] == new['images']['CARRY'][-2:] == bytes.fromhex('1860')
    return whole, labels, body, old_source, new_source, old, new


def literal_calls(body, low, high):
    rows = []
    for origin, data in ((0xa000, body[:0x1fe0]), (0xd000, body[9*1024:])):
        for i in range(len(data)-2):
            target = int.from_bytes(data[i+1:i+3], 'little')
            if data[i] in (0x20, 0x4c, 0x6c) and low <= target < high:
                rows.append(dict(pc=origin+i, opcode=data[i], target=target))
    return rows


def descriptor(raw):
    whole, labels, body, old_source, new_source, old, new = measured(raw)
    old_code, new_code = old['images']['CARRY'], new['images']['CARRY']
    oldp = Current.F.Prior.Early.Old
    payload_offset = START-0xa000
    page, within = divmod(payload_offset, 1024)
    file = oldp.CHR+oldp.PAGES[page]*1024+within
    assert within+len(old_code) <= 1024
    all_calls = literal_calls(body, START, END)
    outside = [row for row in all_calls if not START <= row['pc'] < END]
    assert outside == [dict(pc=0xa06f, opcode=0x4c, target=START)], outside
    reason_words = [i for i in range(len(body)-1) if body[i:i+2] == REASON.to_bytes(2, 'little')]
    assert len(reason_words) == 1
    assert body[reason_words[0]-1] == 0x8d
    assert START-0xa000 <= reason_words[0]-1 < END-0xa000
    named_reason = [line.strip() for line in whole.splitlines()
                    if re.search(r'\bCarryReason\b', line) and not line.lstrip().startswith(';')]
    assert named_reason == ['CarryReason=$c8f6', 'sta CarryReason'], named_reason
    assert not re.search(r'\$c8f6\b', whole, re.I) or named_reason[0] in whole

    # Complete source instruction metadata is used only for static operand
    # classification. These bytes are never copied to a CPU or a ROM.
    pre = ''.join(f'{name}=${value:x}\n' for name, value in labels.items())
    complete = Source.T.assemble(pre+Source.expand_branches(whole), dict(
        DKJR=(0xa000,8160), DK_MAIN=(0xd65e,73), DK_PAUSE=(0xd540,286), DK_PORTS=(0xd6a7,345)))
    instructions = complete['instructions']
    direct_reason = [row for row in instructions if row['operand'] == REASON]
    assert len(direct_reason) == 1 and direct_reason[0]['op'] == 'STA'
    indexed_alias = [row for row in instructions if row['mode'] in ('abx', 'aby')
                     and isinstance(row['operand'], int) and row['operand'] <= REASON <= row['operand']+255
                     and row['operand'] >= 0xc700]
    indirect = [row for row in instructions if row['mode'] in ('inx', 'iny', 'ind')]
    assert indirect == []  # Original indirect operations are explicit SMC below.
    indexed_domains = []
    for row in indexed_alias:
        base = row['operand']
        if base in (0xc8c0,0xc8c1,0xc8c8,0xc8c9,0xc8d0,0xc8d1):
            maximum, why = 6, 'Profile1..4 table selector/publisher X0,2,4,6; currentPhase profile1'
        elif base in range(0xc800, 0xc804):
            maximum, why = 188, 'Three64-byte lists; validate stops at finalC8BC sentinel; append max60'
        elif base == 0xc8e4:
            maximum, why = 3, 'CopyRect startsX0; increments untilCPX4'
        elif base == 0xc8e8:
            maximum, why = 2, 'FullBox TXA/AND1/ASL producesY0or2'
        else:
            raise AssertionError(('Unclosed indexed reason alias', row))
        assert base+maximum < REASON
        size = 3
        at = row['pc']-0xa000 if row['pc']<0xc000 else 9*1024+row['pc']-0xd000
        origin = dict(DKJR=0xa000,DK_MAIN=0xd65e,DK_PAUSE=0xd540,DK_PORTS=0xd6a7)[row['segment']]
        expected = complete['images'][row['segment']][row['pc']-origin:row['pc']-origin+size]
        assert body[at:at+size] == expected, ('Current indexed alias preimage', row)
        indexed_domains.append(dict(**row, maximum_index=maximum,
            maximum_address=base+maximum, legal_domain=why, current_preimage=expected.hex()))
    smc = []
    originals = re.findall(r'^D_([0-9a-f]+):[^\n]*original \$[0-9A-F]+: (lda|sta) \(\$(\w+)\),y', whole, re.M)
    assert len(originals) == 23
    for suffix, op, pointer in originals:
        name = 'DIndirect_'+suffix
        pc = complete['symbols'][name]
        at = pc-0xa000
        expected = bytes.fromhex('b9ffff' if op == 'lda' else '99ffff')
        assert body[at:at+3] == expected, ('Current virtual-indirect template', name)
        if pointer == '91':
            maximum, why = 0xc4ff, 'World fruit pointer0400; even full8-bit Y staysbelowC500; realcount<=4'
        elif pointer == '04':
            maximum, why = 0xc3fe, 'OAM pointerhigh02; even lowFF+full8-bit Y staysbelowC400; highrestoredaftercall'
        elif pointer == '02':
            maximum, why = 0xc8bc, 'Native lists C800/840/880 <=60; originalstatic record ROM/OAM tables do not targetC8F6'
        else:
            raise AssertionError(('Unclosed virtual-indirect family', pointer))
        assert maximum < REASON
        smc.append(dict(name=name, PC=pc, operation=op, original_pointer=pointer,
                        maximum_private_address=maximum, legal_domain=why,
                        current_initial_preimage=expected.hex()))

    moved = {name: dict(old=pc, new=new['symbols'][name]) for name, pc in old['symbols'].items()
             if name in new['symbols'] and START <= pc < END and new['symbols'][name] != pc}
    moved_targets = {row['old'] for row in moved.values()}
    words = []
    for origin, data in ((0xa000, body[:0x1fe0]), (0xd000, body[9*1024:])):
        for i in range(len(data)-1):
            pc = origin+i
            target = int.from_bytes(data[i:i+2], 'little')
            if target in moved_targets and not START <= pc < END:
                owners = [row for row in instructions if row['pc'] <= pc < row['pc']+3]
                words.append(dict(word_pc=pc, target=target,
                    source_instruction_candidates=owners, near_hex=data[max(0,i-3):i+5].hex()))
    assert len(words) == 1 and words[0]['word_pc'] == 0xb488 and words[0]['target'] == 0xb74c
    assert body[0xb488-0xa000:0xb48b-0xa000] == bytes.fromhex('4cb7b3')
    words[0]['classification'] = 'JMP opcode4C plus low operandB7; real targetB3B7, not pointerB74C'

    # The actual native post-position wrapper is a saved-AXYP, saved scratch/
    # SMC publisher of row37. Native public code never calls an interior carry
    # label directly. Publish all raw PRG candidates without calling unrelated
    # bank-local B6xx words executable DK ingress.
    prg = raw[16:16+128*8192]
    raw_absolute = []
    bank3_publishers = []
    for i in range(len(prg)-15):
        target = int.from_bytes(prg[i+1:i+3], 'little')
        if prg[i] in (0x20, 0x4c, 0x6c) and START <= target < END:
            raw_absolute.append(dict(file=i+16, physical_bank=i//8192,
                                     opcode=prg[i], target=target))
        if (prg[i] == 0xa9 and prg[i+2:i+6] == bytes.fromhex('8d6c01a9')
                and prg[i+7:i+11] == bytes.fromhex('8d6d01a9') and prg[i+11] == 3):
            target = prg[i+1]+256*prg[i+6]
            if START <= target < END:bank3_publishers.append(dict(file=i+16, target=target))

    carry_calls = literal_calls(body, labels['DkjrNativeImportAnchor'], labels['DkjrNativeImportAnchor']+1)
    phase_calls = literal_calls(body, labels['DkjrNativePhase'], labels['DkjrNativePhase']+1)
    shift_calls = literal_calls(body, labels['DkjrNativeShiftCamera'], labels['DkjrNativeShiftCamera']+1)
    sync_calls = literal_calls(body, labels['DkjrNativeCameraSync'], labels['DkjrNativeCameraSync']+1)
    return dict(detached_measurement=True, owning_ROM_SHA256=PIN,
        source_SHA256=SOURCE_SHA, label_SHA256=LABEL_SHA, bytes=END-START,
        span=dict(payload_offset=payload_offset, file_offset=file, physical_CHR=oldp.PAGES[page],
            RAM_bank=3, start=START, end_exclusive=END,
            old_hex=old_code.hex(), new_hex=new_code.hex(),
            old_SHA256=H(old_code), new_SHA256=H(new_code),
            changed_bytes=sum(a != b for a,b in zip(old_code,new_code))),
        funding=dict(short_guard_bytes_saved=3, dead_reason_store_bytes=3,
            accepted_import_wrapper_growth=5, explicit_unreachable_balance_bytes=1,
            new_RAM=0, new_carriers=0, no_padding_or_41_tail_lease=True,
            preserved_reject_PC=0xb779, preserved_life_reset_PC=END),
        retained_delivered_pending_transition=dict(PC=0xb7bb, bytes_hex='2010a24ce1a8',
            source='tools/reference/dkjr_carry_transition_1110_v2.s',
            before_original_fall_distance=True, changed=False),
        old_labels={name:pc for name,pc in old['symbols'].items() if START <= pc < END},
        new_labels={name:pc for name,pc in new['symbols'].items() if START <= pc < END},
        moved_labels=moved, current_external_control=outside,
        current_external_words_to_moved_labels=words,
        reason=dict(address=REASON, named_source_uses=named_reason,
            exact_current_payload_word_occurrences=reason_words,
            direct_instruction_uses=direct_reason,
            indexed_alias_domains=indexed_domains,
            native_indirect_opcodes=indirect, virtual_indirect_SMC_domains=smc,
            closure_scope='Legal source/native callers and initialized bounded lists/OAM/fruit; arbitrary poisoned standalone pointers excluded'),
        lifecycle_current_calls=dict(import_anchor=carry_calls, native_phase=phase_calls,
            shift_camera=shift_calls, camera_sync=sync_calls),
        native_PRG_raw_control_candidates=raw_absolute,
        split_immediate_bank3_publishers=bank3_publishers,
        proposed_cookie_scope=dict(file_offset=oldp.COOKIE_AT, bytes=16,
            current_hex=raw[oldp.COOKIE_AT:oldp.COOKIE_AT+16].hex(),
            future_source_lease_must_cover_required_cookie_encoding=True),
        CPU_executed=False, source_overlay=False, ROM_composed=False,
        outputs_written=0, old_source=old_source, proposed_source=new_source)


if __name__ == '__main__':
    raw = Current.F.Prior.Early.Old.NIGHTLY.read_bytes()
    q = descriptor(raw)
    encoded = json.dumps(q, sort_keys=True, separators=(',', ':'))
    display = {k:v for k,v in q.items() if k not in
               ('old_source','proposed_source','native_PRG_raw_control_candidates')}
    display['native_PRG_raw_control_candidate_counts'] = dict(Counter(
        str(row['physical_bank']) for row in q['native_PRG_raw_control_candidates']))
    display['reason'] = {k:v for k,v in q['reason'].items() if k != 'virtual_indirect_SMC_domains'}
    display['reason']['virtual_indirect_SMC_families'] = dict(Counter(
        row['original_pointer'] for row in q['reason']['virtual_indirect_SMC_domains']))
    print('DKJR_CARRY_CAMERA_DETACHED_PLAN '+json.dumps(display, sort_keys=True, separators=(',', ':')), flush=True)
    print('DKJR_CARRY_CAMERA_DETACHED_PLAN_SHA256 '+H(encoded.encode()), flush=True)
