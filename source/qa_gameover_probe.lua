local mt=emu.memType.wsWorkRam
local path=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local final=tonumber(os.getenv('QA_END') or '18000')
local continue=tonumber(os.getenv('QA_CONTINUE') or '0')
local out=assert(io.open(report,'w'))
out:write('frame,state,substate\n')
local function input()
 local f=emu.getState().frameCount
 local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if f>=520 and f<524 then inp.down=true end
 if f>=610 and f<614 then inp.a=true end
 if continue==1 and f>=9900 and f<9904 then inp.a=true end
 emu.setInput(inp,0)
end
local function frame()
 local f=emu.getState().frameCount
 if f%600==0 then
  local state=emu.read(0x1e33,mt)+256*emu.read(0x1e34,mt)
  out:write(string.format('%d,%04X,%d\n',f,state,emu.read(0x1e35,mt)))
  local p=string.format('%s.%05d.png',path,f)
  local fh=assert(io.open(p,'wb'));fh:write(emu.takeScreenshot());fh:close()
 end
 if f==final then
  out:close()
  local fh=assert(io.open(path,'wb'));fh:write(emu.takeScreenshot());fh:close()
  emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
