"""Broaden the complete corner oracle to the signed level origin and aliases."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-sophia-head-axis-d'
G=V/'ryu49-head-status-bridge-g';sys.path.insert(0,str(G))
spec=importlib.util.spec_from_file_location('head_origin_bus',G/'check.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);CPU=g.loadcpu().NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=D/'origin-and-query-d.json';assert not out.exists()
    proofs=[]
    for mapper in ['mmc3','mmc5']:
        old=g.Image(V/f'root49-sophia-head-axis-c/source/build/smb-crossover-{mapper}.nes')
        im=g.Image(D/f'source/build/smb-crossover-{mapper}.nes');L=im.ram
        assert old.ram==im.ram
        def call(image,entry,values,tile=0x54):
            ram=bytearray(10240)
            def put(n,v):
                n,_,off=n.partition('+');ram[g.at(L[n]+int(off or 0))]=v&255
            defaults=dict(SelectedCharacter=11,OperMode=1,GameEngineSubroutine=8,Player_State=1,Player_Y_HighPos=1,
                          Player_X_Position=0,Player_PageLoc=0,Player_Y_Position=172,Player_Y_Speed=252,
                          RyWallOldX=0,RyWallOldPage=0,RyWallOldY=176,RyWallSupported=1,
                          RgTempX=0,RgTempPage=0,RgTempY=176,RgTemp2=192,SmTemp=30)
            defaults.update({'MmVY+2':252,'MmYFraction+1':128,'CurrentBankC':36})
            defaults.update(values)
            for n,v in defaults.items():put(n,v)
            for seg in image.segs.values():
                if seg['name']=='SMCCODE':ram[seg['start']:seg['start']+seg['size']]=image.raw[seg['ooffs']:seg['ooffs']+seg['size']]
            x=defaults['RgTempPage']*256+defaults['RgTempX']
            address=L['Block_Buffer_1']+(x//256%2)*208+(x%256//16)+((defaults['RgTempY']-32)//16)*16
            ram[g.at(address)]=tile
            h=image.hook(entry);put('CurrentBank',h['physical_bank']|(128 if image.mapper==5 else 0))
            if image.mapper==4:put('BankShadow',0x47)
            sp=233;ram[sp+257]=(g.RET-1)&255;ram[sp+258]=(g.RET-1)>>8
            return g.execute(image,CPU,ram,[11,0,30,0x81,sp],{0x8000:62,0xA000:h['physical_bank'],0xC000:36,0xE000:63},h['address'],g.RET,native_status=True)
        a=call(old,'SophiaHeadSourceAxis',{})
        b=call(im,'SophiaHeadSourceAxis',{})
        assert not(a['regs'][3]&1) and b['regs'][3]&1,('Retained C signed-origin negative and D correction',mapper)
        # A real origin center tile is still a ceiling with stationary X.
        a=call(old,'SophiaSourceHeadProbe',{})
        b=call(im,'SophiaSourceHeadProbe',{})
        assert a['regs'][0]==0 and b['regs'][0]==0x54
        assert b['ram'][g.at(L['SmCeilingHit'])]==128
        normal=[]
        for page in [0,1,2,15]:
            for column in [0,15]:
                for tile in [0,0x12,0x54,0x61,0xc2,0xc3,0xff]:
                    values=dict(Player_PageLoc=page,RgTempPage=page,RgTempX=column*16,Player_X_Position=100)
                    a=call(old,'SophiaTerrainQuery',values,tile)
                    b=call(im,'SophiaTerrainBoundedQuery',values,tile)
                    assert a['regs']==b['regs'] and a['ram']==b['ram'] and a['banks']==b['banks']
                    assert [(a,v)for pc,op,a,p,v in a['trace']]==[(a,v)for pc,op,a,p,v in b['trace']]
                    normal.append(b['cycles']-a['cycles'])
        negative=[]
        for tile in range(256):
            values=dict(Player_PageLoc=0,RgTempPage=255,RgTempX=254)
            a=call(old,'SophiaTerrainQuery',values,tile)
            b=call(im,'SophiaTerrainBoundedQuery',values,tile)
            assert a['regs'][0]==tile and b['regs'][0]==b['ram'][g.at(L['R3'])]==0
            assert b['regs'][1:3]==[0,30] and b['regs'][4:]==a['regs'][4:]
            negative.append(b['cycles']-a['cycles'])
        assert set(normal)=={12}
        proofs.append(dict(mapper=mapper,retained_C_origin_head_return=0,D_origin_head_return=0x54,
                           normal_query_cases=len(normal),positive_query_added_cycles=12,
                           all256_aliased_tiles_suppressed=True,negative_query_cycle_delta=sorted(set(negative))))
    out.write_text(json.dumps(dict(status='PASS_SIGNED_ORIGIN_AND_ALL256_NEGATIVE_QUERY_ALIASES',script_sha256=sha(__file__),proofs=proofs,
                                  preparation_cost_correction='Initial11cycle estimate was one short: actual absolute LDA makes the normal bounded-query tail12CPUcycles. Existing fast feet never call this slow wrapper.'),indent=2)+'\n')

    # Reuse B's entire independent mathematical oracle, expanding to the real
    # nonnegative engine origin instead of wrapping negative host coordinates.
    parent=R/'tools/audit/check_easy49_sophia_head_axis_b.py';text=parent.read_text()
    assert sha(parent)=='787facf79aee5cc5d0f5b294ba7015e048649c81419b16b2934a9101dda43289'
    text=text.replace("D = V / 'root49-sophia-head-axis-b'","D = V / 'root49-sophia-head-axis-d'")
    text=text.replace("'compiled-axis-b.json'","'compiled-axis-c.json'")
    text=text.replace('                nonlocal count','                nonlocal count\n                if prior_x<0 or current_x<0:return')
    text=text.replace('[256, 496, 512, 608, 752, 768, 1024]','[0, 16, 256, 496, 512, 608, 752, 768, 1024]')
    text=text.replace('            rng = random.Random(0x49C0)', '''            for ox in [0,1,32767,32768,32769,65535,65536,98304,131072]:
                for cx in [0,1,32767,32768,32769,65535,65536,98304,131072]:
                    for vx in [0,1,-1]:
                        execute(ox,cx,189*Q,0,192,vx,-Q,0x81)
            rng = random.Random(0x49C0)''')
    a="            assert all(jsr <= i < jsr+3 or append <= i < append+im.sym('SophiaHeadSourceAxis')['size'] for i in delta)"
    assert text.count(a)==1
    b="""            oldseg=next(z for z in old.segs.values()if z['name']=='SOPHIA_TERRAIN_COLD')
            query=old.hook('SophiaTerrainQuery')['address']
            op=bytes([0x20,query&255,query>>8])
            calls=[i for i in range(oldseg['ooffs'],oldseg['ooffs']+oldseg['size']-2)if old.raw[i:i+3]==op]
            assert len(calls)==3
            allowed=set(range(jsr,jsr+5))|set(range(append,append+im.sym('SophiaHeadSourceAxis')['size']+im.sym('SophiaTerrainBoundedQuery')['size']))
            for off in calls:allowed.update(range(off,off+3))
            assert all(i in allowed for i in delta)"""
    text=text.replace(a,b)
    ns={'__file__':__file__,'__name__':'full_origin_axis_d'};exec(compile(text,str(parent),'exec'),ns);ns['main']()
    # Complete unchanged96 and split-ceiling assertions with actual C parent.
    finish=R/'tools/audit/finish_easy49_sophia_head_axis_d.py';s=finish.read_text()
    s=s.replace("D=V/'root49-sophia-head-axis-c'","D=V/'root49-sophia-head-axis-d'")
    s=s.replace("    ns['main']()","    ns['D']=D\n    ns['main']()")
    # The original C metadata-negative is pinned in its original directory.
    s=s.replace("sha(D/'compiled-ig.json')","sha(V/'root49-sophia-head-axis-c/compiled-ig.json')")
    ns={'__file__':__file__,'__name__':'full_origin_original96_d'};exec(compile(s,str(finish),'exec'),ns);ns['main']()


if __name__=='__main__':main()
