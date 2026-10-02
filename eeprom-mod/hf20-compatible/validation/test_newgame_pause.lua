local finished=false
local stop=emu.stop
local function finish(code) if not finished then finished=true;stop(code) end end
local frame=0
local found=false
local base=assert(os.getenv('OUT'))
local function shot(name) local p=assert(io.open(base..name..'.png','wb'));p:write(emu.takeScreenshot());p:close() end
local out=assert(io.open(base..'fresh_newgame_pause.tsv','w'))
emu.addEventCallback(function()
  if finished then return end
 frame=frame+1
 local ps=emu.read(0x1E92,emu.memType.wsWorkRam)
 if not found and frame>1000 and ps==2 then
   found=true
   out:write(string.format('frame=%d\tpause=%d\tstate=%04X\n',frame,ps,emu.read16(0x1E33,emu.memType.wsWorkRam)));out:close();shot('fresh_newgame_pause');finish(0)
 end
 if frame>5000 then out:write('FAIL timeout\n');out:close();shot('fresh_newgame_timeout');finish(2) end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
  if finished then return end
 local start,a,b,right,left=false,false,false,false,false
 local cyc=frame%1200
 start=(frame>=120 and frame<140) or (cyc>=20 and cyc<30)
 a=(frame>=190 and frame<210) or (cyc>=180 and cyc<200) or (cyc>=980 and cyc<995)
 b=(cyc>=1030 and cyc<1040)
 right=(cyc>=250 and cyc<900)
 left=(cyc>=910 and cyc<940)
 emu.setInput({start=start,a=a,b=b,right=right,left=left,up=false,down=false,sound=false,up2=false,down2=false,left2=false,right2=false},0)
end,emu.eventType.inputPolled)
