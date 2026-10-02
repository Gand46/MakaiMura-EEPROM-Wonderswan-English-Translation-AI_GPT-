local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local records={}
local function w(a)return emu.read(a,mt)+256*emu.read(a+1,mt)end
local function frame()
 local f=emu.getState().frameCount
 if f==180 then emu.write(0x1e33,0x33,mt);emu.write(0x1e34,1,mt)end
 if f>=200 and f<=400 and f%20==0 then
  local p=assert(io.open(string.format('%s.%04d.png',dest,f),'wb'));p:write(emu.takeScreenshot());p:close()
  records[#records+1]=string.format('{"f":%d,"state":%d}',f,w(0x1e33))
 end
 if f==400 then
  local p=assert(io.open(dest,'wb'));p:write(emu.takeScreenshot());p:close()
  local r=assert(io.open(report,'w'));r:write('{"method":"SYNTHETIC_STATE","target":307,"observations":['..table.concat(records,',')..']}');r:close();emu.stop(0)
 end
end
emu.addEventCallback(frame,emu.eventType.endFrame)
