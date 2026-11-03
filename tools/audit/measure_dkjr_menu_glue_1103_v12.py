"""Link-only size budget for a current Mini-preserving DK Jr UI adapter.

The virtual B400 placement is NOT allocated and is NEVER applied to a ROM,
even in the CPU model. This conservative independent adapter retains Mini's
existing queue, Select and physical-CHR publisher. Its size is an upper bound,
not a claim that no smaller integrated implementation is possible.
"""
import json, re, subprocess
from pathlib import Path
import assess_dkjr_menu_current_1103_v11 as V

R, O = V.R, V.O
SOURCE = '''.setcpu "6502"
.segment "DK_BUDGET"
.export DkQueue,DkToggle,DkOam,DkEnd
Selected=$6002
Pressed=$7308
Index=$7309
Vram=$04af
VramEnd=$04ae
Sprites=$0200
ObjectMetasprite=$06e1
PosePtr=$6b06
CurrentOff=$06de
MiniQueue=$ad3c
MiniOriginal=$ad74
MiniToggle=$b02e
MiniMapSetup=$b0b2
DkQueue:
 php
 pha
 lda Selected
 cmp #40
 beq Own
 pla
 plp
 jmp MiniQueue
Own:
 pla
 plp
 lda #28
 sta Selected
 jsr MiniOriginal
 lda #40
 sta Selected
 ldx #0
FindName:
 lda Vram+1,x
 cmp #$28
 beq Found
 txa
 clc
 adc Vram+2,x
 adc #3
 tax
 bne FindName
Found:
 ; Existing native row is "  DONKEY KONG   ": append authentic JR,
 ; preserving the real native16-byte command and its queue position.
 lda #19
 sta Vram+17,x
 lda #27
 sta Vram+18,x
 ldy #0
 sty ObjectMetasprite
 lda #<ObjectMetasprite
 sta PosePtr
 lda #>ObjectMetasprite
 sta PosePtr+1
 lda #16
 sta CurrentOff
 ldx #15
Copy:
 lda DkOam,x
 sta Sprites,x
 dex
 bpl Copy
 lda #248
 sta Sprites+16
 sta Sprites+20
 ldx VramEnd
 ; Native DK already queued original opaque white30. Jr exchanges the
 ; remaining original skin/brown entries; backdrop/universal untouched.
 lda #6
 sta Vram-2,x
 lda #54
 sta Vram-1,x
 lda #192
 ; Existing Mini setup uses high3/window1, also correct for page960.
 jmp MiniMapSetup
DkToggle:
 php
 pha
 lda Pressed
 and #32
 beq Foreign
 ldx Index
 cpx #27
 bne Foreign
 pla
 plp
 lda Selected
 eor #52
 sta Selected
 sec
 rts
Foreign:
 pla
 plp
 jmp MiniToggle
DkOam:
 .byte 167,80,0,112,167,82,0,120,167,84,0,128,167,86,0,136
DkEnd:
'''


