"""Resolve target-record ownership and exercise its actual caller/observer."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from link_pit_rygar_sophia_audit_cpu import scoped_load, Arena
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU
from parodius_visibility_hud_static_startup_v1 import MOCK
from final_item_abilities_run import lua

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D/'root-current-roster-composition-v1'
READY = D/'mm-proto-weapon-boundary-v1/native-ready-v3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--output', type=Path, required=True);a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    b = scoped_load(B/'candidate.nes');cfg = json.loads((READY/'native/config.json').read_text())
    script = (READY/'native/run.lua').read_text()
    assert sha(READY/'native/run.lua') == json.loads((READY/'readiness.json').read_text())['script_sha256']
    data_bank = (location(b, 'MmMM_HAIR_STANDRight')-16)//8192
    table_bank = (location(b, 'ProtoShotRightLo')-16)//8192
    off = location(b, 'ProtoDrawShots')
    expected = [0xa9, data_bank|128, 0x8d, address(b,'CurrentBankC')&255, address(b,'CurrentBankC')>>8,
                0xa9, data_bank|128, 0x8d, 0x16, 0x51, 0x20,
                address(b,'ProtoLegacyDrawShotsCold')&255, address(b,'ProtoLegacyDrawShotsCold')>>8]
    assert list(b['raw'][off:off+13]) == expected and data_bank == 12 and table_bank == 66
    sys.path.insert(0, str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    rows = []
    for typ in [1, 2, 3]:
        for age in [1, 3, 9]:
            q = Arena(b,1)
            q.put(ProtoVariant=0, ScreenLeft_PageLoc=0, ScreenLeft_X_Pos=0,
                  CurrentOAMOffset=0, MmDeathFlag=0)
            for n,v in [('MmBulletType',typ),('MmBulletAge',age),('MmBulletX',139),('MmBulletPage',0),('MmBulletY',194),('MmBulletDir',1)]:q.set(n,v,3)
            q.m.page(1,66);q.set('CurrentBank',194)
            q.m.page(2,88);q.set('CurrentBankC',216)
            q.m.writes=[]
            c=NesMPU(memory=q.m,pc=address(b,'ProtoDrawShots'));c.sp=0xfd;c.p=0x30;c.stPushWord(0x5aff)
            observed=[];at_pointer=address(b,'ProtoLegacyDrawShotsCold::Pointer')+2
            for _ in range(40000):
                if c.pc==0x5b00:break
                if c.pc==at_pointer and q.m.banks[1]==66:
                    frame=(age//2)%cfg['primary']['lengths'][typ-1]
                    rec=cfg['primary']['records'][typ-1][frame][0]
                    ptr=q.get('R0')+256*q.get('R1')
                    actual=[q.m[ptr+i]for i in range(len(rec['bytes']))]
                    assert ptr==rec['address'] and q.m.banks[2]==rec['bank']==12 and actual==rec['bytes']
                    observed.append(dict(pointer=ptr,Cbank=q.m.banks[2],frame=frame,record=rec,
                        bank_writes_before=[dict(address=at,value=v)for at,v in q.m.writes if at in [address(b,'CurrentBankC'),0x5116]]))
                c.step()
            else:raise AssertionError(('Full renderer timeout',hex(c.pc)))
            assert c.sp==0xfd and len(observed)==1
            assert observed[0]['bank_writes_before']==[dict(address=address(b,'CurrentBankC'),value=140),dict(address=0x5116,value=140)]
            snap=observed[0];rec=snap['record'];models=[]
            for name,bank,delta,wrong_data,accept in [('correct',12,0,False,True),('old-table-owner',66,0,False,False),('wrong-pointer',12,1,False,False),('wrong-record-byte',12,0,True,False)]:
                mem={address(b,'SelectedCharacter'):1,address(b,'ProtoVariant'):0,address(b,'CrossoverBehaviorVersion'):1,
                    address(b,'MmSlot'):3,address(b,'MmBulletType')+3:typ,address(b,'MmBulletAge')+3:age,
                    address(b,'MmBulletDir')+3:1,address(b,'R0'):(rec['address']+delta)&255,address(b,'R1'):(rec['address']+delta)>>8}
                h=cfg['hooks']['PrimaryArtReady']
                for i,v in enumerate(h['bytes']):mem[h['address']+i]=v
                rom={rec['bank']*8192+rec['address']%8192+i:v for i,v in enumerate(rec['bytes'])}
                if wrong_data:rom[rec['bank']*8192+rec['address']%8192]^=4
                setup=MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;emu.memType.nesPrgRom=7;MEM='+lua(mem)+';ROM='+lua(rom)+'\n'
                setup+='emu.read=function(a,t)if t==7 then return ROM[a]or 0 end;return MEM[a]or 0 end;emu.write=function(a,v)MEM[a]=v end;emu.convertAddress=function(a)return{address=(a==0xc000 and '+str(bank)+' or 66)*8192+a%8192}end;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end\n'
                test="""
entered=true;phase='use';current={q={name='synthetic-art'},art={}}
emu.addMemoryCallback=function()error('Runtime host registration')end
local h=C.hooks.PrimaryArtReady
state['cpu.pc']=h.address;state['cpu.sp']=236
local ok,e=pcall(function()for _,z in ipairs(callbacks)do if z.kind==2 and z.lo==h.address and z.hi==h.address then z.fn(h.address)end end end)
return ok,tostring(e)
"""
                ok,error=LuaRuntime(unpack_returned_tuples=True).execute(setup+script+'\n'+test)
                assert bool(ok)==accept,(typ,age,name,error)
                models.append(dict(name=name,expected_accept=accept,passed=True,error=None if accept else error))
            rows.append(dict(type=typ,age=age,source_snapshot=snap,full_caller_cycles=c.processorCycles,
                return_SP=c.sp,return_registers=dict(A=c.a,X=c.x,Y=c.y,P=c.p),final_Cbank=q.m.banks[2],
                OAM_write_count=sum(0x200<=at<0x300 for at,_ in q.m.writes),actual_callback_models=models))
    proof=dict(passed=True,native_run=False,ROM_sha256=sha(B/'candidate.nes'),
        real_renderer_caller='ProtoDrawShots variant0 -> ProtoLegacyDrawShotsCold -> MetaspriteRenderLoop',
        pointer_table=dict(symbol='ProtoShotRightLo',bank=table_bank),target_bank=data_bank,
        actual_caller_initial13bytes=expected,full_caller_cases=len(rows),actual_pointer_callback_models=4*len(rows),rows=rows,
        script_sha256=sha(READY/'native/run.lua'),readiness_sha256=sha(READY/'readiness.json'),tool_sha256=sha(__file__),
        limits='Source/CPU full renderer and synthetic actual-observer callback controls only. Initial C88 forces the genuine caller to publish C12. No new native, IRQ injection, six-component outcome or pixel claim. The retained native failure did not log R0/Cbank; actual target ownership here is freshly established by source/assembled execution.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,full_caller_cases=len(rows),callback_models=4*len(rows),target_bank=data_bank,table_bank=table_bank)))


if __name__=='__main__':
    main()
