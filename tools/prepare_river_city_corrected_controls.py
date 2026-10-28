"""Corrected linked River City art and complete melee/grab/throw contracts."""
from pathlib import Path
import argparse,hashlib,json
from prepare_river_city_controls import fresh,pad,scoped_load,address,location
from prepare_river_city_reference import NATIVE,native_pixels,player_setup
from prepare_river_city_assets import POSES,decode
from prepare_river_city_packet_controls import check as packet_check

ROOT=Path(__file__).resolve().parents[1]
EXPECTED='62dd860e9dd6d5414cd6251c5bd0557c5c14b6872aacf81d5e628eb4bab8caff'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert sha(a.rom)==EXPECTED
    b=scoped_load(a.rom);raw=NATIVE.read_bytes();art=[];combat=[]
    assert sha(NATIVE)=='276c1a1a37685717c0d808490100874a949ea79b68bdef0fcaeeab4586a72f62'
    chrbase=16+b['raw'][4]*16384
    linked_chr=b['raw'][chrbase+716*1024:chrbase+724*1024]
    assert linked_chr==(ROOT/'chr/characters/river-city.chr').read_bytes()
    for variant in (0,1):
        native=player_setup(raw,variant)
        assert native[0xcb+variant]==0 and native[0x48+variant]==0x80+variant
        for face in (1,2):
            for index,(name,pose) in enumerate(POSES):
                q=fresh(b,variant);q.put(PlayerFacingDir=face)
                q.invoke('RcSetPose',x=index);q.invoke('RcPublish')
                ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
                size=q.m[ptr];record=bytes(q.m[ptr+1:ptr+size+1]);parts=[record[i:i+4]for i in range(0,size,4)]
                pages=[q.get('CurrentCHRBank',i)+256*(q.get('X5ChrMode',i)&3)for i in range(4)]
                assert pages==list(range(716+4*variant,720+4*variant))
                source,_,cycles=native_pixels(raw,pose,variant,face)
                rebuilt={}
                for tt,aa,yy,xx in reversed(parts):
                    assert tt%2==0 and aa&3 in (0,2)
                    pixels=decode(linked_chr[variant*4096+tt*16:variant*4096+tt*16+32])
                    xx=xx-256 if xx>=128 else xx;yy=yy-256 if yy>=128 else yy
                    for y in range(16):
                        for x in range(8):
                            v=pixels[y][7-x if aa&64 else x]
                            if v:rebuilt[(xx+x,yy+y)]=4 if v==2 and aa&3==2 else v
                assert source==rebuilt,(variant,face,name)
                # Actual foreground palette queue bytes, not preview RGB alone.
                q.put(VRAM_Buffer1_Offset=0);q.invoke('RcColors')
                base=address(b,'VRAM_Buffer1')
                assert bytes(q.m[base:base+13])==bytes.fromhex('3f11030f26303f19030f113000')
                art.append(dict(variant=variant,face=face,pose=pose,name=name,parts=len(parts),
                  opaque_pixels=len(source),native_renderer_cycles=cycles,CHR_pages=pages,
                  maximum_body_rectangle_demand=max(sum((p[2]-256 if p[2]>=128 else p[2])<=y<(p[2]-256 if p[2]>=128 else p[2])+16 for p in parts)for y in range(-32,64))))
        for mode in (0,1):
            for face in (1,2):
                q=fresh(b,variant,mode);q.put(PlayerFacingDir=face,ObjectOffset=5)
                q.set('Enemy_Flag',1);q.set('Enemy_ID',address(b,'Goomba'));q.set('Enemy_State',0)
                q.set('Enemy_Y_HighPos',1);q.set('Enemy_Y_Position',184)
                q.set('Enemy_PageLoc',1);q.set('Enemy_X_Position',112 if face==1 else 80)
                q.set('Enemy_X_Speed',240)
                pad(q,64);q.invoke('RcWeapons')
                for _ in range(5):pad(q,0);q.invoke('RcWeapons')
                assert q.get('Enemy_State')==0 and q.get('RcEnemyHP')==2 and q.get('RcEnemyStun')>0
                for _ in range(10):pad(q,0);q.invoke('RcWeapons')
                pad(q,72);q.invoke('RcWeapons');assert q.get('RcCarrySlot')==0
                c,_=q.invoke('RcEnemyControl',x=0);assert c.p&1 and q.get('Enemy_Y_Position')==160
                pad(q,0);q.invoke('RcWeapons');pad(q,64);c,trace=q.invoke('RcWeapons')
                assert q.get('RcCarrySlot')==255 and q.get('RcThrowSlot')==0 and q.get('RcThrowAge')==48
                assert q.get('Enemy_State')==0x22 and q.get('Enemy_X_Speed')==(48 if face==1 else 208) and q.get('Enemy_Y_Speed')==252
                assert q.get('Enemy_Flag')==1 and q.get('ObjectOffset')==5 and c.sp==0xfd
                native_defeat=address(b,'ShellOrBlockDefeat')
                assert any(r['pc']==native_defeat for r in trace),'genuine defeat entry writes are observed'
                combat.append(dict(variant=variant,mode=mode,face=face,
                  actual_native_defeat=True,thrown_state=34,horizontal_speed=48 if face==1 else -48,
                  private_stun_before_throw=True,original_ObjectOffset_restored=True))
    packet=packet_check(a.rom)
    assert all(all(r[k]for k in ('seven_cells_exact','outside_unchanged','no_write_outside_name','real_return_Y_SP_A'))for r in packet)
    inherited=ROOT/'build/river-city-module/linked-controls-v2-inherited.json'
    base=json.loads(inherited.read_text());assert base['passed']and base['ROM_sha256']==EXPECTED
    assert len(base['rows'])==185 and len(base['interrupts'])==12
    paths=[Path(__file__),a.rom,a.rom.with_suffix('.dbg'),a.rom.with_suffix('.lbl'),NATIVE,
      inherited,ROOT/'build/river-city-module/name-packet-v2.json',ROOT/'build/river-city-module/corrected-assets-v2.json',
      ROOT/'tools/prepare_river_city_controls.py',ROOT/'tools/prepare_river_city_packet_controls.py',
      ROOT/'tools/prepare_river_city_reference.py',ROOT/'tools/prepare_river_city_assets.py']
    paths+=sorted((ROOT/'src').glob('river_city*'))+[ROOT/'chr/characters/river-city.chr',ROOT/'chr/characters/river-city-assets.json']
    proof=dict(passed=True,native_run=False,ROM_sha256=EXPECTED,scope=__doc__,
      inherited=dict(rows=185,actual_RTIs=12),linked_art=art,complete_combat=combat,name_canaries=packet,
      scope_correction='Inherited tool retains its old fixed warning about unqualified palette classes. The actual corrected linked72 maps/palette queue checks here supersede that warning only for this62dd ROM; the93c2 proof remains limited.',
      limits=['Typed source/CPU arenas, not natural input or acquired powers.','Root Nr admission/actor bridge and real gameplay remain unqualified here.','No visible-frame, scanline-crowding, PPU deadline, audio or cadence claim.'],
      bindings=[dict(path=str(f),sha256=sha(f))for f in paths])
    a.output.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,linked_art=len(art),complete_throws=len(combat),name_canaries=len(packet),output=str(a.output))))

if __name__=='__main__':main()
