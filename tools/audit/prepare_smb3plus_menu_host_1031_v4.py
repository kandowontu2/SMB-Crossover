"""Append to the existing A81 segment; the main object is at its segment cap."""
from pathlib import Path
import json

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/prepare_smb3plus_menu_host_1031_v3.py'
    text=prior.read_text()
    text=text.replace("O=R/'build/smb3plus-menu-host-1031-v3'","O=R/'build/smb3plus-menu-host-1031-v4'")
    # The nested producer replacement sets the real v1-derived output name.
    text=text.replace("O=R/'build/smb3plus-menu-host-1031-v3'","O=R/'build/smb3plus-menu-host-1031-v4'")
    a=text.index("    c=P.once(c,'    ROGUE_RELOC_PAGE_4:")
    z=text.index('    P.B.write(cfg,c)',a)
    text=text[:a]+text[z:]
    assert text.count('.segment \\"SMB3PLUS_MENU_NAME\\"')==1
    text=text.replace('.segment \\"SMB3PLUS_MENU_NAME\\"','.segment \\"RIVER_CITY_CORE\\"')
    text=text.replace("old_cart=P.B.read(parent/'candidate.nes') if False else (parent/'candidate.nes').read_bytes()",
        "old_cart=(parent/'candidate.nes').read_bytes()")
    namespace={'__file__':str(Path(__file__).resolve()),'__name__':'private_smb3_menu_v4'}
    exec(compile(text,str(prior),'exec'),namespace);namespace['main']()
    O=R/'build/smb3plus-menu-host-1031-v4';P=namespace['P'] if 'P' in namespace else None
    p=O/'source-stage.json';d=json.loads(p.read_text())
    import hashlib
    def sha(x):return hashlib.sha256(Path(x).read_bytes()).hexdigest()
    negative=R/'build/smb3plus-menu-host-1031-v3/main-build.json'
    d['bindings'].update({str(x):sha(x) for x in [prior,negative]})
    d['retained_preparation_negatives'].append(str(negative))
    d['storage']+=' The helper is appended to the existing RIVER_CITY_CORE segment at B05B; no new assembler segment is introduced.'
    p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()
