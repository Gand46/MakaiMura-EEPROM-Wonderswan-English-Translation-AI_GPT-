local path=assert(os.getenv('MESEN_CAPTURE_PATH'))
local out=assert(os.getenv('MESEN_LUA_REPORT'))
local mt=emu.memType.wsWorkRam
local f0=180
local function frame()
 local f=emu.getState().frameCount
 if f==f0 then
  emu.write(0x1e33,0x34,mt)
  emu.write(0x1e34,0,mt)
  emu.write(0x1e8c,3,mt)
 end
 if f==f0+1 or f==f0+90 or f==f0+240 or f==f0+490 or f==900 or f==1200 or f==1600 or f==2000 or (f>=2500 and f<=7000 and f%500==0) then
  local q=string.format('%s.%04d.png',path,f)
  local h=assert(io.open(q,'wb'));h:write(emu.takeScreenshot());h:close()
 end
 if f>=7200 then
  local h=assert(io.open(path,'wb'));h:write(emu.takeScreenshot());h:close()
  local r=assert(io.open(out,'w'));r:write('{"method":"RAM poke state 0034 and mode 03","frame":'..f..',"state":'..emu.read(0x1e8c,mt)..'}');r:close()
  emu.stop(0)
 end
end
emu.addEventCallback(frame,emu.eventType.endFrame)
