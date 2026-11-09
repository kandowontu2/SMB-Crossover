"""Extend the split-cycle observer with a bounded six-actor entry snapshot."""
from pathlib import Path
import prepare_mini_split_profile_1110 as profile


original_prepare = profile.prepare


def with_actors(output, rom, source, refs, **kwargs):
    old = 'for i=0,5 do context.scene.enemies[i+1]=read(0x10+i) end'
    assert source.count(old) == 1
    replacement = '''context.scene.camera_left=read(0x071f)+256*read(0x071d)
 context.scene.actors={}
 for i=0,5 do
  context.scene.enemies[i+1]=read(0x10+i)
  context.scene.actors[i+1]={slot=i,flag=read(0x10+i),id=read(0x17+i),
   state=read(0x1f+i),x=read(0x76+i)+256*read(0x5d+i),
   y_low=read(0xbe+i),y_high=read(0xa5+i),owner=read(0x73ae+i),
   box_control=read(0x0646+i),contact=read(0x0566+i)}
 end'''
    source = source.replace(old, replacement)
    original_prepare(output, rom, source, {*refs, Path(__file__)}, **kwargs)


if __name__ == '__main__':
    profile.prepare = with_actors
    profile.main()