def main():
    ready = json.loads((O / 'readiness-v11.json').read_text())
    assert ready['passed'] and ready['parent_SHA256'] == V.PIN
    raw = V.ROM.read_bytes(); assert V.sha(raw) == V.PIN
    # Bind every reused entry to the exact current Mini compiler output.
    p = R / 'build/mini-mario-menu-1103-v14'
    labels = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$', (p / 'menu.lbl').read_text(), re.M)}
    assert {n: labels[n] for n in ['MiniQueue', 'MiniOriginal', 'MiniToggle', 'MiniMapSetup']} == dict(MiniQueue=0xad3c, MiniOriginal=0xad74, MiniToggle=0xb02e, MiniMapSetup=0xb0b2)
    assert raw[V.off(66, 0xad3c):V.off(66, 0xad7a)] == (p / 'menu.bin').read_bytes()
    code = bytearray((p / 'code.bin').read_bytes()); code[labels['MiniMapSetup'] - 0xb02e + 1] = 3
    assert raw[V.off(66, 0xb02e):V.off(66, 0xb0c0)] == code
    assert raw[V.off(66, 0xb0b2):V.off(66, 0xb0b6)] == bytes.fromhex('a203c88d')
    # These aliases are from the existing public menu ABI, not new RAM.
    b = V.bundle()
    assert V.address(b, 'CurrentOAMOffset') == 0x06de
    stem = O / 'glue-budget-v12'
    stem.with_suffix('.s').write_text(SOURCE)
    stem.with_suffix('.cfg').write_text('MEMORY{P:start=$b400,size=$200,file=%O;}SEGMENTS{DK_BUDGET:load=P,type=ro;}')
    cc = R / 'tools/Windows/cc65/bin'
    for cmd in [[cc / 'ca65.exe', stem.with_suffix('.s'), '-o', stem.with_suffix('.o')],
                [cc / 'ld65.exe', '-C', stem.with_suffix('.cfg'), stem.with_suffix('.o'), '-o', stem.with_suffix('.bin'), '-Ln', stem.with_suffix('.lbl')]]:
        q = subprocess.run(list(map(str, cmd)), capture_output=True, text=True)
        assert q.returncode == 0, q.stderr
    stem.with_suffix('.o').unlink()
    L = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$', stem.with_suffix('.lbl').read_text(), re.M)}
    body = stem.with_suffix('.bin').read_bytes()
    assert len(body) == L['DkEnd'] - L['DkQueue']
    out = dict(passed=True, link_only=True, CPU_behavior_qualified=False,
        parent_SHA256=V.PIN, ROM_written=False, memory_ROM_changed=False,
        allocated_or_available_placement_claim=False, menu_admitted=False,
        virtual_link_address_not_a_lease='B400',
        conservative_independent_adapter_bytes=len(body),
        queue_name_color_preview_bytes=L['DkToggle'] - L['DkQueue'],
        Select_wrapper_bytes=L['DkOam'] - L['DkToggle'],
        exact_original_four_part_OAM_bytes=L['DkEnd'] - L['DkOam'],
        source_funding=dict(horizontal64_to37_recovered_bytes=27,
            focused_resolver_bytes=20, remaining_nav_bytes=7,
            independent_adapter_additional_bytes_unfunded=len(body)-7),
        retained_alias_negative='Initial link-only draft incorrectly declared CurrentOAMOffset04DE. Exact current-symbol assertion rejected it before compilation/output; corrected to actual06DE.',
        integration='QueueSelection3B JMP would target DkQueue; foreign tail is exact MiniQueue. PublicSelect AD39 JMP would target DkToggle; foreign tail is exact MiniToggle. Focused resolver is separatev11. Actual relocation and these operand patches are NOT emitted.',
        preview='Four original8x16 pairs80/82/84/86 at exact physical960[256:384], source palette30/06/36,32x16 full idle. Existing DK family grid silhouette shared. No extra CHR/RAM/slot.',
        limitations=['This is a conservative linked upper-bound budget, not an optimized combined leaf or a resource request to overwriteB400.',
            'Only seven current source-funded nav bytes remain after resolver. The rest of this adapter has no proven placement.',
            'No current Mini code/data, foreign portrait, mapper, manager or Prince105 span is replaced by this measurement.',
            'Actual complete public UI/native/IRQ/FF/PPU-publication qualification must follow a root-reviewed funded placement.'],
        source_files_to_commit=[Path(__file__).relative_to(R).as_posix(), Path(V.__file__).relative_to(R).as_posix()],
        bindings={q.relative_to(R).as_posix():V.sha(q.read_bytes()) for q in [Path(__file__),Path(V.__file__),V.ROM,O/'readiness-v11.json',p/'menu.lbl',p/'menu.bin',p/'code.bin']})
    (O / 'glue-budget-v12.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k:v for k,v in out.items() if k in ['passed','link_only','conservative_independent_adapter_bytes','queue_name_color_preview_bytes','Select_wrapper_bytes','exact_original_four_part_OAM_bytes','source_funding']}))


if __name__ == '__main__': main()
