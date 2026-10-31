"""Complete native-kernel pixels for all legal BT basic poses, both facings."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_native_adapter_controls_v1 as T
from battletoads_small_core_assets_v1 import decode
O=R/'build/battletoads-native-adapter-v9';J=O/'joint'
def render(b):
    pack=json.loads((R/'build/battletoads-small-core-assets-v1/poses.json').read_text())['frames']
    art=(R/'build/battletoads-small-core-assets-v1/art.chr').read_bytes();rows=[]
    for player,variant,face in itertools.product(range(2),range(2),[0,64]):
        m=T.seed(b,player,variant)
        T.put(m,'BtSrc_Objects_Flags',face,player)
        for pose in pack:
            T.put(m,'BtSrc_player1_obj_wanted_frame',pose['frame'],player)
            T.H.put(m,VRAM_Buffer1_Offset=0,CurrentOAMOffset=0,Player_Rel_XPos=120,Player_Rel_YPos=160,
                ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Player_SprAttrib=0)
            T.row(m,26)
            packet=bytes(m[T.address(b,'VRAM_Buffer1'):T.address(b,'VRAM_Buffer1')+13])
            shades=bytes([15,10,26]if variant==0 else[15,23,39])
            assert packet==bytes([63,17,3])+shades+bytes([63,21,3,24,40,32,0])
            T.row(m,1)
            assert T.H.get(m,'CurrentCHRBank')+256*(m[T.address(b,'X5ChrMode')]&3)==915+pose['page']
            # X5SetPhysicalChr is the genuine deferred publisher. Service the
            # actual native publisher; do not expect immediate hardware writes.
            T.H.invoke(m,'X5PublishChr')
            assert m.chr_latches[0]==915+pose['page']
            m[0x5116]=0xa2;T.H.put(m,CurrentBankC=0xa2)
            T.row(m,2)
            count=T.H.get(m,'CurrentOAMOffset');assert count==pose['parts']*4
            assert m.rawtags[2]==0xa2 and T.H.get(m,'CurrentBankC')==0xa2
            assert T.H.get(m,'SmPosePtr')+256*m[T.address(b,'SmPosePtr')+1]==T.address(b,'QwEmpty34')
            oam=bytes(m[0x200:0x200+count]);actual={}
            for i in range(0,count,4):
                y,t,a,x=oam[i:i+4];assert y<240
                at=16+0x100000+m.chr_latches[0]*1024+t*16
                pattern=b['raw'][at:at+32]
                px=decode(pattern,x-128,y+1-181,a&3,bool(a&64))
                for key,v in px.items():
                    if key not in actual:actual[key]=v
            expected={}
            rec=pose['descriptor']
            for i in range(1,len(rec),4):
                t,a,y,x=rec[i:i+4];at=pose['page']*1024+t*16
                expected.update(decode(art[at:at+32],x-256 if x>127 else x,y-256 if y>127 else y,a))
            if face:expected={(-x,y):v for(x,y),v in expected.items()}
            assert actual==expected,('actual kernel original pixels/roles/mirror/anchor',player,variant,face,pose['frame'],len(actual),len(expected),list(set(actual)^set(expected))[:8])
            rows.append(dict(player=player,variant=variant,face=face,pose=pose['frame'],parts=count//4,
                opaque_pixels=len(actual),physical=m.chr_latches[0],source_roles_exact=True))
    return dict(actual_native_kernel_pixel_pairs=len(rows),all12_basic_poses_both_players_variants_faces=True,
        original_source_pixel_role_proof=str(R/'build/battletoads-small-core-assets-v1/controls.json'),
        source_two_role_queue_and_transparent_black_exact=True,real_deferred_CHR_publisher=True,
        original_full_pose_mirror_and_foot_anchor_exact=True,rows=rows,
        scope='Native kernel/OAM+actual published CHR compared to source-verified pack pixels/roles; no native PPU/video or cold-menu claim. P1 retirement remains pending.')
def main():
    T.O=O;T.J=J;T.palettes_render=render
    T.main()
if __name__=='__main__':main()
