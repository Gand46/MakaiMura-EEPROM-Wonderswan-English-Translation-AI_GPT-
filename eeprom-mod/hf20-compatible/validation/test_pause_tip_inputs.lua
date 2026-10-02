local finished=false
local stop=emu.stop
local function finish(code) if not finished then finished=true;stop(code) end end
local base=assert(os.getenv('OUT'))
local frame=0; local paused=false; local age=0; local baseline=0
local function wc()
 local t=emu.getAccessCounters(emu.memType.wsCartEeprom,emu.counterType.writeCount); local n=0
 for i=0,2047 do n=n+(t[i] or 0) end; return n
end
local function log(s) local f=assert(io.open(base..'tip_conflict_test.log','a'));f:write(s..'\n');f:close() end
os.remove(base..'tip_conflict_test.log'); emu.resetAccessCounters()
emu.addEventCallback(function()
  if finished then return end
 frame=frame+1; local ps=emu.read(0x1E92,emu.memType.wsWorkRam)
 if not paused and frame>1500 and ps==2 then paused=true;age=0;baseline=wc();log('pause writes='..baseline) end
 if paused then
  age=age+1
  if age==40 then
    local now=wc(); local hold=emu.read(0x5F8,emu.memType.wsWorkRam)
    if ps~=2 then log('FAIL pause exited');finish(2);return end
    if now~=baseline then log('FAIL EEPROM writes '..now);finish(3);return end
    if hold~=0 then log('FAIL START hold counter changed '..hold);finish(4);return end
    log('PASS all A/B/X/Y-equivalent controls: pause=2 writes=0 holdCounter=0');finish(0)
  end
 end
 if frame>3000 then log('FAIL timeout');finish(5) end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
  if finished then return end
 local start,a,b,right,left,up,down,up2,down2,left2,right2=false,false,false,false,false,false,false,false,false,false,false
 if not paused then
  local cyc=frame%1200
  start=(frame>=120 and frame<140) or (cyc>=20 and cyc<30)
  a=(frame>=190 and frame<210) or (cyc>=180 and cyc<200) or (cyc>=980 and cyc<995)
  b=(cyc>=1030 and cyc<1040);right=(cyc>=250 and cyc<900);left=(cyc>=910 and cyc<940)
 else
  if age>=5 and age<30 then a=true;b=true;right=true;left=true;up=true;down=true;up2=true;down2=true;left2=true;right2=true end
 end
 emu.setInput({start=start,a=a,b=b,right=right,left=left,up=up,down=down,sound=false,up2=up2,down2=down2,left2=left2,right2=right2},0)
end,emu.eventType.inputPolled)
