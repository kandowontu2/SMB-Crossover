Luigi dry movement641: PRIVATE / UNADOPTED source and two-mode item checkpoint

Candidate641460e2646806c03fb98cf84f8a8c2e8de99c74dac8c5876c50f05ef1eb512c.
Parent/production731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c.
Four exact source files and implementation.patch are ready for independent review.
Luigi uses current Mario's mode-specific dry movement, plus51/256 upward launch
speed and one-eighth less ground braking. Real Luigi identity/art/items remain.
Foreign paths have114 complete-call ZERO-cycle differences; OWNED movement cost
is not yet characterized here. No palette change or new RAM. Some legacy handoffs
leave new genuine live farcall operands: exact differences are disclosed, not
masked as byte identity. Water/climb/spring/control handoffs are not retuned.

Source/trait/full-wrapper/428IRQ controls and exact canonical/flagoff builds pass.
ROOT independently reproduced641/d444/f4ffd. Original source report is historical
NATIVE UNRUN; fresh result report adds exactly two zero-retry component launches.
Easy0: pickups867/1494,60+60 growth,13Rg3 source requests, liveKoopa contact1911,
all-ten-slotempty1912..1958,0deaths. Hard1: pickups959/1579,60+60 growth,15requests,
liveGoomba contacts2058/2077 (second already in flight during neutral), empty2078..
2105,0deaths. Both finalFire2; committedCHR0bad; motion maximumworld/camera3.
These are actual numeric modes, genuine physical items and real enemy contacts.

Six sheets show42 inspected complete PPU placements. No obvious corrupt scenery,
block displacement, body or HUD seen in those samples. Not every-frame, source-art,
audible waveform, fullE008 transfer/enable timing, ownedcadence, full1-1 or adoption
qualification. Fresh fullroute/ordinary stomp and exactinput replay remain required.

Review-files.json binds each copied file to its original path/hash/role. Native
captures/settings/ROM/audio stay external. Retained assembler/mock/host/checker
failures remain separate and are not relabeled game failures or native retries.
This checkpoint installs nothing, launches nothing and stages/commits nothing.
