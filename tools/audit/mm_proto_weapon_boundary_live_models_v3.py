"""Synthetic live callback controls for the unlaunched six-component profile."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from parodius_visibility_hud_static_startup_v1 import MOCK

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
READY = D/'mm-proto-weapon-boundary-v1/native-ready-v3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--output', type=Path, required=True);p.add_argument('--ready',type=Path,required=True);a = p.parse_args();ready=a.ready
    a.output.mkdir(parents=True, exist_ok=False)
    script = (ready/'native/run.lua').read_text()
    assert sha(ready/'native/run.lua') == json.loads((ready/'readiness.json').read_text())['script_sha256']
    sys.path.insert(0, str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    mock = MOCK+'''
L={};OUTPUT='mock/';MEM={};MAP={}
emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6
emu.read=function(a)return MEM[a]or 0 end;emu.write=function(a,v)MEM[a]=v end
emu.convertAddress=function(a)return{address=(MAP[a]or 0)*8192+a%8192}end
emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end
'''
    pre = '''
entered=true;phase='use';wall=100;updates=20
local function set(n,v,i)MEM[L[n]+(i or 0)]=v end
set('SelectedCharacter',C.identity.owner);set(C.identity.variant_ram,C.identity.variant);set('CrossoverBehaviorVersion',C.mode_value)
set('InvAmmo',20,24)
local function begin(n,kind)
 current={q={kind=kind,name='synthetic',item=0},primarySpawns={},art={},refillCredits=0}
 local h=C.hooks[n]
 for i,v in ipairs(h.bytes)do MEM[h.address+i-1]=v end
 MAP[h.address]=h.physical_bank;state['cpu.pc']=h.address;state['cpu.sp']=240
 MEM[0x1f1]=0xff;MEM[0x1f2]=0x91;MAP[0x9200]=4
 for _,q in ipairs(callbacks)do if q.kind==2 and q.lo==h.address and q.hi==h.address then q.fn(h.address)end end
end
local function finish()
 state['cpu.pc']=0x9200;state['cpu.sp']=242;callbacks[#callbacks].fn(0x9200)
end
emu.addMemoryCallback=function()error('Runtime host callback registration')end
emu.removeMemoryCallback=function()error('Runtime callback removal')end
'''
    cases = [
        ('primary', "state['cpu.a']=1;begin('MegaManWeapons::Spawn','primary');set('MmBulletType',1,3);set('MmBulletDir',1,3);finish();assert(#current.primarySpawns==1)", True),
        ('reject-primary-special-debit', "state['cpu.a']=1;begin('MegaManWeapons::Spawn','primary');set('MmBulletType',1,3);set('MmBulletDir',1,3);set('InvAmmo',19,24);finish()", False),
        ('rush-existing-free-buster', "set('RgShotType',20,9);begin('MegaManRushAttack','rush');set('MmBulletType',1,3);finish();assert(current.existingAttack)", True),
        ('rush-direct-debit', "begin('MegaManRushBounce','rush');set('InvAmmo',8,24);set('MmJumpReleased',1);set('MmRushLandRequest',1);finish();assert(current.bounced==20)", True),
        ('reject-rush-wrong-debit', "begin('MegaManRushBounce','rush');set('InvAmmo',9,24);set('MmJumpReleased',1);set('MmRushLandRequest',1);finish()", False),
        ('balance-choice', "state['cpu.a']=8;set('InvAmmo',4,18);begin('InventoryRefillAmount','balance');set('InvRefill',18);set('InvRefillRemain',8);set('InvRefillTick',3);finish();assert(current.balanceChoice)", True),
        ('reject-balance-wrong-index', "state['cpu.a']=8;set('InvAmmo',4,18);begin('InventoryRefillAmount','balance');set('InvRefill',24);set('InvRefillRemain',8);set('InvRefillTick',3);finish()", False),
        ('balance-credit', "set('InvAmmo',4,18);set('InvRefill',18);set('InvRefillTick',1);set('InvRefillRemain',8);begin('InventoryUiTick','balance');set('InvAmmo',8,18);set('InvRefillRemain',4);set('InvRefillTick',3);finish();assert(current.refillCredits==4)", True),
        ('reject-balance-credit-wrong-owner', "set('InvAmmo',4,18);set('InvRefill',24);set('InvRefillTick',1);set('InvRefillRemain',8);begin('InventoryUiTick','balance');set('InvAmmo',8,18);set('InvRefillRemain',4);set('InvRefillTick',3);finish()", False),
    ]
    rows = []
    for name, test, expected in cases:
        code = mock+'\n'+script+'\n'+pre+'\nlocal ok,e=pcall(function()'+test+' end);return ok,tostring(e)'
        ok, error = LuaRuntime(unpack_returned_tuples=True).execute(code)
        assert bool(ok) == expected, (name, error)
        rows.append(dict(name=name, expected_accept=expected, passed=True, error=None if expected else error))
    proof = dict(passed=True, native_run=False, actual_generated_callback_models=rows,
        script_sha256=sha(ready/'native/run.lua'), readiness_sha256=sha(ready/'readiness.json'),
        tool_sha256=sha(__file__), limits='Synthetic MEM/CPU return inputs exercise actual generated callback bodies and static return dispatcher. Not emulation or native lifecycle/contact/PPU evidence; no native launch.')
    (a.output/'proof.json').write_text(json.dumps(proof, indent=2)+'\n');print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
