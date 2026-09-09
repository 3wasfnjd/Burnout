from pathlib import Path
p=Path('src/bunker17.js')
s=p.read_text()
# Lighting: readable before power, brighter practical lighting after power.
s=s.replace("renderer.toneMappingExposure = 1.18;","renderer.toneMappingExposure = 1.42;")
s=s.replace("const ambient = new THREE.HemisphereLight(0x3d4d55, 0x080808, 0.16);","const ambient = new THREE.HemisphereLight(0x9aabb2, 0x17130f, 0.72);")
s=s.replace("const l = new THREE.PointLight(0xffd6a3, 0, 8, 1.9);","const l = new THREE.PointLight(0xffd6a3, 1.15, 10, 1.7);")
s=s.replace("if(n===0){ emergency.intensity=.8; mainLights.forEach(l=>l.intensity=4.4); }","if(n===0){ emergency.intensity=.45; ambient.intensity=1.05; mainLights.forEach(l=>l.intensity=5.2); }")
# Make loading cache recover after failed request.
s=s.replace("if (!cache.has(url)) cache.set(url, loader.loadAsync(url));","if (!cache.has(url)) cache.set(url, loader.loadAsync(url).catch(e=>{ cache.delete(url); throw e; }));")
start=s.index('function powerPuzzle(){')
end=s.index("\n\nuseBtn?.addEventListener", start)
new=r'''function finishPuzzle(n, message){
  status.textContent=message;
  if(!completed[n]) solve(n);
}

function powerPuzzle(){
  pDesc.textContent='أعد الطاقة عبر شبكة التوزيع. كل زر يدير قطعة سلك 90°. يجب إنشاء مسار متصل من المولد إلى وحدة التحكم.';
  const target=[1,2,0,3,1,0,2,1,3], rot=[0,0,0,0,0,0,0,0,0];
  game.innerHTML='<div class="b17-grid power-grid"></div><div class="b17-meter">GENERATOR ▸ ▢ ▢ ▢ ▸ CONTROL</div>';
  const wrap=game.firstChild;
  rot.forEach((_,i)=>{const b=document.createElement('button');b.className='b17-tile';b.innerHTML='<span>└</span>';b.onclick=()=>{rot[i]=(rot[i]+1)%4;b.querySelector('span').style.transform=`rotate(${rot[i]*90}deg)`;const ok=rot.every((v,j)=>v===target[j]);status.textContent=`استقرار الشبكة ${rot.filter((v,j)=>v===target[j]).length}/9`;if(ok){wrap.classList.add('powered');finishPuzzle(0,'POWER BUS ONLINE — عادت الإضاءة الرئيسية');}};wrap.appendChild(b);});
}

function pressurePuzzle(){
  pDesc.textContent='وازن ضغط خطوط التبريد. تدوير أي صمام يؤثر في أكثر من خط؛ اجعل العدادات الثلاثة داخل المجال الأخضر 45–55 PSI.';
  let v=[0,0,0]; const pressure=()=>[28+v[0]*9+v[2]*4,31+v[1]*8-v[0]*3,26+v[2]*10+v[1]*3];
  game.innerHTML='<div class="b17-gauges"></div><div class="b17-valves"></div>';const gauges=game.firstChild,wrap=game.lastChild;
  const render=()=>{const ps=pressure();gauges.innerHTML=ps.map((x,i)=>`<div class="b17-gauge ${x>=45&&x<=55?'ok':''}"><b>${Math.round(x)}</b><small>PSI ${i+1}</small></div>`).join('');status.textContent=`PRESSURE ${ps.map(x=>Math.round(x)).join(' / ')} PSI`;if(ps.every(x=>x>=45&&x<=55))finishPuzzle(1,'PRESSURE STABLE — خطوط التبريد مستقرة');};
  for(let i=0;i<3;i++){const b=document.createElement('button');b.className='b17-valve';b.innerHTML=`<span class="wheel">✣</span><b>V${i+1}</b>`;b.onclick=()=>{v[i]=(v[i]+1)%4;b.querySelector('.wheel').style.transform=`rotate(${v[i]*90}deg)`;render();};wrap.appendChild(b);}render();
}

function cluePuzzle(){
  pDesc.textContent='استخرج الأدلة بالترتيب المنطقي من سجل الملجأ. الرموز وحدها لا تكفي؛ الرقم الموجود مع كل دليل هو ترتيب الإدخال.';
  const clues=[['كتاب العمليات','△','2'],['خزانة الطوارئ','○','4'],['مذكرة المكتب','III','1'],['لوحة التحذير','✕','3']];let found=new Map();
  game.innerHTML='<div class="b17-clues"></div><div class="b17-evidence">الأدلة المكتشفة: —</div>';const wrap=game.firstChild,out=game.lastChild;
  clues.forEach(([name,sym,n])=>{const b=document.createElement('button');b.className='b17-clue';b.textContent=name;b.onclick=()=>{found.set(n,sym);b.classList.add('found');b.textContent=`${name}  [${n}] ${sym}`;out.textContent='الأدلة: '+[...found.entries()].sort().map(([k,x])=>`${k}:${x}`).join('   ');if(found.size===4)finishPuzzle(2,'تم جمع الأدلة — رتّب الرموز حسب الأرقام 1 ← 4');};wrap.appendChild(b);});
}

function consolePuzzle(){
  pDesc.textContent='أدخل الرموز حسب أرقام الأدلة، وليس حسب مكان العثور عليها.';
  const answer=['III','△','✕','○'], symbols=['△','○','III','✕'];let entry=[];
  game.innerHTML='<div class="b17-symbols"></div><div class="b17-entry">— — — —</div>';const wrap=game.firstChild,out=game.lastChild;
  symbols.forEach(sym=>{const b=document.createElement('button');b.textContent=sym;b.onclick=()=>{if(entry.length<4)entry.push(sym);out.textContent=entry.join('  ');if(entry.length===4){if(entry.every((x,i)=>x===answer[i]))finishPuzzle(3,'SECURITY CORE ACCEPTED — DOOR CODE 7314');else{status.textContent='ACCESS DENIED — أعد قراءة أرقام الأدلة';entry=[];setTimeout(()=>out.textContent='— — — —',450);}}};wrap.appendChild(b);});
}

function doorPuzzle(){
  pDesc.textContent='أدخل رمز الأمان الذي ظهر على وحدة التحكم، ثم فعّل قفل الباب الميكانيكي.';
  let code='';game.innerHTML='<div class="b17-keypad"></div><div class="b17-code">____</div>';const pad=game.firstChild,out=game.lastChild;
  [...'1234567890'].forEach(n=>{const b=document.createElement('button');b.textContent=n;b.onclick=()=>{if(code.length<4)code+=n;out.textContent=code.padEnd(4,'_');if(code.length===4){if(code==='7314'){status.textContent='CODE ACCEPTED — القفل الميكانيكي جاهز';pad.querySelectorAll('button').forEach(x=>x.disabled=true);const open=document.createElement('button');open.className='b17-open';open.textContent='تدوير مقبض الباب';let turns=0;open.onclick=()=>{turns++;open.style.transform=`rotate(${turns*45}deg)`;status.textContent=`تحرير الأقفال ${turns}/4`;if(turns>=4){finishPuzzle(4,'BUNKER 17 OPEN — تم تحرير الباب');modal.classList.remove('show');}};game.appendChild(open);}else{status.textContent='رمز غير صحيح';code='';setTimeout(()=>out.textContent='____',350);}}};pad.appendChild(b);});
}'''
s=s[:start]+new+s[end:]
p.write_text(s)

css=Path('bunker17.css')
c=css.read_text() if css.exists() else ''
c += r'''
/* Bunker 17 interaction upgrade */
.b17-grid{display:grid;grid-template-columns:repeat(3,minmax(68px,1fr));gap:10px;margin:16px 0}.b17-tile{min-height:72px;background:#11191b;border:1px solid #536064;border-radius:8px;color:#e8d7ae;font-size:36px}.b17-tile span{display:inline-block;transition:transform .16s}.b17-grid.powered .b17-tile{box-shadow:0 0 18px rgba(104,255,211,.35);border-color:#68ffd3}.b17-meter,.b17-evidence{padding:12px;border:1px solid #4b5558;background:#0b1011;font-family:monospace}.b17-gauges{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0}.b17-gauge{aspect-ratio:1;border:5px solid #5b2722;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#151718}.b17-gauge.ok{border-color:#47765d;box-shadow:inset 0 0 18px rgba(90,255,160,.18)}.b17-gauge b{font-size:24px}.b17-gauge small{opacity:.7}.b17-open{transition:transform .12s}
'''
css.write_text(c)
