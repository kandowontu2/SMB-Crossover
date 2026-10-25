"""Compiled palette ownership and public-register/scratch/stack comparisons."""
from pathlib import Path
import collections,hashlib,importlib.util,itertools,json,traceback
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'world-palette-abi-gb'
s=importlib.util.spec_from_file_location('palette_fw_model',V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
at=lambda ad:ad if ad<2048 else ad-0x6000+2048
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def seed(im,char,area,power,offset,variant=0):
    raw=bytearray(10240)
    for seg in im.segs.values():
        if seg['name']=='SMCCODE':raw[seg['start']:seg['start']+seg['size']]=im.raw[seg['ooffs']:seg['ooffs']+seg['size']]
    for n,v in dict(SelectedCharacter=char,AreaType=area,PlayerStatus=power,BillVariant=variant,CurrentBank=3|(128 if im.mapper==5 else 0),VRAM_Buffer1_Offset=offset,PlayerSize=0,NmiDisable=255).items():raw[at(im.ram[n])]=v
    if im.mapper==4:raw[at(im.ram['BankShadow'])]=0x43
    for i in range(8):raw[at(im.ram['R0']+i)]=(19*i+27)&255
    for i in range(offset):raw[at(im.ram['VRAM_Buffer1']+i)]=(i*31+41)&255
    raw[0x1ef]=255;raw[0x1f0]=0x5c
    return raw


def call(im,raw,name,p):
    q=m.execute(im,raw,[199,71,89,p,238],{0x8000:62,0xa000:3,0xc000:12,0xe000:63},im.hook(name)['address'],0x5d00,240)
    assert q['banks']=={0x8000:62,0xa000:3,0xc000:12,0xe000:63}
    if name=='QueueMegaManFacePalette':assert q['selector']==(0x43 if im.mapper==4 else 0x47)
    return q


def queue_y_consumer(im,raw):
    # GetPlayerColors is the sole production caller of QueueMegaManFacePalette.
    # Its next child preserves Y without reading it, then LDY #0 replaces it.
    b=m.Bus(im,raw,{0x8000:62,0xa000:3,0xc000:12,0xe000:63},())
    c=m.q.core.NesMPU(memory=b);c.a,c.x,c.y,c.p,c.sp=199,71,89,0xc5,238
    entry=im.hook('GetPlayerColors')['address'];c.pc=entry;armed=False;replacement=None
    assert b.data[entry]==0x20 and b.data[entry+1]+256*b.data[entry+2]==im.hook('QueueMegaManFacePalette')['address']
    for steps in range(10000):
        if c.pc==0x5d00 and c.sp==240:break
        if c.pc==entry+3:armed=True
        b.pc=c.pc;b.op=b.data[c.pc];mn,mode=c.disassemble[b.op]
        if armed and replacement is None:
            assert mn not in('STY','TYA','INY','DEY','CPY')and mode not in('aby','iny','zpy'),('Internal Y consumed before replacement',hex(c.pc),mn,mode)
            if mn in('LDY','TAY'):
                replacement=dict(PC=c.pc,opcode=b.op,mnemonic=mn)
        popped=b.data[0x100+((c.sp+1)&255)]if b.op in(0x28,0x40)else None
        c.step()
        if popped is not None:c.p=popped&0xcf
    else:raise AssertionError('Bounded real GetPlayerColors caller')
    assert armed and replacement
    return replacement


def main():
    assert not O.exists();O.mkdir();report=dict(status='REVIEWING',groups=[],goal_complete=False);context=None
    try:
        # The actual linked pose/weapon file contains every authored part,
        # including death, hurt, crouch and all three power forms.
        text=(R/'src/rygar_metasprites.inc').read_text()
        spec=importlib.util.spec_from_file_location('palette_fw_tags',R/'tools/reference/tag_player_outlines.py');tags=importlib.util.module_from_spec(spec);spec.loader.exec_module(tags)
        parts=[z for line in text.splitlines()if(z:=tags.PART.fullmatch(line))]
        assert parts and all(int(z[3],16)&3==0 for z in parts)
        report['Rygar_art']=dict(source_sha256=sha(R/'src/rygar_metasprites.inc'),parts=len(parts),all_palette0=True,
            inventory='InventorySupported excludes Rygar in both modes; no selected-weapon icon uses sprite palette3',
            dynamic_paths='ExpandedGraphics clears player palette bits; ExpandedDrawShots and chain explicitly set R3=0. Native movement/pickup/return tests and ordinary replay provide separate execution evidence.')
        identities=[(c,0)for c in range(13)]+[(3,1)]
        for mapper in ('mmc3','mmc5'):
            ims=[m.q.Image(R/f'build/checkpoints/hud-numbers-fl/build/smb-crossover-{mapper}.nes'),m.q.Image(V/f'world-palette-fv/source/build/smb-crossover-{mapper}.nes')]
            assert ims[0].ram==ims[1].ram;L=ims[0].ram
            group=dict(mapper=mapper,ROMs=[sha(im.path)for im in ims],cases=0,entry_costs=collections.Counter(),native_world_palettes={})
            group['internal_Y_first_replacement']=[queue_y_consumer(im,seed(im,7,2,1,0))for im in ims]
            report['groups'].append(group)
            native={}
            for area in range(4):
                q=call(ims[0],seed(ims[0],0,area,0,0),'QueueMegaManFacePalette',1)
                native[area]=list(q['ram'][at(L['VRAM_Buffer1']):at(L['VRAM_Buffer1'])+6]);group['native_world_palettes'][area]=native[area]
            for name in ('QueueMegaManFacePalette','GetPlayerColors'):
                ps=sorted({x&0xcf for x in range(256)})if name=='QueueMegaManFacePalette'else[0,0x49,0xc5]
                offsets=(0,7,28,77)if name=='QueueMegaManFacePalette'else(0,7,28)
                powers=(0,)if name=='QueueMegaManFacePalette'else(0,1,2)
                for (char,var),area,power,offset,p in itertools.product(identities,range(4),powers,offsets,ps):
                    context=dict(mapper=mapper,name=name,char=char,variant=var,area=area,power=power,offset=offset,P=p)
                    a,b=[call(im,seed(im,char,area,power,offset,var),name,p)for im in ims]
                    if name=='QueueMegaManFacePalette'and char==7:
                        assert a['regs'][:2]+a['regs'][3:]==b['regs'][:2]+b['regs'][3:],('internal AX/P/SP',context)
                        assert a['regs'][2]==6 and b['regs'][2]==6*area+12
                    else:
                        assert a['regs']==b['regs'],('full public registers/flags/SP',context,a['regs'],b['regs'])
                    assert a['banks']==b['banks']and a['selector']==b['selector']and a['ports']==b['ports']
                    start=at(L['VRAM_Buffer1'])+offset
                    expected=native[area]if char==7 else list(a['ram'][start:start+6])
                    assert list(b['ram'][start:start+6])==expected,('palette ownership',context)
                    changed={L['VRAM_Buffer1']+offset+i for i in (3,4,5)}if char==7 else set()
                    dead={ad for q in(a,b)for pc,op,ad0,ad,value in q['trace']if 0x100<=ad<=0x1ee and op in(0x08,0x48,0x20)}
                    for i,(v,w)in enumerate(zip(a['ram'],b['ram'])):
                        if v!=w:assert m.q.g.RAMS[i]in changed|dead,('unexpected live RAM',context,hex(m.q.g.RAMS[i]),v,w)
                    assert a['ram'][0x1ef:0x200]==b['ram'][0x1ef:0x200]
                    group['cases']+=1;group['entry_costs'][name+':'+str(b['cycles']-a['cycles'])]+=1
            print(mapper,group['cases'],'compiled palette/caller cases',flush=True)
        report['status']='PASS_RYGAR_WORLD_PALETTE_AND_OTHER_CHARACTER_CALLER_IDENTITY'
    except Exception as error:
        report.update(status='FAILURE_RETAINED',context=context,error=repr(error),traceback=traceback.format_exc());raise
    finally:(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
