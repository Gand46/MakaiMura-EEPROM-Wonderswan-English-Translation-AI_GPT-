local f=0;local wr=emu.memType.wsWorkRam;local ep=emu.memType.wsCartEeprom
local out=assert(os.getenv('OUT'))
local function dump(file, mt,addr,len) local p=assert(io.open(out..file,'wb'));for i=0,len-1 do p:write(string.char(emu.read(addr+i,mt))) end;p:close() end
emu.resetAccessCounters()
emu.addEventCallback(function()
 f=f+1
 if f==20 then
  dump('mirror_645.bin',wr,0x370,645);dump('eeprom.bin',ep,0,2048)
  local n=0;for _,v in pairs(emu.getAccessCounters(ep,emu.counterType.writeCount)) do n=n+v end
  local diff=0;for i=0,644 do if emu.read(i+0x370,wr)~=emu.read(i,ep) then diff=diff+1 end end
  local q=assert(io.open(out..'result.tsv','w'));q:write('writes='..n..'\tdiff='..diff..'\n');q:close()
  local ok=n==0 and (os.getenv('FRESH')=='1' or diff==0)
  emu.stop(ok and 0 or 2)
 end
end,emu.eventType.endFrame)
emu.addEventCallback(function() emu.setInput({a=false,b=false,start=false,up=false,down=false,left=false,right=false,up2=false,down2=false,left2=false,right2=false,sound=false},0) end,emu.eventType.inputPolled)
