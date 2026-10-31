"""Use the actual A81 gap before Rogue audio, not Celeste's occupied tail."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/prepare_smb3plus_menu_host_1031_v1.py'
    text=prior.read_text()
    old="f'.assert *-M3StatusNameDispatch<={old_size},error,\"Existing status span\"\\n.res {old_size}-(*-M3StatusNameDispatch),$ea\\n'"
    assert text.count(old)==1
    text=text.replace(old,"f'.assert *-M3StatusNameDispatch={old_size},lderror,\"Existing status span\"\\n'")
    text=text.replace("O=R/'build/smb3plus-menu-host-1031-v1'","O=R/'build/smb3plus-menu-host-1031-v3'")
    a=text.index("    text=P.once(text,'  lda #28");z=text.index('    P.B.write(names,text)',a)
    text=text[:a]+'''    text=P.once(text,'  lda #28\\n  clc\\n  adc M3Variant\\n  jmp NameIndex\\n',
        '  jmp MbMenuNameSelect\\n  .res 6,$ea\\n')
'''+text[z:]
    at='    P.B.write(status,text)\n'
    extension='''    cfg=J/'private.cfg'
    c=P.B.read(cfg)
    c=P.once(c,'    ROGUE_RELOC_PAGE_4:',
        '    SMB3PLUS_MENU_NAME:load=X5_NEW_51,type=ro,start=$b05b;\\n    ROGUE_RELOC_PAGE_4:')
    P.B.write(cfg,c)
    menu=J/'smb3plus_menu_name.s'
    P.B.write(menu,\"\"\"; Exact A81 gap B05B..B100, after current River City code.
.pushseg
.segment \"SMB3PLUS_MENU_NAME\"
.proc MbMenuNameSelect
 lda M3Variant
 cmp #2
 bcs New
 clc
 adc #28
 jmp NrQueueSelectName::NameIndex
New:
 sec
 sbc #2
 asl
 asl
 asl
 asl
 clc
 adc #<Names
 sta R2
 lda #>Names
 adc #0
 sta R3
 lda #0
 jmp NrQueueSelectName::NamePage
Names:.byte \"   SMB3 TOAD    \",\"   SMB3 PEACH   \"
.endproc
.assert *<=$b100,lderror,\"Preserve Rogue relocation page4\"
.popseg
\"\"\")
    P.B.write(J/'entrypoint.s',P.B.read(J/'entrypoint.s')+'\\n.include \"smb3plus_menu_name.s\"\\n')
'''
    assert text.count(at)==1;text=text.replace(at,at+extension)
    namespace={'__file__':str(Path(__file__).resolve()),'__name__':'private_smb3_menu_v3'}
    exec(compile(text,str(prior),'exec'),namespace)
    P=namespace['P'];h=json.loads(P.B.read(namespace['H']));parent=Path(h['joint'])
    old_cart=P.B.read(parent/'candidate.nes') if False else (parent/'candidate.nes').read_bytes()
    offset=16+81*8192+0x105b
    preimage=old_cart[offset:offset+0xa5]
    assert preimage==bytes([255])*0xa5
    namespace['main']()
    O=namespace['O'];J=namespace['J'];p=O/'source-stage.json';d=json.loads(p.read_text())
    d.pop('menu_name_indices')
    d['storage']='Existing navigation padding funds Select; existing palette NOPs fund status offsets; compact status stays82B. Own name helper/data occupies only the reviewed165B A81 B05B..B100 gap after River City and before Rogue relocation page4. Celeste BB10..C000 is untouched.'
    d['name_resource']=dict(physical_ROM=81,CPU_first='B05B',CPU_end_exclusive='B100',
        bytes_available=165,execution_view='A',preimage_sha256=hashlib.sha256(preimage).hexdigest())
    negatives=[R/'build/smb3plus-menu-host-1031-v1/main-build.json',R/'build/smb3plus-menu-host-1031-v2/final-link.json']
    d['retained_preparation_negatives']=[str(p) for p in negatives]
    d['bindings'].update({str(x):P.B.sha(x) for x in [prior,*negatives,J/'private.cfg',J/'entrypoint.s',J/'smb3plus_menu_name.s']})
    P.B.write(p,json.dumps(d,indent=2)+'\n')


if __name__=='__main__':main()
