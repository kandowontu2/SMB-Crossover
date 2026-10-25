from pathlib import Path
import configparser,hashlib,json,shutil,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-ship-lives-v25';O=D/'mmc3-static-call-v33';O.mkdir(exist_ok=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tools=O/'tools';shutil.copytree(V/'tools',tools);recipe=tools/'mmc3_oversized/repairs.json';m=json.loads(recipe.read_text())
def add(path,old,new):
 row=next((z for z in m['text_repairs']if z['path']==path),None)
 if row is None:row=dict(path=path,chunks=[]);m['text_repairs'].append(row)
 row['chunks'].append(dict(old=old,new=new))
add('smb1base-mmc3-oversized.cfg','    SRAM_00:start = $6000,  size = $2000, type = rw, file = "";','    SRAM_00:start = $6000,  size = $2000, type = rw, file = "";\n    M3_CALL_RAM:start=$73fa,size=6,type=rw,file=""; # Explicit final six-byte alignment gap before history.')
add('smb1base-mmc3-oversized.cfg','    SMCCODE:    load = PRGA_01, type = rw,  run = SP,     define = yes;','    SMCCODE:    load = PRGA_01, type = rw,  run = M3_CALL_RAM, define = yes;\n    M3_CALL_PADDING: load=PRGA_01,type=ro;')
old=(V/'source/src/mmc3.s').read_text();begin=old.index('.segment "SMCCODE"');end=old.index('\n  rts',begin)+len('\n  rts\n');old=old[begin:end]
new='''.segment "SMCCODE"
SMCCODE:
; Tiny dynamically addressed call: its return address remains on the ordinary
; CPU stack, while executable bytes live in a proven SRAM alignment gap.
.include "smc.inc"
SMC SafecallA, { lda #SMC_Value }
SMC FarcallJmpTarget, { jmp SMC_AbsAdr }
M3FarReturn: .byte $42
NextBank_SMC=NextBank-1
SafereturnA_SMC=M3FarReturn-1
.export NextBank_SMC,SafereturnA_SMC
.assert SMCCODE=$73fa,error,"MMC3 tiny call uses only the final six-byte gap"
.assert Z2UiState+1<=SMCCODE,error,"Tiny call does not overlap preceding live state"
.assert M3FarReturn+1<=XgLzHistory,error,"Tiny call stays below native audio/history"
.segment "M3_CALL_PADDING"
.res 43,$ea                    ; Preserve the original49-byte A-bank load span.
.segment "LOWCODE"
FarCallCommon:
  ; NextBank is an existing reserved cell. Original code addressed its SMC
  ; immediate instead; all named operand writers retain the same source ABI.
  sta NextBank
  lda CurrentBank
  pha
    lda #7 | PRG_FIXED_8
    sta BankShadow
    sta BANK_SELECT
    lda NextBank
    sta CurrentBank
    sta BANK_DATA
    jsr SMCCODE
    sta M3FarReturn
    lda #7 | PRG_FIXED_8
    sta BankShadow
    sta BANK_SELECT
  pla
  sta CurrentBank
  sta BANK_DATA
  lda M3FarReturn
  rts
'''
tiny,common=new.split('.segment "LOWCODE"\n',1)
assert common.startswith('FarCallCommon:')
common=common.replace('FarCallCommon:','::FarCallCommon:',1)
add('src/mmc3.s',old,tiny)
# Use a genuinely resident92-byte leaf slot, not the banked status wrapper.
# Its RAM-only cell-reset body moves to a verified empty A-window ROM bank;
# the18-byte rare-call trampoline and49-byte static dispatcher fit the slot.
# Append after the unchanged original Gradius driver, in its actual FF tail.
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load
parent_bundle=load(V/'candidate.nes');parent=parent_bundle['raw'];g=next(g for g in parent_bundle['segs'].values()if g.get('name')=='"VIC_NATIVE_AUDIO"');tail=int(g['ooffs'],0)+int(g['size'],0);bank=(tail-16)//8192
assert bank==253 and (tail-16)%8192+96<=8192 and parent[tail:tail+96]==bytes([255])*96
add('smb1base-mmc3-oversized.cfg','    VECTORS:    load = PRGFix, type = ro,  start = $fffa;','    M3_CELL_RESET: load=M3_FREE_FD,type=ro; # Append after native audio; preserve its original bytes.\n    VECTORS:    load = PRGFix, type = ro,  start = $fffa;')
text=(V/'source/src/megaman_weapons.s').read_text();begin=text.index('.proc MegaManResetBlockHealth\n');end=text.index('.endproc',begin)+len('.endproc');body=text[begin:end]
cold=body.replace('.proc MegaManResetBlockHealth','.proc M3ResetBlockHealthCold',1).replace('    rts','    jmp BillNativeCaptureP').replace('  rts','  jmp BillNativeCaptureP')
assert cold.count('jmp BillNativeCaptureP')==2
stub='.proc MegaManResetBlockHealth\n  BillRareCall M3ResetBlockHealthCold\n'+common+'  .res 92-(*-MegaManResetBlockHealth),$ea\n  .assert *-MegaManResetBlockHealth=92,error,"Resident cell-reset slot retained"\n.endproc\n.pushseg\n.segment "M3_CELL_RESET"\n'+cold+'\n.popseg'
add('src/megaman_weapons.s',body,stub)
recipe.write_text(json.dumps(m,indent=2));source=O/'source' 
with(O/'prepare.log').open('w')as log:p=subprocess.run([sys.executable,str(tools/'prepare_mmc3_oversized.py'),'--source-root',str(R),'--output',str(source),'--reference-rom',str(D/'native-probes-qa-v2/candidate.nes')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'prepare.log').read_text()[-2000:]
# Reuse the same frozen external compile/options/header/CHR-differential steps.
helper=D/'build_mmc3_ship_lives_v25.py';suffix=helper.read_text().split('config=configparser.ConfigParser()',1)[1].split('q=dict(',1)[0];exec(compile('config=configparser.ConfigParser()'+suffix,str(helper),'exec'),globals())
q=dict(compiled=True,adopted=False,goal_complete=False,ROM_sha256=sha(rom),parent_ROM_sha256=sha(V/'candidate.nes'),changed_ROM_bytes=len(diff),changed_PRG_banks=sorted(set((i-16)//8192 for i in diff)),new_physical_RAM_bytes=0,new_CHR_bytes=0,tiny_call_and_return_gap=[0x73fa,0x7400],existing_reserved_NextBank=0x13f,hardware_stack_code_bytes=0,compile_helper_sha256=sha(helper),scope='Private architectural MMC3 candidate: resident immutable bank dispatcher in the original92-byte cell-reset slot calls a five-byte LDA/JMP trampoline plus one private return byte in the six-byte alignment gap after Z2UiState/before XgLzHistory. Original49-byte A-bank load span padded, no source character physics or board RAM/CHR expansion. All five named operand data fields, register/flag/bank/IRQ behavior, stack ownership, full native routes and current-hash qualification must be verified. No adoption or gameplay-pass claim.')
(O/'build-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
