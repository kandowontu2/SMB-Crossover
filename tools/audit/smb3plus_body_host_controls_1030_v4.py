"""Separate current non-shoe body coverage from unsupported Kuribo records.

The existing host explicitly disables Kuribo before this change. Retain all
source-frame failures in the report; this is not full-form qualification.
"""
from pathlib import Path
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import benj_current_menu_controls_1030_v1 as M
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

P=R/'build/peach-palette-fix-1030-v1/joint'
O=R/'build/smb3plus-body-host-1030-v3';J=O/'joint'
A=R/'build/smb3plus-original-characters-1030-v1'


def seed(bundle,variant,form,frame,face):
    q=M.T.make(bundle,17)
    q.put(M3Marker=0xb3,M3Ready=0xb3,M3Variant=variant,M3Form=form,M3RenderForm=form,M3Growth=0,M3Poof=0,
        MmDeathFlag=0,OperMode=1,VRAM_Buffer1_Offset=0,M3PaletteValid=0,PlayerFacingDir=face)
    q.set('M3Native::Player_Frame',frame)
    q.set('M3Native::Player_FlipBits',64 if face==1 else 0)
    return q


def pixels(parts,chr_bytes,page,origin=(0,0),native=False):
    result={}
    for part in parts:
        if native:
            y,tile,attr,x=part
            if y>=240:continue
            x-=origin[0];y-=origin[1]
        else:
            tile,attr,y,x=part
            x=x-256 if x>=128 else x
            y=y-256 if y>=128 else y
        for yy in range(16):
            ty=15-yy if attr&128 else yy
            base=page*1024+(tile&62)*16+(ty//8)*16+ty%8
            lo,hi=chr_bytes[base],chr_bytes[base+8]
            for xx in range(8):
                bit=xx if attr&64 else 7-xx
                value=(lo>>bit&1)|((hi>>bit&1)<<1)
                if value:result.setdefault((x+xx,y+yy),value)
    return result


def main():
    assert not(O/'body-controls-v4.json').exists()
    assert 'Kuribo shoe frames18/43/44 are deliberately unavailable' in B.read(P/'src/smb3_mario_art.inc')
    assert ' sta M3Native::Player_Kuribo' in B.read(P/'src/smb3_mario_motion.s')
    assert 'PF_KURIBO_BIG=24' in B.read(P/'src/smb3_native_controller.inc')
    assert 'PF_KURIBO_SMALL=67' in B.read(P/'src/smb3_native_controller.inc')
    s=json.loads(B.read(O/'source-stage.json'));B.bound(s)
    old,new=[scoped_load(p/'candidate.nes')for p in [P,J]]
    oldraw,newraw=old['raw'],new['raw']
    # Genuine audio owners are preserved byte-for-byte, not just relabelled.
    for name in ['ROGUE_AUDIO_PAGES_7','ROGUE_AUDIO_UPPER_RAW_0']:
        x=next(g for g in old['segs'].values()if g.get('name')=='"'+name+'"')
        start,size=int(x['ooffs'],0),int(x['size'],0)
        assert oldraw[start:start+size]==newraw[start:start+size],name
    foreign=[]
    for variant,form,frame,flags in itertools.product([0,1],range(7),[0,14,31,57,62,79],[0x30,0x31,0x71,0xf1]):
        outcomes=[]
        for bundle in [old,new]:
            q=seed(bundle,variant,form,frame,1)
            c,tr,path,info=M.T.invoke(q,'M3Graphics',a=91,x=3,y=7,p=flags)
            outcomes.append((M.regs(c),M.T.app(q,tr),q.m.banks[:],c.processorCycles))
        assert outcomes[0][:3]==outcomes[1][:3],('Existing SMB3 body changed',variant,form,frame,flags)
        foreign.append(dict(variant=variant,form=form,frame=frame,flags=flags,
            CPU_delta=outcomes[1][3]-outcomes[0][3]))
    donor_chr=Path('C:/NES/the stash/Super Mario Bros. 3+.nes').read_bytes()[16+524288:]
    target_chr=newraw[16+128*8192:]
    drawings=json.loads(B.read(A/'draw-consumers.json'))
    records={(q['character'],q['form'],q['frame'],q['facing']):q for q in drawings}
    own=[];unsupported=[]
    for variant,form,frame,face in itertools.product([2,3],range(7),range(81),[1,2]):
        q=seed(new,variant,form,frame,face)
        c,tr,path,info=M.T.invoke(q,'M3Graphics')
        page=q.get('SmChrBank')+256*q.get('M3SpritePageHi')
        ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
        size=q.m[ptr];assert 0<size<=24 and size%4==0
        parts=[list(q.m[ptr+1+at:ptr+5+at])for at in range(0,size,4)]
        source=records[variant,form,frame,64 if face==1 else 0]
        raw=bytes.fromhex(source['original_OAM'])
        source_parts=[list(raw[at:at+4])for at in range(0,24,4)]
        expected=pixels(source_parts,donor_chr,source['original_page'],(64,160),True)
        actual=pixels(parts,target_chr,page)
        if actual!=expected:
            failure=dict(variant=variant,form=form,frame=frame,face=face,page=page,
                source_page=source['original_page'],target_pixels=len(actual),source_pixels=len(expected),
                mismatch=list(sorted(set(actual.items())^set(expected.items())))[:16])
            if frame in [0x18,0x19,0x43,0x44]:
                unsupported.append(failure)
                continue
            B.write(O/'body-negative-v4.json',json.dumps(failure,indent=2)+'\n')
            raise AssertionError(failure)
        own.append(dict(variant=variant,form=form,frame=frame,face=face,physical_page=page,opaque_pixels=len(actual)))
    assert len(own)==2156 and len(unsupported)==112
    palettes=json.loads(B.read(A/'palette-consumers.json'));palette_cases=[]
    for variant,form,statue in itertools.product([2,3],range(7),[0,1]):
        q=seed(new,variant,form,14,1)
        q.set('M3Native::Player_Statue',statue)
        M.T.invoke(q,'M3Palette')
        at=address(new,'VRAM_Buffer1');packet=bytes(q.m[at:at+7])
        source_form=7 if form==5 and statue else form
        expected=next(p['visible_colors']for p in palettes if p['character']==variant and p['player']==0 and p['form']==source_form)
        assert packet[:3]==bytes.fromhex('3f1103')and list(packet[3:6])==expected and packet[6]==0
        palette_cases.append(dict(variant=variant,form=form,statue=statue,packet=packet.hex()))
    d=dict(passed=True,CPU_only=True,native=False,menu_unlocked=False,candidate=s['candidate'],
        foreign_pairs=len(foreign),source_pixel_cases=len(own),source_palette_cases=len(palette_cases),
        audio_owners_byte_exact=True,retired_constant_tables=4,retired_bytes=324,
        full_source_form_coverage=False,unsupported_existing_Kuribo_records=unsupported,
        pixel_domain='All81 frames audited; non-shoe body domain compared exactly; existing disabled Kuribo records retained as failures.',
        foreign=foreign,source_pixels=own,palettes=palette_cases,limits=s['limits'],
        bindings={str(p):B.sha(p)for p in [Path(__file__),O/'source-stage.json',A/'source-proof.json',
            A/'draw-consumers.json',A/'palette-consumers.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl']})
    B.write(O/'body-controls-v4.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:v for k,v in d.items()if k not in ['foreign','source_pixels','palettes','bindings','unsupported_existing_Kuribo_records']},indent=2))


if __name__=='__main__':main()
