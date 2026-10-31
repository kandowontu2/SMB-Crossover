"""Probe authentic complete Peach updates at HUD-height/state boundaries."""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/smb3plus_whole_controller_probe_1031_v2.py';text=prior.read_text()
    text=text.replace("O=R/'build/smb3plus-whole-controller-probe-1031-v2'",
        "O=R/'build/smb3plus-whole-controller-edges-1031-v1'")
    text=text.replace("J=R/'build/smb3plus-peach-air-frame-1031-v2/joint'",
        "J=R/'build/smb3plus-peach-complete-controller-1031-v3/joint'")
    text=text.replace('character,form,air,held,vy in itertools.product([2,3],range(7),[0,1],[0,128],[0,5,224,70])',
        'character,form,air,held,vy,ready,expired,fresh,Y in itertools.product([3],range(7),[0,1],[0,128],[0,224],[0,1,2],[0,1],[0,128],[2,176,255])')
    text=text.replace('Player_Y=176,Player_YHi=1','Player_Y=Y,Player_YHi=1')
    text=text.replace('Pad_Holding=held,Pad_Input=held','Pad_Holding=held,Pad_Input=fresh')
    text=text.replace('        bus=ChrRomBus',"        q.put(MbFloatReady=ready,MbFloatExpired=expired,MbFloatAnchor=176)\n        bus=ChrRomBus")
    text=text.replace('bus.ram[0x7ae4:0x7ae8]=bytes(4)',
        "bus.ram[0x7ae4:0x7ae8]=bytes(q.get(n) for n in ['MbFloatExpired','MbFloatTimer','MbFloatAnchor','MbFloatReady'])")
    text=text.replace('input_VY=vy,differences=differences,',
        'input_VY=vy,ready=ready,expired=expired,fresh=fresh,Y=Y,differences=differences,')
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_controller_edges'}
    exec(compile(text,str(prior),'exec'),ns);ns['main']()


if __name__=='__main__':main()
