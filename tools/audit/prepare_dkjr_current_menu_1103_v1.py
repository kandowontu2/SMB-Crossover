"""Current32-slot DK Jr frontend study; memory only, no ROM or admission.

The Prince159 + exact approved105 frontend are explicit read-only inputs.
"""
from pathlib import Path
import copy,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit'),str(R/'tools/reference')]
import prepare_prince_backdrop_manifest_1103_v159 as P
import audit_bub_menu_frontend_1102_v1 as F
import check_hogan_current_bounded_v1 as N
import dkjr_original_cpu_1102_v1 as D
from check_tmnt_render_oa import address,location
from inventory_playable_menu_1101_v3 import menu_name
O=R/'build/dkjr-menu-current-1103-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()
off=lambda bank,pc:16+bank*8192+pc-0xa000


def current():
    b,q=P.image();raw=bytearray(b['raw']);grant=R/'docs/qa/allocations/prince-current-frontend-1103-v105.json';g=json.loads(grant.read_text())
    assert g['granted'] and q['expected_memory_only_SHA256']=='b303e4451694cf5c8555eb53b268adfe17bed37fc9bd6207bc8b5c9f56b5b82d'
    for row in g['approved_exact_patches']:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex']);assert raw[at:at+len(old)]==old;raw[at:at+len(new)]=new
    return dict(b,raw=bytes(raw)),q,g


def seed(b,slot):
    m=N.fresh(b);N.put(m,CrossoverMenuIndex=slot,CmActive=0);m[0x5ffe]=0
    F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection');return m


def main():
    O.mkdir(exist_ok=True);b,q,g=current();m=seed(b,27)
    syms={n:dict(pc=address(b,n),file=location(b,n))for n in ['QueueSelection','NrQueueSelectName','QueueSelectName','DrawSelectionPreview','DkPortrait','DkSetPose','DkMenuRecord','FmDrawPreviewSelected','X5SetPhysicalChr','X5ClearChrModes','MenuPreviewBudget','FmStartRetireFlags']if n in b['syms']}
    at=address(b,'Sprite_Data');buf=address(b,'VRAM_Buffer1')
    out=dict(passed=True,probe_only=True,ROM_written=False,current_memory_SHA256=sha(b['raw']),Prince159_preserved=True,frontend105_preserved=True,DK_name=menu_name(m),DK_OAM=list(m[at:at+80]),DK_commands=F.commands(m),DK_CHR=[N.get(m,'CurrentCHRBank',i)for i in range(8)],symbols=syms,codec_tail_SHA256=sha(b['raw'][off(66,0xb02e):off(66,0xb0c0)]))
    c,frames=D.active();D.frame(c,0)
    out['original_Jr_idle']=dict(frames=frames,state=D.state(c),OAM=list(c.memory[0x210:0x230]),palette=list(c.memory.ppu[0x3f11:0x3f14]))
    (O/'current-input-v1.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))


if __name__=='__main__':main()
