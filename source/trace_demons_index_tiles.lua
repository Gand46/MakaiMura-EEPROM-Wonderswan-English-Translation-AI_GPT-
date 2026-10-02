local function held(f,t) return f>=t and f<t+5 end
local function input()
 local f=emu.getState().frameCount; local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if held(f,520) or held(f,550) then inp.down=true end
 if held(f,610) then inp.a=true end
 if held(f,720) or held(f,900) or held(f,1080) then inp.right=true end
 if held(f,1260) then inp.a=true end
 emu.setInput(inp,0)
end
local rows={}; local seen={}
local function wr(addr,val)
 local f=emu.getState().frameCount
 if f>=1240 and f<=1360 and (addr%16)==0 then
  local s=emu.getState();
  local k=string.format('f=%d pc=%04X:%04X dst=%04X ds:si=%04X:%04X dx=%04X cx=%04X',f,s['cpu.cs']or 0,s['cpu.ip']or 0,addr,s['cpu.ds']or 0,s['cpu.si']or 0,s['cpu.dx']or 0,s['cpu.cx']or 0)
  if not seen[k] then seen[k]=true; table.insert(rows,k) end
 end
end
local done=false
local function frame()
 local f=emu.getState().frameCount
 if f>=1380 and not done then done=true; local h=io.open('/mnt/data/demons_index_tile_sources.txt','w'); for _,r in ipairs(rows) do h:write(r..'\n') end; h:close(); emu.stop(0) end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addMemoryCallback(wr,emu.callbackType.write,0x2000,0x3FFF,emu.cpuType.ws,emu.memType.wsWorkRam)
emu.addEventCallback(frame,emu.eventType.endFrame)
