    if late.flower and late.flower.left then
      late.swordTrace=late.swordTrace or {}
      if commits%8==0 then
        local t=late.swordTrace
        if #t==16 then table.remove(t,1)end
        t[#t+1]={state=s,kind=read(0x39),flag=read(0x15),itemState=read(0x24),
          itemX=read(0x7b)+256*read(0x62),itemY=read(0xc3),status=read(0x75b),phase=progress}
      end
      if source(0x6ee)>=1 then
        assert(late.flower.spawned and read(0x15)==0,'Authored flower erased before sword inventory')
        late.sword={state=s,inventory=source(0x6ee),status=read(0x75b),flag=read(0x15)}
        finish(true,'Naturally earned mushroom and flower sword');return
      end
      local target=late.flower.left-13
      if progress=='flower-retreat' and idle(s) and floor(s)then
        if s.x<=target then switch('flower-face',1)
        elseif s.facing~=0 then switch('flower-left-face',2)
        else switch('flower-step-left',66)end
      elseif progress=='flower-left-face'then
        if s.facing==0 then pad=0 end
        if age>4 and s.facing==0 and idle(s) and floor(s)then switch('flower-step-left',66)end
      elseif progress=='flower-step-left' and s.action~=0 and s.action~=1 and s.action~=10 then
        switch('flower-step-settle',0)
      elseif progress=='flower-step-settle' and idle(s) and floor(s)then
        switch('flower-retreat',0)
      elseif progress=='flower-face'then
        if s.facing==255 then pad=0 end
        if age>4 and s.facing==255 and idle(s) and floor(s)then
          late.flower.climb=s;switch('flower-climb',8)
        end
      elseif progress=='flower-climb'then
        if s.action==10 then pad=0 end
        if s.y<=114 and(support(s)or s.action==10)then
          late.flower.boarded=s;switch('flower-walk',s.x>1248 and 2 or 1)
        elseif age>=125 then error('Bounded original flower ledge climb')end
      elseif progress=='flower-walk'then
        pad=s.x>1252 and 2 or s.x<1240 and 1 or 0
        assert(age<120,'Bounded native flower overlap')
      end
      assert(age<180,'Bounded original flower collection phase');return
    end
