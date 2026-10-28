"""Actual original8x8 draw return-X/cursor closure; no host8x16 substitution."""
from pathlib import Path
import argparse,hashlib,itertools,json
import prepare_rogue_dawn_art_v1 as art
import rogue_dawn_map_v1 as ref
R=Path(__file__).resolve().parents[1]

def draw(raw,frame,face,offset,action=1,slot=0,m=None):
    if m is None:m=art.Memory(ref.cpu_image(raw,lower_bank=2))
    m[0x4b]=slot;m[0x55]=int(slot==0);m[0x300+slot]=action;m[0x303+slot]=frame
    m[0x30d+slot]=128;m[0x30e+slot]=128;m[0x49]=2;m[0x6b]=face*16;m[0x5b]=offset
    c=art.call(m,0xde4a if slot==0 else 0xde47,a=1 if slot else 0,x=slot)
    return m,c

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=R/'build/rogue-dawn-control-v1/draw-return.json');a=p.parse_args()
    raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
    # Actual original game resets its cursor, renders ENEMIES then three
    # projectile owners, and only then invokes the complete player action.
    order=raw[16+62*8192+0xb29:16+62*8192+0xb36]
    assert order==bytes.fromhex('a200865b2045f320bfd4200dcc')
    admitted_frames=sorted(art.BODY)+[247]
    counts={};rows=[];states=0
    for action,frame,face,offset in itertools.product([0,1,2,3,4,6,7],admitted_frames,[0,1],[0,4,128,236,252]):
        m,c=draw(raw,frame,face,offset,action)
        step=(m[0x5b]-offset)&255
        if frame==247:assert c.x==0 and m[0x5b]==offset
        else:assert c.x==m[0x5b] and step%4==0
        key=(frame,face)
        if key in counts:assert counts[key]==step,(action,frame,face,offset,counts[key],step)
        else:counts[key]=step
        states+=1
        if action==1:rows.append([frame,face,offset,c.x,m[0x5b],c.a,c.y,c.p])
    sequences=[]
    for prior_frames in [[],[40],[37,40],[40,38,39]]:
        m=None;cursor=0;steps=[]
        for i,f in enumerate(prior_frames):
            m,c=draw(raw,f,0,cursor,1,0xd0+16*i,m);steps.append([f,cursor,m[0x5b],c.x]);cursor=m[0x5b]
        m,c=draw(raw,8,0,cursor,3,0,m)
        assert c.x==(cursor+counts[8,0])&255
        byte=raw[16+62*8192+0xcc0+c.x]
        sequences.append(dict(actual_native_draws_before_body=steps,body_frame=8,body_input_cursor=cursor,body_return_X=c.x,source_morph_read=f'CCC0+{c.x:02X}',source_byte=byte))
    proof=dict(passed=True,native_run=False,source_ROM=ref.binding(ref.ROM),states=states,
      actual_main_call_order=dict(bank=62,PC='CB29',bytes=order.hex(),order=['cursor=0','F345 enemy owners','D4BF three projectile owners','CC0D player control']),
      admitted_actions=[0,1,2,3,4,6,7],frames=admitted_frames,facing=[0,1],input_cursor=[0,4,128,236,252],
      rows_layout=['frame','face','input5B','returnX','output5B','returnA','returnY','returnP'],rows=rows,
      native_player_cursor_steps=[dict(frame=f,face=face,bytes=n)for(f,face),n in counts.items()],ordered_actual_decoder_sequences=sequences,
      conclusions=['For non-F7 default body frames, returnX equals native original8x8 output cursor; the incoming allocator cursor contributes.','F7 performs no body emission, leaves cursor unchanged, but returnsX0.','World/enemy/projectile ordering is authenticated by actual main bytes; sequences execute actual draw instructions, not complete room AI.','The host8x16 output cursor is not this original8x8 semantic output. ROOT adapter must derive the original-format cursor from genuine prior draw context or declare a deliberate adaptation. It cannot use an arbitrary/hardcoded seed.'],
      limitations=['Finite actual-ROM CPU draw contexts; no original/native gameplay route, PPU, hardware eight-sprite, whole-room or host timing claim.','Testing every admitted action/frame combination is decoder closure, not a claim every such combination is reachable from controls.'],
      tool=ref.binding(__file__))
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,states=states,table_rows=len(rows),sequences=len(sequences))))
if __name__=='__main__':main()
