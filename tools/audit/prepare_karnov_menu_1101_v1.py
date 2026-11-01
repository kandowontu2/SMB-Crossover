"""Use ROM callbacks for Karnov's real cold menu/portrait/name paths."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-host-resource-base-1101-v1'
FM=R/'build/doki-current-component-1101-v1/menu/full_roster_menu.s'
ART=R/'build/hogan-thomas-current/src/full_roster_menu_art.inc'
NR=R/'build/ready76-visible/new_roster_dispatch.s'
IDLE=R/'build/karnov-original-art-1101-v1/art-controls.json'

def once(t,a,b):
    assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)

def prepare(resident,write):
    fm=once(FM.read_text(),' lda #2\n sec\n rts\nNotKarnov:',' lda #2\n clc\n rts\nNotKarnov:')
    fm=once(fm,'farcall HuResolve,jmp','farcall KrMenuResolve,jmp')
    fm=once(fm,'farcall FmStartRetireFlags,jmp','farcall KrStartFlags,jmp')
    write(O/'full_roster_menu.s',fm)
    write(O/'full_roster_menu_art.inc',once(ART.read_text(),'"    *KARNOV     "','"     KARNOV     "'))
    # This real shared gate previously sent raw34 back into twelve-owner
    # legacy palette/inventory code. Only the newly owned ID gains admission.
    nr=once(NR.read_text(),'::GmOnlyHigh:\n cmp #34','::GmOnlyHigh:\n cmp #35')
    write(O/'new_roster_dispatch.s',nr)
    resident=once(resident,' jsr KrCheckCode\n bcc KrDispatchNo',' jsr KrColdResolve\n bcs KrDispatchROM\n jsr KrCheckCode\n bcc KrDispatchNo')
    resident=once(resident,''' lda #2
 sta CurrentBankC
 sta $5116
 tsx
 lda $010a,x''',''' lda #2
 sta CurrentBankC
 sta $5116
 lda #3
KrDispatchROM:
 sta NextBank_SMC+1
 tsx
 lda $010a,x''')
    resident=once(resident,' lda #3\n jsr FarCallCommon\n php\n pha\n txa',' lda NextBank_SMC+1\n jsr FarCallCommon\n php\n pha\n txa')
    body=json.loads(IDLE.read_text());assert body['passed']
    p=next(p for p in body['poses']if p['state']==0 and p['facing']==0 and p['hurt']==0 and p['phase']==0)
    assert p['cells']==5 and p['packed_page']==1
    packet=p['packet'];records=[]
    for i in range(1,len(packet),4):
        tile,attr,y,x=packet[i:i+4];records.append([tile,attr,(y+32)&255,(x+8)&255])
    packed=[packet[0],*(v for record in records[::-1]for v in record)]
    text=(R/'tools/reference/karnov_host_menu_1101_v1.inc').read_text()
    text=once(text,'; GENERATED_IDLE_PACKET','KrColdPose:.byte '+','.join(map(str,packed)))
    write(O/'kr-menu.inc',text)
    resident=once(resident,'KrCookie:.incbin "kr-cookie.bin"','.include "kr-menu.inc"\nKrCookie:.incbin "kr-cookie.bin"')
    return resident,[Path(__file__),R/'tools/reference/karnov_host_menu_1101_v1.inc',FM,ART,NR,IDLE,O/'full_roster_menu.s',O/'full_roster_menu_art.inc',O/'new_roster_dispatch.s',O/'kr-menu.inc']
