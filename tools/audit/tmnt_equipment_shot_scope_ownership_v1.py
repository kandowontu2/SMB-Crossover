"""Fused shot source ownership, literal uncommon paths and full cold-domain costs."""
from pathlib import Path
from collections import Counter
import argparse
import itertools
import json
from py65.disassembler import Disassembler
from check_tmnt_render_oa import load,address,location,Memory
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
from tmnt_equipment_empty_scans_cpu_v1 import execute,outcome,qualified_cache
from tmnt_native_storage_driver import ROOT,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    old,new=load(a.baseline),load(a.candidate)
    for b,path in[(old,a.baseline),(new,a.candidate)]:qualified_cache[id(b)]=qualified(path)
    assert qualified(a.baseline).items()<=qualified(a.candidate).items()
    bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    assert all(bank(old['raw'],n)==bank(new['raw'],n)for n in range(128)if n!=87)
    assert bank(old['raw'],87)[0x1500:0x1700]==bank(new['raw'],87)[0x1500:0x1700]
    src=a.candidate.parent/'source';cfg=(src/'smb1base-mmc5-expanded.cfg').read_text()
    assert 'TN_SWEEP_C87_MEM: start=$d500, size=$0200'in cfg and'TN_EQUIP_FAST_MEM: start=$b700, size=$0900'in cfg
    text=(src/'src/tmnt_equipment_draw.s').read_text()
    assert text.count('jsr TnExactIconRender')==text.count('jsr TnExactShurikenRender')==1
    before_shot=text[text.index('ShotPointer:'):text.index('NextShot:')]
    assert 'ShotPointer:\n jmp TnShotOwnerScope\n' in before_shot and' lda #1\n sta R7\n lda #0\n sta R3\n jsr TnExactShurikenRender'in before_shot
    icon=text[text.index('::TnEquipmentIconResume:'):text.index('Ammo:jsr TnAmmoHud')]
    assert ' ldy #1\n jsr TnWorldPointer\n lda #128\n sta R4\n lda #0\n sta R5\n sta R3\n lda #23\n sta R6\n lda #1\n sta R7\n jsr TnExactIconRender'in icon
    pointer=text[text.index('.proc TnWorldPointer'):text.index('.proc TnWorldScreenX')]
    assert pointer.startswith('.proc TnWorldPointer\n tax\n')and pointer.count('ldx')==0
    screen=text[text.index('.proc TnWorldScreenX'):text.index('.proc TnWorldDraw')]
    assert not any(v in screen for v in[' ldx',' tax',' inx',' dex'])
    ranges=[(address(new,n),address(new,n)+int(new['syms'][n]['size'],0))for n in['TnExactIconRender','TnExactShurikenRender','TnShotOwnerScope']]
    m=Memory(new);m.page(1,87);c=NesMPU(memory=m);dis=Disassembler(c);seen=set();todo=[lo for lo,hi in ranges];targets=[];stores=[]
    permitted={address(new,'CurrentBankC'),address(new,'CurrentOAMOffset'),0x5116}
    permitted|={address(new,'R'+str(i))for i in [0,1,3,4,5,6,7]}
    permitted|={address(new,n)for n in['Sprite_X_Position','Sprite_Y_Position','Sprite_Attributes','Sprite_Tilenumber']}
    while todo:
        pc=todo.pop()
        if pc in seen:continue
        assert any(lo<=pc<hi for lo,hi in ranges),hex(pc)
        seen.add(pc);width,_=dis.instruction_at(pc);op,mode=c.disassemble[m[pc]];assert op not in['???','BRK']
        word=m[pc+1]+256*m[pc+2]if width==3 else None
        if op in['STA','STX','STY','INC','DEC']:
            assert mode in['abs','abx','zpg']and (word if word is not None else m[pc+1]) in permitted,(hex(pc),op,mode,word)
            stores.append(dict(PC=pc,operation=op,address=word if word is not None else m[pc+1],mode=mode))
        if op=='RTS':continue
        if op=='JSR':
            assert mode=='abs'
            if word!=address(new,'TnWorldDraw'):
                assert any(lo<=word<hi for lo,hi in ranges),hex(word);todo.append(word)
            targets.append(dict(PC=pc,target=word));todo.append(pc+width);continue
        if mode=='rel':
            rel=m[pc+1];todo += [pc+width,pc+width+(rel-256 if rel>=128 else rel)]
        elif op=='JMP':
            assert mode=='abs';targets.append(dict(PC=pc,target=word))
            if word not in [address(new,'TnWorldDraw'),qualified(a.candidate)['TnDrawEquipment','NextShot']]:todo.append(word)
        else:todo.append(pc+width)
    assert not any(row['address']in[0x5115,0x5205,0x5206]for row in stores)
    flags=[32|(i&15)|((i&16)<<2)|((i&32)<<2)for i in range(64)];rows=[]
    named=[('normal-empty',dict(seed={'TnGearSelected':0})),
        ('normal-drop',dict(seed={'TnGearSelected':0},drops=[(0,1)])),
        ('normal-private',dict(seed={'TnGearSelected':0},pickups=[(0,4,19,0xb4,0x2e,128,1)])),
        ('normal-three-boomerangs',dict(seed={'TnGearSelected':0},shots=[(i,60+i,3)for i in range(3)])),
        ('normal-three-kiai',dict(seed={'TnGearSelected':0},shots=[(i,72,4)for i in range(3)]))]
    for name,cfg in named:
        for pin in flags:
            cfg=dict(cfg,flags=pin);c,m,_,_=execute(old,cfg);d,n,_,_=execute(new,cfg)
            assert outcome(c,m)==outcome(d,n),(name,pin)
            rows.append(dict(tag=name,P=pin,cfg=cfg,delta=d.processorCycles-c.processorCycles))
    for gear,kind,count,face,offset,page,y in itertools.product([0,1],[2,3,4],range(1,4),[1,2],[0,48,232,248,252],[0,1],[23,176]):
        pose=73 if kind==2 else 60 if kind==3 else 72
        cfg=dict(seed={'TnGearSelected':gear},shots=[(i,pose,kind)for i in range(count)],face=face,offset=offset,page=page,y=y,flags=flags[len(rows)%64])
        c,m,_,_=execute(old,cfg);d,n,_,_=execute(new,cfg);assert outcome(c,m)==outcome(d,n),('Complete kind cold path',cfg)
        rows.append(dict(tag='actual-kind-and-capacity-domain',cfg=cfg,delta=d.processorCycles-c.processorCycles))
    # Explicit arithmetic/flag/edge controls for both admitted and literal paths.
    for pose,face,flag,edge in itertools.product([1,60,72,73,74,75,83],[0,1,2,3,255],flags,range(4)):
        xx,scroll,pp,cam,yy,off=[(128,0,0,0,176,48),(7,8,0,255,23,248),(255,0,255,255,255,252),(8,0,0,0,24,0)][edge]
        cfg=dict(seed={'TnGearSelected':0},shots=[(1,pose,2)],face=face,x=xx,scroll=scroll,page=pp,camera_page=cam,y=yy,offset=off,flags=flag)
        c,m,_,_=execute(old,cfg);d,n,_,_=execute(new,cfg)
        assert outcome(c,m)==outcome(d,n),('Fused full flags/arithmetic/uncommon',cfg)
        rows.append(dict(tag='fused-caller-flags-and-arithmetic',cfg=cfg,delta=d.processorCycles-c.processorCycles))
    grouped={name:dict(cases=len(v),minimum=min(v),maximum=max(v))for name in{r['tag']for r in rows}if(v:=[r['delta']for r in rows if r['tag']==name])}
    positives=[r for r in rows if r['delta']>0]
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
    q=dict(passed=True,source_only=True,native_run=False,accepted=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
        only_bank87_changed=True,all_preexisting_1d741_labels_exact=True,all_audio_banks_and_C87_original_prefix_exact=True,
        A87_tail_declared=[0xb700,0xc000],preserved_C87_span=[0xd500,0xd700],source_role_producers_exact=True,
        one_actual_compiled_caller_per_new_helper=True,source_binding_sha256=sha(src/'src/tmnt_equipment_draw.s'),
        complete_new_helper_control_flow_instructions=len(seen),genuine_direct_targets=targets,complete_write_operand_closure=stores,
        no_foreground_multiplier_RAM_alias_A_bank_switch_or_new_DMC_owner=True,complete_extra_cold_cases=len(rows),grouped=grouped,
        positive_cost_cases=len(positives),maximum_added_cycles=max([r['delta']for r in positives],default=0),
        positive_examples=sorted(positives,key=lambda r:-r['delta'])[:8],all_full_final_state_and_ordered_OAM_hardware_exact=True,
        cases_sha256=sha(a.output/'cases.json'),checker_sha256=sha(Path(__file__)),
        limits='Source/CPU component ownership only. Audio goldens are explicitly inherited by exact unchanged core/data/writer bytes; separate fresh fullAudio interface tests required. No native/NMI/PPU/DMC timing/recovery claim. Seeded gear-off outstanding actors include legal last-ammo depletion controls, not a natural acquisition playthrough.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['genuine_direct_targets','complete_write_operand_closure','positive_examples']}))


if __name__=='__main__':main()
