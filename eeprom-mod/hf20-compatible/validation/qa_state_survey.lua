local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local target=assert(tonumber(os.getenv('QA_STATE')))
local observations={}
local function rw(a)return emu.read(a,mt) end
local function frame()
 local f=emu.getState().frameCount
 if f==180 then
  emu.write(0x1e33,target%256,mt)
  emu.write(0x1e34,math.floor(target/256),mt)
 end
 if f==240 or f==360 or f==600 or f==900 then
  local p=string.format('%s.%04d.png',dest,f)
  local h=assert(io.open(p,'wb'));h:write(emu.takeScreenshot());h:close()
  observations[#observations+1]=string.format('{"frame":%d,"state":%d,"counter":%d}',f,rw(0x1e33)+256*rw(0x1e34),rw(0x1e5a)+256*rw(0x1e5b))
 end
 if f==900 then
  local h=assert(io.open(dest,'wb'));h:write(emu.takeScreenshot());h:close()
  local r=assert(io.open(report,'w'));r:write(string.format('{"target":%d,"method":"SYNTHETIC_STATE","observations":[%s]}',target,table.concat(observations,',')));r:close()
  emu.stop(0)
 end
end
emu.addEventCallback(frame,emu.eventType.endFrame)
