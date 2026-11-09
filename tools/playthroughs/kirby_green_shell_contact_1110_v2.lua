-- Contact observer used by the unchanged natural green-shell controller.
local probes,contactAttempts={},{}
local function supportAt(a)
 local wx,wy=a.x+8,a.y+24
 local tile=0
 if wy>=32 and wy<240 then
  tile=r('Block_Buffer_1',math.floor(wx/256)%2*208+math.floor((wy-32)/16)*16+math.floor(wx%256/16))
 end
 return {x=wx,y=wy,tile=tile,dy=r('Enemy_Y_Speed',a.slot),force=r('Enemy_Y_MoveForce',a.slot)}
end
local function appendBounded(rows,row)
 if #rows<16 then rows[#rows+1]=row end
end
hook('probe',function()
 if not attack or hit then return end
 local p=shot(r('KbSavedSlot'))
 if p.type~=3 or p.kind~=2 then return end
 appendBounded(probes,{frame=frame,shell=p,intended=actor(shotInput.target.slot)})
end)
hook('contact',function(s)
 if not attack or hit then return end
 local a=actor(s['cpu.x'])
 local born=births[a.slot]
 local p=shot(r('KbSavedSlot'))
 local dx,dy=p.x-a.x,p.y-a.y
 local row={player=player(),target=a,native_goomba=born,shell=p,dx=dx,dy=dy,
            support=supportAt(a),object_offset=r('ObjectOffset'),cpu_a=s['cpu.a'],
            cpu_x=s['cpu.x'],cpu_y=s['cpu.y']}
 row.v1_predicates={id6=a.id==6,state0=a.state==0,flag1=a.flag==1,y_high1=a.y_high==1,
                    y184=a.y==184,expected_birth=not not(born and born.id==6 and born.x>=1750 and born.x<=2100),
                    vx4=p.vx_hi==4,vx_fraction0=p.vx_lo==0,dx_within12=math.abs(dx)<=12,dy_within12=math.abs(dy)<=12}
 appendBounded(contactAttempts,row)
 if p.type~=3 or p.kind~=2 then return end
 local native=a.id==6 and a.state<2 and a.flag>0 and a.flag<128 and a.y_high==1 and
              born and born.id==6 and born.flag==1 and born.y_high==1
 row.target_class=not native and 'wrong-target' or (a.slot==shotInput.target.slot and 'intended-goomba' or 'other-natural-goomba')
 row.qualified=native and p.vx_hi==4 and p.vx_lo==0 and math.abs(dx)<=12 and math.abs(dy)<=12 and
               row.object_offset==a.slot
 contact=row
end)
hook('defeat',function(s)
 if not contact or defeat then return end
 local sp=s['cpu.sp']
 local function stack(i) return emu.read(256+((sp+i)&255),emu.memType.nesDebug) end
 local actual=stack(1)+256*stack(2)+1
 defeat={frame=frame,slot=s['cpu.x'],return_pc=actual,object_offset=r('ObjectOffset')}
 if actual~=C.hooks.consumed.pc or s['cpu.x']~=contact.target.slot or
    defeat.object_offset~=contact.target.slot then failure='unexpected-native-defeat-caller' end
end)
hook('consumed',function()
 if not defeat or hit then return end
 local a=actor(defeat.slot)
 if a.state&0x20==0 or r('KbShotType',contact.shell.slot)~=3 then
  failure='unexpected-native-defeat-return';return
 end
 hit={player=player(),target=a,shell=shot(contact.shell.slot),target_class=contact.target_class,
      genuine_natural_goomba=contact.qualified and a.id==6}
end)
