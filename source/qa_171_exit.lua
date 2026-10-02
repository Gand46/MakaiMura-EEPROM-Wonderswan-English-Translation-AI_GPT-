local mt=emu.memType.wsWorkRam
local path=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local observations={}
local function state()return emu.read(0x1e33,mt)+256*emu.read(0x1e34,mt)end
local function input()
 local f=emu.getState().frameCount
 emu.setInput({a=f>=960 and f<966},0)
end
local function frame()
 local f=emu.getState().frameCount
 if f==180 then emu.write(0x1e33,0x71,mt);emu.write(0x1e34,1,mt) end
 if f==900 or f==1000 or f==1300 then
  local h=assert(io.open(string.format('%s.%d.png',path,f),'wb'));h:write(emu.takeScreenshot());h:close()
  observations[#observations+1]=string.format('{"frame":%d,"state":%d}',f,state())
 end
 if f==1300 then
  local h=assert(io.open(path,'wb'));h:write(emu.takeScreenshot());h:close()
  local r=assert(io.open(report,'w'));r:write('{"method":"SYNTHETIC_STATE","target":369,"input":"A@960-965","observations":['..table.concat(observations,',')..']}');r:close()
  emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
