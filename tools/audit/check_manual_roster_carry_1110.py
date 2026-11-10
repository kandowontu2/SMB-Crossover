"""Genuine jump boarding of the frozen native WWF/FF manual platforms."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_manual_roster_input_1110 as I
import check_manual_roster_motion_1110 as M

P,N,W,R=I.P,I.N,I.W,I.R
PROOF=I.OUT/'leaf-proof.json'
SHA=lambda p:sha256(Path(p).read_bytes()).hexdigest()


def horizontal(m,owner):
    # Flat legal CPU scene; real native invulnerability isolates carrying from
    # unrelated naturally streamed enemies. No position/velocity/actor writes.
    N.put(m,CheatInvincible=1)
    P.frame(m,0x24)
    [(slot,birth)]=W.D.owned(m,0x28)
    board=None;approach=[]
    for age in range(420):
        row=P.actors(m)[slot]
        px=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
        dx=P.world(row,3,4)+16-(px+8)
        run=0 if owner==29 else 64  # WWF heldB repeats source punches and stops walking.
        held=((1|run) if dx>4 else (2|run) if dx<-4 else 0)
        if age%60<23:held|=128
        P.frame(m,held)
        row=P.actors(m)[slot]
        p=P.fields(m,P.PLAYER_FIELDS)
        flag=N.get(m,'PlatformCollisionFlag',slot)
        if age%20==0:approach.append([age,P.world(row,3,4),row[5],P.world(p),p[2],flag,N.get(m,'GameEngineSubroutine')])
        if flag<128:
            board=age;break
    assert board is not None,(owner,'jump-boarding',approach)
    if owner==29:
        # Genuine source walking actions retire over two neutral updates.
        # A retained last walking step is independent of native platform carry.
        P.frame(m,0);P.frame(m,0)
    samples=[]
    for _ in range(60):
        before=P.actors(m)[slot];px=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
        P.frame(m,0)
        row=P.actors(m)[slot];p=P.fields(m,P.PLAYER_FIELDS)
        flag=N.get(m,'PlatformCollisionFlag',slot)
        delta=P.world(row,3,4)-P.world(before,3,4)
        samples.append([P.world(row,3,4),row[5],P.world(p),p[2],flag,delta,P.world(p)-px])
    carried=[s for s in samples if s[4]<128]
    assert len(carried)>=40,(owner,board,approach,samples)
    assert all(s[1]-s[3]==32 and s[5]==s[6] for s in carried),(owner,board,samples)
    assert max(s[2] for s in carried)-min(s[2] for s in carried)>=4
    return dict(boarding_updates=board,native_carry_samples=len(carried),
        exact_integer_carry=True,top_minus_player_Y=32,
        player_X_range=[min(s[2] for s in carried),max(s[2] for s in carried)],
        platform_X_range=[min(s[0] for s in samples),max(s[0] for s in samples)],
        source_controller=('A23/60 + right/left (WWF noB) center chase,2neutral source-action retirement,60neutral GameCore updates.' if owner==29 else
            'A23/60 + rightB/leftB center chase until support,60neutral actualGameCore updates.'),
        unrelated_contact_isolation='Native CheatInvincible1; no actor/position/velocity writes during controller.',
        first=carried[0],last=carried[-1])


def main():
    cli=argparse.ArgumentParser();cli.add_argument('--owner',type=int,choices=(22,29));a=cli.parse_args()
    q=json.loads(PROOF.read_text())
    for name,digest in q['bindings'].items():assert SHA(R/name)==digest,name
    raw=I.BASE.read_bytes();assert I.SHA(raw)==q['parent_SHA256']==I.PIN
    candidate=P.install(raw,q['patches']);assert I.SHA(candidate)==q['expected_memory_only_SHA256']
    b=I.bundle(candidate,q['labels']);result={};W.D.offset=W.right_offset
    for owner,count in ((22,4),(29,6)):
        if a.owner and owner!=a.owner:continue
        for variant in range(count):
            triangle=W.native_triangle(M.scene(b,owner,variant),q['labels'])
            vertical=W.D.motion(M.scene(b,owner,variant),owner,0x28)
            h=horizontal(M.scene(b,owner,variant),owner)
            result[f'{owner}:{variant}']=dict(triangle=triangle,vertical=vertical,horizontal=h)
            print('Actual jump/carry',owner,variant,vertical,h,flush=True)
    receipt=dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        expected_memory_only_SHA256=q['expected_memory_only_SHA256'],leaf_proof_SHA256=SHA(PROOF),forms=result,
        scope='Real guest GameCore/native jump boarding/60update carrying and337native initial-right112px stroke updates. Cheat contact isolation disclosed. No Mesen/IRQ/full-stage claim.',
        bindings={p.relative_to(R).as_posix():SHA(p) for p in (Path(__file__),Path(M.__file__),PROOF)})
    (I.OUT/('carry'+(f'-{a.owner}' if a.owner else '')+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
