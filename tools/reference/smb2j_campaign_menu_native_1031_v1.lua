-- Controller-only private frontend smoke. SMB2J remains deliberately unavailable.
local frame,age,phase,done=0,0,'title',false
local selectStep,updates,shots=0,0,0
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function p(a)return emu.read(a,emu.memType.nesPpuDebug)end
local function bank(pc)local q=emu.convertAddress(pc);return q and q.address//8192 or -1 end
local function change(n)phase=n;age=0 end
local function shot(n)
 shots=shots+1;assert(shots<=4,'Four PNG cap')
 local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local texts={{0x2166,{28,30,25,14,27,36,22,10,27,18,24,36,11,27,24,28,44}},
 {0x21c6,{28,30,25,14,27,36,22,10,27,18,24,36,11,27,24,28,36,2,19}}}
local function menu(choice)
 assert(r('CrossoverMenuState')==10 and r('DisableScreenFlag')==0,'Completed native game-choice screen')
 assert(r('MarioVariant')==6 and r('SelectedCharacter')==0,'Peach alternate survives transition')
 for _,row in ipairs(texts)do for i,tile in ipairs(row[2])do assert(p(row[1]+i-1)==tile,'Actual game-title nametable cells')end end
 assert(p(0x2164)==(choice==0 and 253 or 36)and p(0x21c4)==(choice==1 and 253 or 36),'Actual cursor PPU cells')
end
local function finish()
 if done then return end;done=true
 assert(updates>=60,'Actual controlled SMB1 Main updates after game choice')
 shot('gameplay')
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write('{"passed":true,"source_only":false,"SMB2J_implemented":false,"frames":'..frame..',"main_updates":'..updates..',"PNGs":'..shots..',"RAM_writes":0,"ROM_sha256":"5995749b2efe82343f58899358a663bd050219d3857bbdbc7e01bb38c7e540ba","scope":"Cold controller-only Peach selection, game choices, guarded2J confirm, B return preserving alternate and real SMB1 start"}\n');f:close()
 print('PASS bounded native campaign frontend');emu.stop(0)
end
emu.addMemoryCallback(function()
 if phase=='game'and bank(L.GameLoop)==B.GameLoop and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then updates=updates+1 end
end,emu.callbackType.exec,L.GameLoop)
emu.addEventCallback(function()
 if done then return end;local b={}
 if phase=='open'and age<5 or phase=='confirmCharacter'and age<5 or phase=='reopen'and age<5 or phase=='launch'and age<5 then b.start=true
 elseif phase=='select'and age<5 then b.select=true
 elseif phase=='toggle'and age<5 then b.down=true
 elseif phase=='guard'and age<5 then b.a=true
 elseif phase=='back'and age<5 then b.b=true
 elseif phase=='game'and age>=20 and age<40 then b.right=true
 elseif phase=='game'and age>=45 and age<100 then b.a=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 if phase=='title'and frame==100 then assert(r('OperMode')==0 and r('CrossoverMenuState')==0,'Cold title');change('open')
 elseif phase=='open'and age>=36 then assert(r('CrossoverMenuState')==2,'Actual Start opens roster');change('select')
 elseif phase=='select'and age>=24 then selectStep=selectStep+1;if selectStep==3 then assert(r('MarioVariant')==6,'Actual three Select edges pick Peach');change('confirmCharacter')else age=0 end
 elseif phase=='confirmCharacter'and age>=40 then menu(0);shot('smb1-choice');change('toggle')
 elseif phase=='toggle'and age>=24 then menu(1);shot('smb2j-choice');change('guard')
 elseif phase=='guard'and age>=24 then menu(1);assert(r('OperMode')==0,'Unavailable2J must not start SMB1');change('back')
 elseif phase=='back'and age>=40 then assert(r('CrossoverMenuState')==2 and r('MarioVariant')==6,'B preserves actual alternate');shot('back-to-peach');change('reopen')
 elseif phase=='reopen'and age>=40 then menu(0);change('launch')
 elseif phase=='launch'and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then assert(r('MarioVariant')==6,'SMB1 launched selected alternate');change('game')
 elseif phase=='game'and age>=180 then finish()end
 assert(frame<1500,'Bounded menu smoke')
end,emu.eventType.endFrame)
