"""Recover actual Rogue audio control flow without installing an audio port.

The real cartridge and its dispatch tables are authoritative. Stock Metroid
labels are not used to choose instruction PCs or to replace changed effects.
Finite traces supplement the static graph; neither claims native audio timing.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tools/audit")]
import rogue_dawn_map_v1 as ref
import rogue_dawn_audio_owner_v1 as owner
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

OUT = ROOT / "docs/qa/rogue-dawn-audio-source-closure-2026-10-28.json"


def static_graph(raw):
    memory = ref.cpu_image(raw, a_bank=49, lower_bank=48)
    d = Disassembler(MPU(memory=memory))
    word = lambda a: memory[a] | (memory[a+1] << 8)
    # Actual B4BD consumes these ten five-byte descriptions, not stock labels.
    descriptions, dispatch_targets = [], set()
    for at in range(0xb289, 0xb2bb, 5):
        table, continuation = word(at), word(at+2)
        assert 0xb2bb <= table < 0xbc36
        entries = [word(table+i*2) for i in range(8)]
        assert all(0xa000 <= pc < 0xc000 for pc in entries+[continuation])
        dispatch_targets.update(entries+[continuation])
        descriptions.append(dict(address=at, table=table,
                                 fallback=continuation, channel=memory[at+4],
                                 targets=entries))
    # Original transition phase1 increments to2; phases2..6 select this table.
    transition = [word(0xa79c+phase*2) for phase in range(2, 7)]
    assert transition == [0xa7aa, 0xa7b9, 0xa7b9, 0xa7ed, 0xa7d6]
    roots = dispatch_targets | set(transition) | {0xa770}
    # Actual code AND1/TAY constrains Y0..1 before this two-byte nonzero view.
    # No call/branch enters its indexed load; retain the cartridge predicate.
    assert bytes(memory[0xb770:0xb77a]) == bytes.fromhex("2901a8b978b7d0289381")
    nonzero_table_branches = {0xb776: dict(index_range=[0, 1],
                                          table=0xb778, bytes="9381")}
    # Several genuine BNEs are unconditional after nonzero LDX/LDY. Following
    # their impossible fallthrough decodes volume tables as instructions.
    # Track only the immediately established Z/C facts; calls and arithmetic
    # conservatively forget them. Unknown entries retain both real branches.
    todo = [(pc, None, None) for pc in roots]
    code, indirect, refs, edges, states = {}, {}, set(), set(), set()
    nz_ops = {"LDA", "LDX", "LDY", "TAX", "TAY", "TXA", "TYA", "TSX",
              "PLA", "INC", "DEC", "INX", "INY", "DEX", "DEY", "AND",
              "ORA", "EOR", "ASL", "LSR", "ROL", "ROR", "ADC", "SBC",
              "CMP", "CPX", "CPY", "BIT", "PLP"}
    c_ops = {"ASL", "LSR", "ROL", "ROR", "ADC", "SBC", "CMP", "CPX", "CPY", "PLP"}
    while todo:
        pc, z, carry = todo.pop()
        if (pc, z, carry) in states:
            continue
        states.add((pc, z, carry))
        assert 0xa000 <= pc < 0xc000, ("External audio instruction", hex(pc))
        length, text = d.instruction_at(pc)
        op, mode = MPU.disassemble[memory[pc]]
        assert op not in ("???", "BRK", "RTI"), (hex(pc), text)
        data = bytes(memory[pc:pc+length])
        code[pc] = dict(pc=pc, bytes=data.hex(), instruction=text, mode=mode)
        target = word(pc+1) if length == 3 else None
        if length == 3 and target >= 0x8000 and op not in ("JSR", "JMP"):
            refs.add((pc, target, mode))
        next_pcs = []
        if op == "RTS":
            pass
        elif op == "JMP" and mode == "ind":
            assert (pc, target) in [(0xa79d, 0x6ec), (0xb33a, 0xe2),
                                    (0xb359, 0xe2), (0xbc48, 0xe2)], (hex(pc), hex(target))
            destinations = set(transition) if target == 0x6ec else dispatch_targets
            indirect[pc] = dict(pointer=target, destinations=sorted(destinations))
        elif op == "JMP":
            next_pcs = [target]
        elif op == "JSR":
            next_pcs = [target, pc+length]
            z = carry = None
        elif mode == "rel":
            offset = memory[pc+1]
            branch = (pc+2+(offset if offset < 128 else offset-256)) & 65535
            condition = {"BEQ": z, "BNE": None if z is None else not z,
                         "BCS": carry, "BCC": None if carry is None else not carry}.get(op)
            if pc in nonzero_table_branches:
                assert op == "BNE"
                condition = True
            next_pcs = ([branch] if condition is True else [pc+2]
                        if condition is False else [pc+2, branch])
        else:
            next_pcs = [pc+length]
            if op in nz_ops:
                z = (memory[pc+1] == 0 if op in {"LDA", "LDX", "LDY"}
                     and mode == "imm" else True if op == "AND" and mode == "imm"
                     and memory[pc+1] == 0 else None)
            if op in c_ops:
                carry = None
            if op == "CLC":
                carry = False
            elif op == "SEC":
                carry = True
        for nxt in next_pcs:
            edges.add((pc, nxt))
            todo.append((nxt, z, carry))
    return dict(instructions=[code[p] for p in sorted(code)],
                static_edges=sorted(edges), roots=sorted(roots),
                dispatch_descriptions=descriptions,
                indirect_dispatch={hex(k): v for k, v in sorted(indirect.items())},
                absolute_ROM_operands=[dict(pc=p, target=t, mode=m) for p,t,m in sorted(refs)],
                minimum_instruction_PC=min(code), maximum_instruction_PC=max(code))


def main():
    assert not OUT.exists(), "Keep frozen evidence immutable"
    raw = ref.ROM.read_bytes()
    assert ref.digest(raw) == ref.EXPECTED
    graph = static_graph(raw)
    report = dict(status="STATIC_ACTUAL_SOURCE_GRAPH_ONLY", passed=True,
                  native_run=False, source=ref.binding(ref.ROM), graph=graph,
                  scope="Actual49 control flow including all ten original effect/music dispatch tables and valid transition phase targets; ROM data and runtime integration remain separate",
                  bindings=[ref.binding(p) for p in [Path(__file__),
                      ROOT / "tools/rogue_dawn_map_v1.py",
                      ROOT / "tools/audit/rogue_dawn_audio_owner_v1.py"]])
    OUT.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(dict(output=str(OUT.relative_to(ROOT)),
                          instructions=len(graph["instructions"]),
                          minimum_PC=hex(graph["minimum_instruction_PC"]),
                          maximum_PC=hex(graph["maximum_instruction_PC"]))))


if __name__ == "__main__":
    main()
