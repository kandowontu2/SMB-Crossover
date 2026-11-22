-- Read-only observer additions for the retained native item controllers.
-- Native timers/status are separate from private rings/shield/star/drop state.
local acceptedInputMotor=-1
local guestProof={returns=0,finishes={}}
local pickupResources={}
local function samePrivate(a,b)
 return a.rings==b.rings and a.ringLives==b.ringLives and a.hurt==b.hurt
  and a.sourceStar==b.sourceStar and a.drop==b.drop and a.shoes==b.shoes
end
local function collectorResource(before,after)
 assert(samePrivate(before,after),'Native item collector preserves actual private ring/resources')
 local row={before=before,after=after}
 pickupResources[#pickupResources+1]=row
 return row
end
local function guestReturned(p)
 local b,a=p.guestBefore,state()
 if b.guest_active~=1 then return end
 guestProof.returns=guestProof.returns+1
 assert(b.guest_age<60 and a.guest_age==b.guest_age+1,'Actual native transformation age advances once')
 assert(a.sx==b.sx and a.sy==b.sy and a.vx==b.vx and a.vy==b.vy and samePrivate(a,b),
        'Frozen transformation preserves source motion and private resources')
 if a.guest_age==60 then
  assert(a.guest_active==0 and a.engine==8 and a.status==b.guest_target,'Actual sixtieth update applies target tier')
  guestProof.finishes[#guestProof.finishes+1]={before=b,after=a,returned=guestProof.returns}
 else
  assert(a.guest_active==1 and a.engine==9,'Transformation remains hosted before age60')
 end
end
