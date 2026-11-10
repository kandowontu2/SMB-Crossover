"""Assemble the real Rogue driver and executable paged ROM reader privately.

No scheduler/Main/mixer hook is installed. Complete A480..BFFF source bytes and
all six lower banks remain represented; source PCs retain their +2000 layout.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"tools"), str(ROOT/"tools/audit")]
import rogue_dawn_map_v1 as ref
from py65.devices.mpu6502 import MPU

OUT = ROOT/"build/rogue-dawn-audio-driver-v4"
PAGES = ROOT/"build/rogue-dawn-audio-pages-v3"
SOURCE_GRAPH = ROOT/"docs/qa/rogue-dawn-audio-source-closure-2026-10-28.json"
UPPER_SLOTS = [(91,0x1400,12),(92,0x1500,11),(99,0x1800,8)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def binding(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def labels(path):
    return {n: int(a, 16) for a,n in re.findall(r"^al ([0-9A-Fa-f]+) \.([^\r\n]+)$", Path(path).read_text(), re.M)}


def generate(raw, graph):
    source = ref.cpu_image(raw, a_bank=49, lower_bank=48)
    instructions = {r["pc"]: r for r in graph["instructions"]}
    raw_reads = {r["pc"]:r for r in graph["absolute_ROM_operands"]
                 if 0x8000<=r["target"]<0xa000}
    assert len(raw_reads)==4
    upper_reads={r["pc"]:r for r in graph["absolute_ROM_operands"]
                 if 0xa480<=r["target"]<0xc000 and r["pc"]not in [0xa78e,0xa794]}
    needed_data=set()
    for r in upper_reads.values():
        assert r['mode']in ['abs','aby']
        needed_data.update(range(r['target'],r['target']+(256 if r['mode']=='aby'else 1)))
    groups=[]
    for address in sorted(needed_data):
        if not groups or groups[-1][1]!=address:groups.append([address,address+1])
        else:groups[-1][1]+=1
    assert len(groups)==8 and len(needed_data)==2159
    # Real code-view gaps, not assumptions from FF bytes. All original bytes
    # remain separately preserved in the complete immutable raw-bank view.
    gaps=[[0xa8fb,0xb090],[0xbcb0,0xbf19]]
    preserved=set(range(0xa79c,0xa7aa))|set(range(0xb200,0xb400))
    for r in instructions.values():
        preserved.update(range(r['pc'],r['pc']+len(bytes.fromhex(r['bytes']))))
    assert not any(a in preserved for lo,hi in gaps for a in range(lo,hi))
    placements=[]
    available=[r[:]for r in gaps]
    for lo,hi in sorted(groups,key=lambda r:-(r[1]-r[0])):
        choices=[(end-begin,i)for i,(begin,end)in enumerate(available)if end-begin>=hi-lo]
        assert choices,('Raw direct-data copy does not fit',lo,hi)
        _,i=min(choices)
        begin,end=available[i]
        placements.append(dict(source_start=lo,source_end=hi,view_start=begin,view_end=begin+hi-lo))
        available[i][0]+=hi-lo
    copy_starts={r['view_start']:r for r in placements}
    def copy_address(original):
        matches=[r for r in placements if r['source_start']<=original<r['source_end']]
        assert len(matches)==1,hex(original)
        r=matches[0]
        return r['view_start']+original-r['source_start']
    table=[]
    for label,values in [
        ("RdaAbsoluteReturnLo",[(pc+0x2002)&255 for pc in sorted(raw_reads)]),
        ("RdaAbsoluteReturnHi",[(pc+0x2002)>>8 for pc in sorted(raw_reads)]),
        ("RdaAbsoluteTargetLo",[raw_reads[pc]["target"]&255 for pc in sorted(raw_reads)]),
        ("RdaAbsoluteTargetHi",[raw_reads[pc]["target"]>>8 for pc in sorted(raw_reads)])]:
        table += [label+":"," .byte "+",".join(f"${n:02x}"for n in values)]
    (ROOT/"src/rogue_dawn_audio_absolute_v4.inc").write_text("\n".join(table)+"\n")
    words = {}
    for row in graph["dispatch_descriptions"]:
        for p in [row["address"], row["address"]+2] + list(range(row["table"], row["table"]+16, 2)):
            words[p] = source[p] | source[p+1] << 8
    for p in range(0xa7a0, 0xa7aa, 2):
        words[p] = source[p] | source[p+1] << 8
    assert all(0xa480 <= value < 0xc000 for value in words.values())
    compounds = {
        0xb386: (bytes.fromhex("91e0c8"), "jsr GuestMetroidStoreIndirectY", 3),
        0xba69: (bytes.fromhex("b1ec85ea"), "jsr RdaLoadVolume", 4),
        0xbadc: (bytes.fromhex("bc3806fe3806b1e6"), "jsr RdaAdvanceNote", 8),
        0xbb3d: (bytes.fromhex("b1e6a8"), "jsr RdaLoadNoteY", 3),
    }
    for pc, (data, _, length) in compounds.items():
        assert bytes(source[pc:pc+length]) == data
        interior = set(range(pc+1, pc+length))
        assert not (set(graph["roots"]) & interior)
        assert not [(a,b) for a,b in graph["static_edges"] if b in interior and a not in range(pc,pc+length)]
    aliases = set(words.values()) | {0xa770}
    for r in instructions.values():
        b = bytes.fromhex(r["bytes"])
        if len(b) == 3:
            v = int.from_bytes(b[1:], "little")
            if 0xa480 <= v < 0xc000:
                aliases.add(v)
        elif r["mode"] == "rel":
            aliases.add((r["pc"]+2+(b[1] if b[1]<128 else b[1]-256)) & 65535)
    aliases |= set(instructions)
    lines = ["; Generated actual source49, complete A480..BFFF; source SHA "+ref.EXPECTED]
    lines += [f"RdaN{pc:04X}=RdaUpperStart+${pc-0xa480:04x}" for pc in sorted(aliases)]
    projections = {0x10e:"RdMissileMode", 0x6878:"RdGear", 0x308:"RdVY", 0x61f:"RdBeamSfx"}
    needed = set()
    pc = 0xa480
    while pc < 0xc000:
        if pc in copy_starts:
            row=copy_starts[pc]
            data=bytes(source[row['source_start']:row['source_end']])
            lines.append(f"; Byte-exact raw data {row['source_start']:04X}..{row['source_end']-1:04X} in proved code-view gap")
            for at in range(0,len(data),16):
                lines.append(' .byte '+','.join(f'${v:02x}'for v in data[at:at+16]))
            pc=row['view_end']
            continue
        if pc in compounds:
            data, text, length = compounds[pc]
            lines += [f".assert *-RdaUpperStart=${pc-0xa480:04x},error,\"Source PC layout\"",
                      " "+text+f" ; original49:{pc:04X} {data.hex()}"]
            lines += [" nop"]*(length-3)
            pc += length
            continue
        if pc in instructions:
            r = instructions[pc]
            b = bytes.fromhex(r["bytes"])
            op, mode = MPU.disassemble[b[0]]
            v = int.from_bytes(b[1:], "little")
            operand = ""
            if mode == "rel":
                target = (pc+2+(b[1] if b[1]<128 else b[1]-256)) & 65535
                operand = f"RdaN{target:04X}"
            elif mode == "imm":
                operand = f"#${v:02x}"
                # These two writes construct E2/E3 and E4/E5 code-view pointers.
                # Original BC89 is an instrument configuration literal B3,
                # copied into0628/0629 by B9E4; it must remain byte-exact.
                if pc in [0xb37e,0xb4c2]:
                    assert v in [0xb2,0xb3]
                    operand = f"#${v+0x20:02x}"
            elif mode == "acc":
                operand = "a"
            elif mode != "imp":
                if pc in upper_reads:
                    assert op=='LDA'and mode in ['abs','aby']
                    operand=f'RdaUpperStart+${copy_address(v)-0xa480:04x}'+(',y'if mode=='aby'else'')
                elif pc in raw_reads:
                    assert op=="LDA" and mode in ["aby","abs"],(hex(pc),r)
                    op,operand="JSR","RdaReadAbsoluteY"if mode=="aby"else"RdaReadAbsolute"
                elif 0x4000 <= v <= 0x4017 and len(b) == 3:
                    if v in [0x4011,0x4017]:
                        assert op == "STA" and mode == "abs"
                        operand = "RdaDac" if v == 0x4011 else "RdaFrameControl"
                    elif mode == "aby" or v in [0x4001,0x4003,0x4005,0x4007,0x400b,0x400f]:
                        helper = "GuestNativeStore"+op+f"{v-0x4000:02x}"+("Y" if mode=="aby" else "")
                        needed.add(helper)
                        op, operand = "JSR", helper
                    else:
                        assert mode == "abs" and op in ["STA","STY"]
                        operand = f"GuestNativeApu+${v-0x4000:02x}"
                elif 0x8000 <= v < 0xa000 and len(b)==3:
                    assert op == "LDA" and mode == "aby" and v in [0x8002,0x8003,0x801a,0x804c]
                    op, operand = "JSR", f"RdaRead{v:04X}Y"
                else:
                    if v in projections and len(b)==3:
                        assert op == "LDA"
                        operand = projections[v]
                    elif 0x600 <= v < 0x700 and len(b)==3:
                        operand = f"RdaState+${v-0x600:02x}"
                    elif 0xa480 <= v < 0xc000 and len(b)==3:
                        operand = f"RdaN{v:04X}"
                    else:
                        assert len(b)==2 or v in [0xe0,0xe2], (hex(pc),r)
                        operand = f"${v:02x}" if len(b)==2 else f"${v:04x}"
                    if mode in ["zpx","abx"]:
                        operand += ",x"
                    elif mode in ["zpy","aby"]:
                        operand += ",y"
                    elif mode == "iny":
                        operand = "("+operand+"),y"
                    elif mode == "inx":
                        operand = "("+operand+",x)"
                    elif mode == "ind":
                        operand = "("+operand+")"
            lines += [f".assert *-RdaUpperStart=${pc-0xa480:04x},error,\"Source PC layout\"",
                      " "+op.lower()+(" "+operand if operand else "")+f" ;49:{pc:04X} {b.hex()}"]
            pc += len(b)
        elif pc in words:
            lines.append(f" .word RdaN{words[pc]:04X} ; source pointer49:{pc:04X}")
            pc += 2
        else:
            lines.append(f" .byte ${source[pc]:02x} ;49:{pc:04X}")
            pc += 1
    native = ROOT/"src/rogue_dawn_audio_native_v4.inc"
    native.write_text("\n".join(lines)+"\n")
    # Actual fixed62:C000 RNG. Keep the native branches and source ZP owners.
    from py65.disassembler import Disassembler
    m = ref.cpu_image(raw)
    d = Disassembler(MPU(memory=m))
    pc = 0xc000
    rng = ["RdaOriginalRng:"]
    while True:
        length, text = d.instruction_at(pc)
        op, mode = MPU.disassemble[m[pc]]
        rng.append(f"RdaRng{pc:04X}:")
        if mode == "rel":
            target = (pc+2+(m[pc+1] if m[pc+1]<128 else m[pc+1]-256))&65535
            text = op+f" RdaRng{target:04X}"
        rng.append(" "+text)
        pc += length
        if op == "RTS":
            break
        assert pc < 0xc020
    (ROOT/"src/rogue_dawn_audio_rng_v4.inc").write_text("\n".join(rng)+"\n")
    (OUT/'direct-data-copy-layout.json').write_text(json.dumps(dict(
        copied_bytes=2159,groups=placements,proved_code_view_gaps=gaps,
        static_instruction_and_retained_descriptor_bytes_disjoint=True,
        preserved_native_indirect_views='TransitionA79C..A7AA and wholeB200..B3FF register/description/dispatch region',
        raw_upper_bank_retained_separately=True,
        direct_upper_ROM_loads=len(upper_reads),banked_lower_ROM_loads=len(raw_reads)),indent=2)+'\n')
    return needed


def generate_upper_view(raw, parent):
    """Store31 new raw pages; source page3 reuses an exact lower-depot page."""
    original_pages=[raw[16+49*8192+p*256:16+49*8192+(p+1)*256]for p in range(32)]
    source_lower=[(bank,p,raw[16+bank*8192+p*256:16+bank*8192+(p+1)*256])
                  for bank in [52,48,53,54,50,51]for p in range(32)]
    positions=[(bank,off+i*256)for bank,off,count in UPPER_SLOTS for i in range(count)]
    assert len(positions)==31
    page_map=[];new=[]
    for page,data in enumerate(original_pages):
        match=next((i for i,(_,_,b)in enumerate(source_lower)if b==data),None)
        if match is not None:
            at=16+62*8192+0x1ba7
            bank,high=parent[at+match],parent[at+192+match]
            page_map.append((bank,high))
        else:
            bank,offset=positions[len(new)]
            new.append((page,data,bank,offset))
            page_map.append((bank|0x80,0xa0+(offset>>8)))
    assert len(new)==31 and original_pages[3]in [b for _,_,b in source_lower]
    lines=['; Complete original49 raw data view, separate from relocated instructions.',
           '.import __M3_GFX_SIZE__,__M3_NATIVE_SIZE__,__X5_MENU_UI_SIZE__',
           '.assert __M3_GFX_SIZE__<=$1400,lderror,"M3 graphics crossed reserved raw-audio tail"',
           '.assert __M3_NATIVE_SIZE__<=$1500,lderror,"M3 code crossed reserved raw-audio tail"',
           '.assert __X5_MENU_UI_SIZE__<=$1800,lderror,"Menu code crossed reserved raw-audio tail"']
    for slot,(bank,off,count)in enumerate(UPPER_SLOTS):
        lines.append(f'.segment "ROGUE_AUDIO_UPPER_RAW_{slot}"')
        pages=[r for r in new if r[2]==bank]
        assert len(pages)==count and pages[0][3]==off
        for page,data,_,_ in pages:
            lines.append(f'; Original49 page{page:02X}')
            for n in range(0,256,16):
                lines.append(' .byte '+','.join(f'${v:02x}'for v in data[n:n+16]))
    (ROOT/'src/rogue_dawn_audio_upper_raw_v4.s').write_text('\n'.join(lines)+'\n')
    lines=['.export RdaUpperRawBankTable,RdaUpperRawHighTable','RdaUpperRawBankTable:',
           ' .byte '+','.join(f'${bank:02x}'for bank,_ in page_map),
           'RdaUpperRawHighTable:',
           ' .byte '+','.join(f'${high:02x}'for _,high in page_map)]
    (ROOT/'src/rogue_dawn_audio_upper_map_v4.inc').write_text('\n'.join(lines)+'\n')
    return page_map


def main():
    assert not (OUT/"build-proof.json").exists(), "Keep frozen unit immutable"
    OUT.mkdir(exist_ok=True)
    raw = ref.ROM.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ref.EXPECTED
    assessment=ROOT/'docs/qa/rogue-dawn-upper-audio-storage-readonly-2026-10-29.json'
    assert sha(assessment)=='04bdaf7f8d0ae7510c36fe92b662f940771b0bc920d10077737771601ecbb537'
    storage=json.loads(assessment.read_text())
    assert len(storage['inputs'])==9
    for row in storage['inputs']:
        for key in ['ROM','DBG']:
            assert sha(row[key]['path'])==row[key]['sha256'],row[key]['path']
    graph = json.loads(SOURCE_GRAPH.read_text())["graph"]
    needed = generate(raw, graph)
    parent = PAGES/"candidate.nes"
    assert sha(parent) == "a5c7de098beffc04e3f57036e3e89ac2cc4a6829c738ad69c3b13a6515f99404"
    depot_proof = PAGES/"proof.json"
    depot = json.loads(depot_proof.read_text())
    assert depot["union_input_count"] == 11 and depot["source_bytes_rehomed_from_SMB2_C80_art_overlap"] == 2048
    names = labels(PAGES/"candidate.lbl")
    upper_page_map=generate_upper_view(raw,parent.read_bytes())
    rogue_dbg = ROOT/"build/rogue-dawn-host-hazards-v1/candidate.dbg"
    for line in rogue_dbg.read_text().splitlines():
        if line.startswith("sym\t"):
            n = re.search(r'name="(RdVariant|RdMissileMode|RdGear|RdVY|RdBeamSfx)"',line)
            v = re.search(r'val=(0x[0-9A-Fa-f]+)',line)
            if n and v:
                names[n[1]] = int(v[1],0)
    needed |= set("SelectedCharacter RdVariant RdMissileMode RdGear RdVY RdBeamSfx CurrentBank CurrentBankC RgAudioRam RgAudioCpuZp GuestNativeEnable GuestNativeApu GuestMetroidStoreIndirectY RdaLowerHighTable RdaLowerBankTable".split())
    imports = OUT/"src/driver-imports.inc"
    imports.parent.mkdir(exist_ok=True)
    assert not needed-names.keys(), sorted(needed-names.keys())
    imports.write_text("\n".join(f"{n}=${names[n]:04x}" for n in sorted(needed))+"\n")
    leases = [(62,0x1d27,0x2000),(97,0x409,0x2000)]+[(b,off,off+count*256)for b,off,count in UPPER_SLOTS]
    old = parent.read_bytes()
    for bank,lo,hi in leases:
        assert old[16+bank*8192+lo:16+bank*8192+hi] == b"\xff"*(hi-lo)
    cfg = (PAGES/"overlay/smb1base-mmc5-expanded.cfg").read_text()
    for name in ['M3_GFX','M3_NATIVE','X5_MENU_UI']:
        pattern=r'(?m)^(\s*'+name+r':[^\n;]+);'
        assert len(re.findall(pattern,cfg))==1
        cfg=re.sub(pattern,lambda m:m[1]+',define=yes;',cfg)
    mem = {int(b,16):name for name,b in re.findall(r"^\s*(\w+):[^\n]*bank\s*=\s*\$([0-9a-f]+);",cfg,re.M|re.I)}
    starts={name:int(start,16)for name,start in re.findall(r"^\s*(\w+):\s*start\s*=\s*\$([0-9a-f]+)",cfg,re.M|re.I)}
    extra = f'    ROGUE_AUDIO_ADAPTER_A62:load={mem[62]},type=ro,start=$bd27,optional=yes;\n    ROGUE_AUDIO_DRIVER_C97:load={mem[97]},type=ro,start=$c409,optional=yes;'
    for i,(bank,off,_)in enumerate(UPPER_SLOTS):
        extra+=f'\n    ROGUE_AUDIO_UPPER_RAW_{i}:load={mem[bank]},type=ro,start=${starts[mem[bank]]+off:04x},optional=yes;'
    cfg = once(cfg,"}\nSYMBOLS {",extra+"\n}\nSYMBOLS {")
    (OUT/"smb1base-mmc5-expanded.cfg").write_text(cfg)
    builder = (PAGES/"private_builder.py").read_text()
    existing = " if flag: command += ["+repr(str(ROOT/"src/rogue_dawn_audio_pages_v3.s"))+"]"
    builder = once(builder,existing,existing+"\n if flag: command += ["+repr(str(ROOT/"src/rogue_dawn_audio_driver_v4.s"))+","+repr(str(ROOT/"src/rogue_dawn_audio_upper_raw_v4.s"))+"]")
    private = OUT/"private_builder.py"
    private.write_text(builder)
    command = [sys.executable,"-B",str(private),"--workspace",str(ROOT),"--source-overlay",str(OUT),"--output",str(OUT/"candidate.nes")]
    q = subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    if (OUT/"build.log").exists() and not (OUT/"first-build-negative.log").exists():
        (OUT/"first-build-negative.log").write_bytes((OUT/"build.log").read_bytes())
    (OUT/"build.log").write_text(q.stdout+q.stderr)
    assert q.returncode == 0,q.stdout+q.stderr
    output = OUT/"candidate.nes"
    new = output.read_bytes()
    assert len(new)==len(old) and new[:16]==old[:16] and new[16+1048576:]==old[16+1048576:]
    for bank in range(128):
        for off,(a,b) in enumerate(zip(old[16+bank*8192:16+(bank+1)*8192],new[16+bank*8192:16+(bank+1)*8192])):
            if a != b:
                assert any(bank==cb and lo<=off<hi for cb,lo,hi in leases),(bank,off)
    s = labels(OUT/"candidate.lbl")
    assert s["RdaUpperStart"]==0xc480 and s["RdaUpperEnd"]==0xe000
    assert new[16+97*8192+0x1c89:16+97*8192+0x1c8b] == bytes.fromhex("a9b3"), "Actual instrument literal is not a relocated pointer"
    for page,(bank,high)in enumerate(upper_page_map):
        at=16+(bank&127)*8192+(high-0xa0)*256
        assert new[at:at+256]==raw[16+49*8192+page*256:16+49*8192+(page+1)*256]
    report = dict(status="ASSEMBLED_PRIVATE_SOURCE_UNIT_NOT_YET_DIFFERENTIAL_QUALIFIED",native_run=False,
                  original=ref.binding(ref.ROM),parent=binding(parent),candidate=binding(output),
                  upper_source_bytes=7040,all_upper_PCs_preserved_plus_2000=True,
                  lower_source_banks_byte_complete=True,adapter_bytes=s["RdaAdapterEnd"]-s["RdaAdapterStart"],
                  original_upper_raw_view_bytes=8192,new_upper_storage_bytes=7936,
                  instrument_literal_BC89_preserved_B3=True,
                  lower_depot_union_rehome_proof=binding(depot_proof),
                  original_upper_raw_pages_reconstructed_exact=32,
                  direct_upper_data_copy=binding(OUT/'direct-data-copy-layout.json'),
                  actual_storage_union_review=binding(assessment),
                  preceding_owners_have_link_time_size_caps=True,
                  no_scheduler_or_mixer_hooks=True,consumer_exclusive_APIs=True,
                  source_graph_instructions=len(graph["instructions"]),
                  limitations="Actual assembled differential, complete data reads/contexts, IRQ safety and native audio remain open. Source4011/4017 requests are private buffered bytes, not hardware publications; final mixed APU/DMC policy remains open.",
                  command=command,bindings=[binding(p) for p in [Path(__file__),SOURCE_GRAPH,imports,private,OUT/"smb1base-mmc5-expanded.cfg",ROOT/"src/rogue_dawn_audio_driver_v4.s",ROOT/"src/rogue_dawn_audio_native_v4.inc",ROOT/"src/rogue_dawn_audio_rng_v4.inc",ROOT/"src/rogue_dawn_audio_absolute_v4.inc",ROOT/"src/rogue_dawn_audio_upper_raw_v4.s",ROOT/"src/rogue_dawn_audio_upper_map_v4.inc",rogue_dbg]])
    (OUT/"build-proof.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ["status","candidate","adapter_bytes","upper_source_bytes"]}))


if __name__=="__main__":
    main()
