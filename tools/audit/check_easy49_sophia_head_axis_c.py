"""Reuse the complete B arithmetic oracle, plus original head/wall fixtures."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
D=V/'root49-sophia-head-axis-c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parent=R/'tools/audit/check_easy49_sophia_head_axis_b.py'
    assert sha(parent)=='787facf79aee5cc5d0f5b294ba7015e048649c81419b16b2934a9101dda43289'
    text=parent.read_text()
    text=text.replace("D = V / 'root49-sophia-head-axis-b'", "D = V / 'root49-sophia-head-axis-c'")
    text=text.replace("'compiled-axis-b.json'", "'compiled-axis-c.json'")
    a='jsr <= i < jsr+3 or append <= i'
    assert text.count(a)==1
    text=text.replace(a,'jsr <= i < jsr+5 or append <= i')
    ns={'__file__':__file__,'__name__':'bound_axis_c_oracle'}
    exec(compile(text,str(parent),'exec'),ns)
    ns['main']()
    # Execute all96 original assertions unchanged on the current private C.
    original=R/'tools/audit/check_easy49_sophia_terrain_ig.py'
    spec=importlib.util.spec_from_file_location('original_terrain_96',original)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.D=D
    mod.main()
    g,CPU=mod.g,mod.CPU
    proofs=[]
    for mapper in ['mmc3','mmc5']:
        im=g.Image(D/f'source/build/smb-crossover-{mapper}.nes')
        L=im.ram
        ram=bytearray(10240)
        def put(n,v):
            n,_,off=n.partition('+')
            ram[g.at(L[n]+int(off or 0))]=v&255
        for seg in im.segs.values():
            if seg['name']=='SMCCODE':ram[seg['start']:seg['start']+seg['size']]=im.raw[seg['ooffs']:seg['ooffs']+seg['size']]
        # Center cell608 is empty. Left corner cell592 is side-only; remaining
        # right point624 is an actual direct ceiling, which must still run.
        fields=dict(SelectedCharacter=11,OperMode=1,GameEngineSubroutine=8,Player_State=1,
                    Player_Y_HighPos=1,Player_PageLoc=2,Player_X_Position=97,Player_Y_Position=172,
                    RyWallSupported=1,RyWallOldX=97,RyWallOldPage=2,RyWallOldY=176,RyWallOldXFrac=128,
                    Player_Y_Speed=252,RgDoubleJump=1)
        fields.update({'MmXFraction':102,'MmXFraction+1':102,'MmYFraction':51,'MmYFraction+1':179,
                       'MmVX':102,'MmVX+1':230,'MmVX+2':255,'MmVY':171,'MmVY+1':170,'MmVY+2':252})
        for n,v in fields.items():put(n,v)
        for x,tile in [(592,0x61),(624,0x54)]:
            a=L['Block_Buffer_1']+(x//256%2)*208+(x%256//16)+((176-32)//16)*16
            ram[g.at(a)]=tile
        h=im.hook('SophiaSourceHeadProbe')
        put('CurrentBank',h['physical_bank']|(128 if im.mapper==5 else 0))
        put('CurrentBankC',36)
        if im.mapper==4:put('BankShadow',0x47)
        sp=233;ram[sp+257]=(g.RET-1)&255;ram[sp+258]=(g.RET-1)>>8
        z=g.execute(im,CPU,ram,[11,0,30,0x81,sp],{0x8000:62,0xA000:h['physical_bank'],0xC000:36,0xE000:63},h['address'],g.RET,native_status=True)
        def rd(n):return z['ram'][g.at(L[n])]
        assert z['regs'][0]==0x54 and rd('SmCeilingHit')==128 and rd('Player_Y_Position')==175
        assert z['ram'][g.at(L['MmYFraction'])+1]==128
        assert z['regs'][1:3]==[0,30] and z['regs'][4:]==[sp+2,g.RET]
        assert z['ram'][sp+257:512]==ram[sp+257:512]
        proofs.append(dict(mapper=mapper,actual_return_tile=z['regs'][0],head_hit=rd('SmCeilingHit'),
                           returned_pointer=[rd('R6'),rd('R7'),rd('R2')],canonical_Y=rd('Player_Y_Position'),cycles=z['cycles']))
    report=dict(status='PASS_COMPLETE_HEAD_SPAN_C_AFTER_REJECTED_SIDE_CORNER',script_sha256=sha(__file__),
                parent_checker_sha256=sha(parent),original96_checker_sha256=sha(original),
                arithmetic=sha(D/'compiled-axis-c.json'),original96=sha(D/'compiled-ig.json'),proofs=proofs,
                qualifications=['Compiled components only. Actual native whole-call capture and ordinary full routes remain separate.'])
    (D/'complete-head-span-c.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'])


if __name__=='__main__':main()
