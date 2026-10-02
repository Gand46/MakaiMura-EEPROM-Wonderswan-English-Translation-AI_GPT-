local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local out=assert(os.getenv('MESEN_LUA_REPORT'))
local samples={}
local last=nil
local pending={}
local function b(a)return emu.read(a,mt) end
local function w(a)return b(a)+256*b(a+1) end
local function frame()
 local f=emu.getState().frameCount
 if f==180 then emu.write(0x1e33,0x34,mt);emu.write(0x1e34,1,mt) end
 local state=w(0x1e33)
 local rem=w(0x1e35)
 local mode=b(0x1e8c)
 if state==0x34 and (mode==4 or mode==5) and rem<=12 and rem~=last then
  last=rem;pending[#pending+1]={at=f+60,remaining=rem,seen=f}
 end
 for i=#pending,1,-1 do
  local x=pending[i]
  if f>=x.at then
   local card=12-x.remaining
   local p=string.format('%s.card%02d.png',dest,card)
   local h=assert(io.open(p,'wb'));h:write(emu.takeScreenshot());h:close()
   samples[#samples+1]={card=card,frame=f,remaining=x.remaining,mode=b(0x1e8c),state=state}
   table.remove(pending,i)
  end
 end
 if f==11000 then
  local h=assert(io.open(dest,'wb'));h:write(emu.takeScreenshot());h:close()
  local r=assert(io.open(out,'w'))
  r:write('{"method":"injected scene initialization 0134","frames":11000,"cards":[')
  for i,x in ipairs(samples) do
   if i>1 then r:write(',') end
   r:write(string.format('{"card":%d,"frame":%d,"remaining":%d,"mode":%d,"state":%d}',x.card,x.frame,x.remaining,x.mode,x.state))
  end
  r:write(']}');r:close();emu.stop(0)
 end
end
emu.addEventCallback(frame,emu.eventType.endFrame)
