"""Read-only source/linked-table constraints for the proposed WWF owner release."""
from pathlib import Path
import collections,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import wwf_resource_inventory_1031_v1 as I
import wwf_action_vm_recovery_1031_v1 as W
J=I.J;O=R/'build/wwf-resource-consumers-1031-v1'

def main():
    assert not O.exists();O.mkdir()
    raw=(J/'candidate.nes').read_bytes();dbg=(J/'candidate.dbg').read_text().splitlines()
    seg={s['id']:s for s in[I.fields(l)for l in dbg if l.startswith('seg\t')]}
    syms=[I.fields(l)for l in dbg if l.startswith('sym\t')]
    used=set()
    def symbol(n):
        q=[s for s in syms if s.get('name')==n and 'val'in s]
        values={(s['val'],s.get('seg'))for s in q};assert len(values)==1,(n,values)
        return q[0]
    def read(n,count):
        s=symbol(n);g=seg[s['seg']];off=g['ooffs']+s['val']-g['start'];used.add(n)
        assert 0<=off<len(raw)-count
        return list(raw[off:off+count])
    cd=read('CdPoseChrLo',60);assert set(cd)==set(range(412&255,425&255))
    cdh=read('CdPoseChrHi',60);assert set(cdh)=={1}
    t=read('TnBodyChr',99);assert min(t)==92 and max(t)==114
    m=read('M3Form0ChrLo',81);delta=read('MbChrOffsets',7)
    m3pages=sorted({512+((p+d)&255)for p in m for d in delta})
    assert max(m3pages)<546
    linked=dict(CD_body_pages=sorted({256+a for a in cd}),CD_world_page=symbol('CdWorldChr')['val'],CD_table_count=60,
        TMNT_body_table_count=99,TMNT_body_pages=sorted({512+a for a in t}),TMNT_possible_paired_pages=sorted({513+a for a in t}),TMNT_equipment_page=628,
        M3_forms=7,M3_frame_entries=81,M3_body_superset=m3pages,M3_world_pages=[544,545],M3_new_alternates=[969,1019])
    assert linked['CD_world_page']==425
    art=json.loads((R/'build/wwf-roster-source-review-v1/wrestlers.json').read_text())
    per_wrestler=[]
    for c in art['characters']:
        poses=[p for p in art['poses']if p['character']==c['id']]
        per_wrestler.append(dict(id=c['id'],name=c['name'],poses=len(poses),flat_record_and_index_bytes=sum(1+4*len(p['packed_8x16_cells'])+4 for p in poses),original_pages_used=len({p['packed_page']for p in poses}),theme=c['theme']))
    original=W.W.raw();mem=bytearray(65536);mem[0x8000:]=original[:32768];mpu=MPU(memory=mem);d=Disassembler(mpu)
    pointers=collections.defaultdict(list);direct=collections.defaultdict(list);instructions=[]
    blocks=json.loads((R/'build/wwf-action-source-lab-v2/build-proof.json').read_text())['variants']['native']['spans'][:5]
    for b in blocks:
        pc=b['start'];end=pc+b['size']
        while pc<end:
            n,s=d.instruction_at(pc);mn,mode=mpu.disassemble[mem[pc]]
            if mode in ['iny','inx','ind']:
                ptr=mem[pc+1]if mode!='ind'else mem[pc+1]+256*mem[pc+2]
                pointers[ptr].append(dict(native_PC=pc,instruction=s))
            elif mode in ['zpg','zpx','zpy']:direct[mode].append(dict(native_PC=pc,address=mem[pc+1],instruction=s))
            instructions.append(dict(pc=pc,size=n,mnemonic=mn,mode=mode));pc+=n
    source_files=[J/'src'/n for n in ['chip_dale_render.s','chip_dale_art.inc','chip_dale_core.s','chip_dale_motion.s','tmnt_state.inc','tmnt_draw.s','tmnt_art.inc','tmnt_equipment_draw.s','tmnt_dispatch.s','tmnt_animation.inc','smb3_mario_render.s','smb3_mario_art.inc','smb3_mario_world.s','smb3_mario_world_art.inc','mmc5_expanded.s','chr_map_mmc5.inc','new_roster_dispatch.s','cf_menu_body.inc','full_roster_menu.s','full_roster_menu_art.inc','audio.s','reset.s','mike_jones.s','mike_jones_dispatch.s','mike_jones_core.s','mike_jones_art.inc']]
    source_files += [J/'entrypoint.s',J/'union.s',J/'smb3plus_body_host.s',J/'smb3plus_float_data.s',J/'smb3plus_float_state.inc']
    assert all(p.is_file()for p in source_files)
    # Verify proposed tails are literal zero, no emitted segment or symbol occupies them.
    tails=[]
    for owner,lo,hi in [('CD_CHR_MEM',426,460),('M3_CHR_MEM',546,604),('TMNT_CHR_MEM',629,668)]:
        first=16+1048576+lo*1024;last=16+1048576+hi*1024
        emit=[s for s in seg.values()if s.get('size')and 'ooffs'in s and s['ooffs']<last and first<s['ooffs']+s['size']]
        assert not emit,(owner,emit)
        assert not any(raw[first:last]),owner
        tails.append(dict(retained_owner=owner,pages=[lo,hi],bytes=last-first,zero_sha256=hashlib.sha256(raw[first:last]).hexdigest(),no_emitted_segments=True,allocated_to_WWF=False))
    # MIKE_CORE is the sole emitted A96 segment; its actual endpoint is A936.
    g=next(s for s in seg.values()if s['name']=='MIKE_CORE');assert g['start']==0xa000 and g['size']==0x936 and g['ooffs']==16+96*8192
    a,z=16+96*8192+0x936,16+97*8192
    assert all(v==255 for v in raw[a:z])
    resident=dict(owner='X5_NEW_60 / MIKE_CORE',physical_bank=96,A_view=[0xa936,0xc000],bytes=z-a,preimage_sha256=hashlib.sha256(raw[a:z]).hexdigest(),allocated_to_WWF=False)
    q=dict(passed=True,read_only=True,no_allocation=True,candidate=I.sha(J/'candidate.nes'),linked_table_closure=linked,proposed_retained_owner_tails=tails,PRG_resident_candidate=resident,
        script_code_relocation=dict(original_code_bytes=3248,direct_ZP_expansion_sites={k:len(v)for k,v in direct.items()},expanded_code_bytes_before_branch_fixes=3248+sum(len(v)for v in direct.values()),indirect_pairs={hex(k):v for k,v in pointers.items()},all_direct_sites=direct,conditional_branch_count=sum(x['mode']=='rel'for x in instructions),notes=['Counted direct-ZP sites are real instruction growth if relocated to selected C2 absolute state. Indexed-wrap and liveness semantics still require source-symbol relocation/oracle proof.','Do not allocate or swap107ZP bytes. Only true indirect pairs need scoped native R0..7 and IRQ-safe binding.']),
        WWF_selected_metadata=per_wrestler,WWF_menu_to_original_identity=[5,0,1,2,3,4],WWF_slot=28,WWF_raw=29,WWF_variant_bits='FmGroups &7',
        exact_proposed_CFG_splits=[dict(old='CD_CHR_MEM $67000/$c000',prefix='$67000/$3800',tail='$6a800/$8800'),dict(old='M3_CHR_MEM $83000/$14000',prefix='$83000/$5800',tail='$88800/$e800'),dict(old='TMNT_CHR_MEM $97000/$10000',prefix='$97000/$6400',tail='$9d400/$9c00')],
        source_constraints=['CdSetPose consumes only linked60-entry CdPoseChrLo; source60-pose records end424; CdDrawWorld selects425.','TnSetPose reads99-entry TnBodyChr; possible paired publication stays<=627; TnDrawEquipment explicitly selects628.','M3 original7form/81frame superset stays below546, world544/545; new Toad/Peach body uses independent969..<1019.','Current global legacy ChrPhysicalMap addresses only original low physical region; proposed high tails are reached through explicit extended publishers.','Exact byte-identical CFG-only relink and all metadata/page outputs remain the next resource-baseline proof; no owner release is implied.'])
    bound=source_files+[Path(__file__),Path(I.__file__),J/'candidate.nes',J/'candidate.dbg',J/'private.cfg',R/'build/wwf-roster-source-review-v1/wrestlers.json',R/'build/wwf-action-source-lab-v2/build-proof.json',W.W.ROM]
    q['bindings']={str(p.resolve()):I.sha(p)for p in bound}
    (O/'consumers.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','linked_table_closure','PRG_resident_candidate','WWF_selected_metadata']}))
    print(json.dumps(q['script_code_relocation']['direct_ZP_expansion_sites']));print('indirect',list(pointers))
if __name__=='__main__':main()
