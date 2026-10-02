local mt=emu.memType.wsWorkRam
local path=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local stop=tonumber(os.getenv('QA_END') or '2400')
local fh=assert(io.open(report,'w'))
fh:write('frame,event,state,mode,actor16,cs,ip,ax,cx\n')
local function b(a)return emu.read(a,mt) end
local function w(a)return b(a)+256*b(a+1) end
local function actor()
 local t={}
 for a=0x1a08,0x1a17 do t[#t+1]=string.format('%02X',b(a)) end
 return table.concat(t,'')
end
local function log(event)
 local f=emu.getState().frameCount;local s=emu.getState()
 fh:write(string.format('%d,%s,%04X,%04X,%s,%04X,%04X,%04X,%04X\n',f,event,w(0x1e33),w(0x1b74),actor(),s['cpu.cs'] or 0,s['cpu.ip'] or 0,s['cpu.a'] or 0,s['cpu.cx'] or 0))
end
local function input()
 local f=emu.getState().frameCount;local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if f>=520 and f<524 then inp.down=true end
 if f>=610 and f<614 then inp.a=true end
 emu.setInput(inp,0)
end
local function statewrite(addr,val)
 local f=emu.getState().frameCount
 if f>=500 and f<stop then log(string.format('write_%04X_%02X',addr,val)) end
end
local function frame()
 local f=emu.getState().frameCount
 if f%600==0 then log('sample') end
 if f==stop then
  local g=assert(io.open(path,'wb'));g:write(emu.takeScreenshot());g:close()
  fh:close();emu.stop(0)
 end
end
emu.addMemoryCallback(statewrite,emu.callbackType.write,0x1e33,0x1e34,emu.cpuType.ws,mt)
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
