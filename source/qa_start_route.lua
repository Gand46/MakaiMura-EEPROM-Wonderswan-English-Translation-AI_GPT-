local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local marks={180,520,800,1300,1600,1900,2200,2600,3000}
local at={};for _,v in ipairs(marks)do at[v]=true end
local obs={}
local function input()
 local f=emu.getState().frameCount
 local inp={}
 if f>=530 and f<537 then inp.start=true end
 if f>=1450 and f<1457 then inp.start=true end
 if (f>=1710 and f<1715) or (f>=1760 and f<1765) or (f>=1810 and f<1815) then inp.down=true end
 if f>=1900 and f<1907 then inp.a=true end
 if (f>=2310 and f<2315) or (f>=2370 and f<2375) then inp.down=true end
 if f>=2600 and f<2607 then inp.a=true end
 emu.setInput(inp,0)
end
local function frame()
 local f=emu.getState().frameCount
 if at[f] then
  local h=assert(io.open(string.format('%s.%04d.png',dest,f),'wb'));h:write(emu.takeScreenshot());h:close()
  local s=emu.read(0x1e33,mt)+256*emu.read(0x1e34,mt)
  obs[#obs+1]=string.format('{"frame":%d,"state":%d}',f,s)
 end
 if f==3000 then
  local h=assert(io.open(dest,'wb'));h:write(emu.takeScreenshot());h:close()
  local r=assert(io.open(report,'w'));r:write('{"method":"SCRIPTED_NATURAL","inputs":"START@530-536;START@1450-1456;DOWN@1710,1760,1810;A@1900-1906;DOWN@2310,2370;A@2600-2606","observations":['..table.concat(obs,',')..']}');r:close()
  emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
