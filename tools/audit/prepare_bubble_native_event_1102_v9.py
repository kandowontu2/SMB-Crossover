"""Distinct private explicit-stomp-event successor. No candidate ROM output."""
import json
from pathlib import Path
import measure_bubble_native_bounce_gate_1102_v9 as G
P=G.P;R=G.R;O=G.O


def main():
 frozen=json.loads((O/'native-cold-fix-qualified-1102-v8.json').read_text())
 for rel,z in frozen['files'].items():assert P.sha((R/rel).read_bytes())==z['SHA256'],rel
 q=json.loads((O/'native-cold-fix-layout.json').read_text());image=bytearray((O/'native-cold-fix.bin').read_bytes());art=(O/'native-cold-fix-helper.chr').read_bytes()
 actor=q['labels']['BbNativeActor'];event=q['labels']['BbNativeStomp'];ingress=q['labels']['BbNativeIn']+3
 assert image[ingress-0xa000:ingress-0xa000+3]==bytes([32,event&255,event>>8])
 image[ingress-0xa000:ingress-0xa000+3]=bytes([234])*3
 core=P.P.labels(O/'component.lbl');restore=0xd3b2
 source=f'''.setcpu "6502"
.segment "BB_NATIVE_EVENT"
.export BbNativeStomp,BbNativeStompEnd
BbNativeStomp:
 php
 pha
 txa
 pha
 tya
 pha
 jsr ${actor:04x}
 lda #0
 sta $c003,x
 jsr ${core['BbOriginal_D36B']:04x}
 jmp ${restore:04x}
BbNativeStompEnd:
'''
 labels=P.assemble('native-event-v9',source,f'MEMORY{{P:start=${event:04x},size=20,file=%O;}}SEGMENTS{{BB_NATIVE_EVENT:load=P,type=ro;}}')
 callback=(O/'native-event-v9.bin').read_bytes();assert len(callback)==20
 image[event-0xa000:event-0xa000+20]=callback
 image[27*3:27*3+3]=bytes([76,event&255,event>>8]);q['vectors']['27']=dict(name='BbNativeStomp',target=event)
 assert image[0x100:0x153a]==(O/'native-cold-fix.bin').read_bytes()[0x100:0x153a]
 cookie=bytes([0xa7,39,1])+bytes.fromhex(P.sha(image+art))[:13]
 (O/'native-event-v9-image.bin').write_bytes(image);(O/'native-event-v9-BB-cookie.bin').write_bytes(cookie)
 owner=(O/'native-cold-fix-owner.s').read_text().replace('native-cold-fix-BB-cookie.bin','native-event-v9-BB-cookie.bin')
 P.assemble('native-event-v9-owner',owner,'MEMORY{P:start=$ae00,size=$1000,file=%O;}SEGMENTS{COMMON_OWNER_PROPOSAL:load=P,type=ro;}')
 old,new,shared=G.bundles()
 q.update(BB_cookie=cookie.hex(),public_bounce_rows_retain_source_safe_rejection=[31],actual_native_bounce='EnemyStomped -> unchanged fixed MegaManBounceVelocity ->124:A4B0 -> owner39-only A0D6 -> existing124:A179 Y12 -> HuBounceOnly27 -> authenticated private A0E9 -> original D36B once; ordinary NativeIn never infers bounce from speed.',native_event=dict(public_row=27,entry=event,bytes=20,old_inferred_ingress=ingress,removed_inference_bytes=3,inference_replaced_with_NOPS=True,fixed_MegaManBounceVelocity_unchanged=True,callback='Actual native stomp dispatch invokes exactly one original D36B normal restart; no velocity comparison, extra motion step or mutable flag.'),shared_event_proposal=shared,scope='Explicit actual source stomp dispatch only. Private headers/code/helper remain authenticated. Shared10B navigation-tail lease and11B thunk rewrite require exact root successor grant before composition.')
 (O/'native-event-v9-layout.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(passed=True,ROM_written=False,callback_bytes=len(callback),original_source_exact=True,new_mutable_RAM=False,BB_cookie=cookie.hex(),shared_proposal=shared)))


if __name__=='__main__':main()
