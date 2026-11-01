"""Trace authentic controller approach to the first Goomba, without captures."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_karnov_combat_integrated_1101_v7 as I
T=I.T


def main():
    crouch='--crouch'in sys.argv
    T.INTEGRATED=True;T.EXPECTED=I.EXPECTED
    b=T.bundle();m,_=T.boot(b);out=[]
    get=lambda n,i=0:m[T.address(b,n)+i]
    damage=0
    for tick in range(370):
        x=get('Player_X_Position')+256*get('Player_PageLoc')
        foes=[dict(slot=i,x=get('Enemy_X_Position',i)+256*get('Enemy_PageLoc',i),y=get('Enemy_Y_Position',i),state=get('Enemy_State',i))for i in range(6)if get('Enemy_Flag',i)and get('Enemy_ID',i)==6]
        near=any(0<e['x']-x<88 and not e['state']&32 for e in foes)
        key=(64 if tick%24<4 else 0)if near else 1
        if near and crouch:key|=4
        T.keys(m,key)
        hits=[]
        def observe(mem,c,i):
            if c.pc==T.address(b,'HandleEnemyFBallCol')and mem.rawtags[0]==254:hits.append(True)
        T.P.call(m,'GameLoop',observer=observe);damage+=len(hits);T.C.consume(m)
        shots=[list(m.ram[2][0x6e+i:0x71+i])for i in range(0,27,3)if m.ram[2][0x6e+i]&128]
        if near and tick%8==0:out.append(dict(tick=tick,input=key,x=x,y=get('Player_Y_Position'),foes=foes,shots=shots,camera=m.ram[2][0x821]+256*m.ram[2][0x822],gear=m.ram[2][0x65],health=m.ram[2][0x68],damage=damage))
    q=dict(ROM_sha256=I.EXPECTED,no_executable_overlay=True,trace=out,native_damage=damage)
    q['crouching']=crouch
    (I.O/('ground-shot-crouch.json'if crouch else'ground-shot-diagnostic.json')).write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
