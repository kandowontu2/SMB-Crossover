from pathlib import Path
D=Path(__file__).resolve().parent;t=(D/'build_mmc3_static_call_v29.py').read_text();t=t.replace("O=D/'mmc3-static-call-v29'","O=D/'mmc3-static-call-v31'")
anchor="add('src/mmc3.s',old,new);recipe.write_text(json.dumps(m,indent=2));source=O/'source'"
replacement='''tiny,common=new.split('.segment "LOWCODE"\\n',1)
assert common.startswith('FarCallCommon:')
common=common.replace('FarCallCommon:','::FarCallCommon:',1)
add('src/mmc3.s',old,tiny)
# Use a genuinely resident92-byte leaf slot, not the banked status wrapper.
# Its RAM-only cell-reset body moves to a verified empty A-window ROM bank;
# the18-byte rare-call trampoline and49-byte static dispatcher fit the slot.
import re
cfg=(V/'source/smb1base-mmc3-oversized.cfg').read_text();parent=(V/'candidate.nes').read_bytes();empty=[]
for bank in range(228,254):
 if parent[16+bank*8192:16+(bank+1)*8192]!=bytes([255])*8192:continue
 z=re.search(r'^\\s*(\\w+):\\s*start=\\$a000,size=\\$2000,.*?bank=\\$'+format(bank,'02x')+r';',cfg,re.M)
 if z:empty.append((bank,z[1]))
assert empty;bank,memory=empty[0]
add('smb1base-mmc3-oversized.cfg','    M3_CALL_PADDING: load=PRGA_01,type=ro;','    M3_CALL_PADDING: load=PRGA_01,type=ro;\\n    M3_CELL_RESET: load='+memory+',type=ro;')
text=(V/'source/src/megaman_weapons.s').read_text();begin=text.index('.proc MegaManResetBlockHealth\\n');end=text.index('.endproc',begin)+len('.endproc');body=text[begin:end]
cold=body.replace('.proc MegaManResetBlockHealth','.proc M3ResetBlockHealthCold',1).replace('    rts','    jmp BillNativeCaptureP').replace('  rts','  jmp BillNativeCaptureP')
assert cold.count('jmp BillNativeCaptureP')==2
stub='.proc MegaManResetBlockHealth\\n  BillRareCall M3ResetBlockHealthCold\\n'+common+'  .res 92-(*-MegaManResetBlockHealth),$ea\\n  .assert *-MegaManResetBlockHealth=92,error,"Resident cell-reset slot retained"\\n.endproc\\n.pushseg\\n.segment "M3_CELL_RESET"\\n'+cold+'\\n.popseg'
add('src/megaman_weapons.s',body,stub)
recipe.write_text(json.dumps(m,indent=2));source=O/'source' '''
assert t.count(anchor)==1;t=t.replace(anchor,replacement);t=t.replace('resident LOWCODE bank','resident cell-reset-slot bank');t=t.replace('resident immutable bank dispatcher','resident immutable bank dispatcher in the original92-byte cell-reset slot');(D/'build_mmc3_static_call_v31.py').write_text(t)
