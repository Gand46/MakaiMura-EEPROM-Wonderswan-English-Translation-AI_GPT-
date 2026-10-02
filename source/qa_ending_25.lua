local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local out=assert(os.getenv('MESEN_LUA_REPORT'))
local seen={}
local pending={}
local report={}
local function b(a)return emu.read(a,mt) end
local function w(a)return b(a)+256*b(a+1) end
local function frame()
 local f=emu.getState().frameCount
 if f==180 then emu.write(0x1e33,0x34,mt);emu.write(0x1e34,1,mt) end
 local state=w(0x1e33);local mode=b(0x1e8c);local remain=w(0x1e35)
 if state==0x34 and mode==1 and remain<=24 then
  local line=24-remain
  if not seen[line] then
   seen[line]=true
   pending[#pending+1]={line=line,frame=f+30}
  end
 end
 for i=#pending,1,-1 do
  local p=pending[i]
  if f>=p.frame then
   local path=string.format('%s.line%02d.png',dest,p.line)
   local h=assert(io.open(path,'wb'));h:write(emu.takeScreenshot());h:close()
   report[#report+1]={line=p.line,frame=f}
   table.remove(pending,i)
  end
 end
 if f==3300 then
  local h=assert(io.open(dest,'wb'));h:write(emu.takeScreenshot());h:close()
  local r=assert(io.open(out,'w'))
  r:write('{"method":"injected scene initialization 0134","captured_lines":'..#report..',"screens":[')
  for i,v in ipairs(report) do
   if i>1 then r:write(',') end
   r:write(string.format('{"line":%d,"frame":%d}',v.line,v.frame))
  end
  r:write(']}');r:close();emu.stop(0)
 end
end
emu.addEventCallback(frame,emu.eventType.endFrame)
