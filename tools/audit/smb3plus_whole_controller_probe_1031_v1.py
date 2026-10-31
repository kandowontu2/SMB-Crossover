"""Compare complete ordinary donor controller updates, not isolated helpers."""
from pathlib import Path
import itertools
import json
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import smb3plus_kick_host_controls_1031_v1 as K
from discover_smb3plus_chr_routes_1030_v1 import ChrRomBus,DONOR
from benj_mario_donor_trace_1030_v1 import MPU
from link_pit_rygar_sophia_audit_cpu import scoped_load

O=R/'build/smb3plus-whole-controller-probe-1031-v1'
J=R/'build/smb3plus-menu-host-1031-v4/joint'
F=R/'build/smb3-original-source-match-v1/smb3.fns'
N=R/'build/smb3plus-peach-float-donor-native-1031-v1/discovery/capture/ram-float-entry.bin'


def main():
    assert not O.exists();O.mkdir()
    source={m[1]:int(m[2],16) for m in re.finditer(r'^(\w+)\s*=\s*\$([0-9A-Fa-f]+)',F.read_text(),re.M)}
    aliases={m[1]:int(m[2],16) for m in re.finditer(r'^(\w+)=\$([0-9A-Fa-f]+)',
        (J/'src/smb3_native_controller.inc').read_text(),re.M) if 0x5c00<=int(m[2],16)<0x5c64 or m[1]=='Player_Suit'}
    assert set(aliases)<=set(source),(set(aliases)-set(source))
    b=scoped_load(J/'candidate.nes');rows=[]
    for character,form,air,held in itertools.product(range(4),[0,1],[0,1],[0,128]):
        q=K.seed(b,character,form)
        q.m.page(2,91);q.set('CurrentBankC',0xdb)
        for name,value in dict(Player_X=100,Player_XHi=0,Player_Y=176,Player_YHi=1,
            Player_InAir=air,Player_YVel=0,Pad_Holding=held,Pad_Input=held).items():q.set('M3Native::'+name,value)
        bus=ChrRomBus(DONOR.read_bytes());bus.ram[:0x8000]=N.read_bytes()
        bus.select=0x47;bus.reg[6]=0;bus.reg[7]=8;bus.remap()
        for name,at in aliases.items():bus.ram[source[name]]=q.m[at]
        for i in range(8):bus.ram[source['Tile_AttrTable']+i]=q.m[aliases['Tile_AttrTable']+i]
        for at,value in {0x119:character,0x11e:character,0x726:0,0x126:form,
            0x140:0,0x142:0,0x1cc:0,0x720:8}.items():bus.ram[at]=value
        bus.ram[0x7ae4:0x7ae8]=bytes(4)
        cpu=MPU(memory=bus);bus.cpu=cpu;cpu.pc=0xa6bb;cpu.sp=0xfd
        cpu.a=0;cpu.x=1;cpu.y=252;cpu.p=0x22
        bus.ram[0x1fe:0x200]=bytes([255,2]);path=[]
        for count in range(20000):
            if cpu.pc==0x300:break
            bank=bus.banks[(cpu.pc-0x8000)//8192] if cpu.pc>=0x8000 else -1
            path.append((bank,cpu.pc))
            assert bus[cpu.pc]!=0,('Original controller BRK',character,form,air,held,hex(cpu.pc),bank)
            cpu.step()
        else:raise AssertionError(('Bounded controller',character,form,air,held,hex(cpu.pc)))
        K.M.T.invoke(q,'M3Native::Player_Control',a=0,x=1,y=252,p=0x22)
        compare={n:at for n,at in aliases.items() if n.startswith(('Player_','Pad_'))}
        differences=[dict(field=n,source=bus.ram[source[n]],host=q.m[at]) for n,at in compare.items() if bus.ram[source[n]]!=q.m[at]]
        for i,name in enumerate(['MbFloatExpired','MbFloatTimer','MbFloatAnchor','MbFloatReady']):
            if bus.ram[0x7ae4+i]!=q.get(name):differences.append(dict(field=name,source=bus.ram[0x7ae4+i],host=q.get(name)))
        rows.append(dict(character=character,form=form,air=air,held=held,differences=differences,
            original_instructions=count,original_after_jump_calls=path.count((30,0xbac0)),
            source_ready=bus.ram[0x7ae7],source_VY=bus.ram[source['Player_YVel']]))
    d=dict(passed=not any(r['differences'] for r in rows),CPU_only=True,native=False,cases=rows,
        candidate=K.B.sha(J/'candidate.nes'),scope='Complete original8:A6BB vs actual joined native Player_Control, same translated RAM fields. Dry, no slope, no custom ground-pound or stomp delay. Probe only until foreign fixture matches.',
        bindings={str(p):K.B.sha(p) for p in [Path(__file__),J/'candidate.nes',J/'candidate.dbg',F,N,DONOR,J/'src/smb3_native_controller.inc']})
    K.B.write(O/'probe.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=d['passed'],cases=len(rows),first_failures=[r for r in rows if r['differences']][:5])))


if __name__=='__main__':main()
