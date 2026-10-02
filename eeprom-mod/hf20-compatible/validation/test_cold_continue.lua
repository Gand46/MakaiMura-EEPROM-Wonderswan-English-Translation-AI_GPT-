local f=0;local out=assert(os.getenv('OUT'));local wr=emu.memType.wsWorkRam
local function shot(n)local p=assert(io.open(out..n..'.png','wb'));p:write(emu.takeScreenshot());p:close()end
emu.addEventCallback(function()
 f=f+1
 if f==500 or f==700 or f==1400 or f==1700 then shot('cold'..f)end
 if f==1700 then
  local p=assert(io.open(out..'continue.tsv','w'));p:write(string.format('state=%04X mode=%d pause=%d\n',emu.read16(0x1e33,wr),emu.read16(0x1b74,wr),emu.read(0x1e92,wr)));p:close();emu.stop(emu.read16(0x1e33,wr)==0x80 and emu.read(0x1e92,wr)==2 and 0 or 2)
 end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
 local k={}
 if f<500 then k.start=(f%90)<3 end
 if f>=610 and f<614 then k.a=true end
 if f>=1450 and f<1460 then k.start=true end
 emu.setInput(k,0)
end,emu.eventType.inputPolled)
