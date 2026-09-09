from pathlib import Path

# Fix valve visual/logical direction mapping in web and VR,
# then make AR use a Drifting-style place-first/play-after workflow.

# --- Web valve puzzle ---
p = Path('src/puzzles.js')
s = p.read_text()
old = "dirs=r=>[[0,1],[1,2],[2,3],[3,0]][r]"
new = "dirs=r=>[[0,1],[3,0],[2,3],[1,2]][r]"
if old not in s:
    raise SystemExit('web valve direction map not found')
s = s.replace(old, new, 1)
p.write_text(s)

# --- XR / AR ---
p = Path('src/main.js')
s = p.read_text()

# VR valve puzzle uses the same visual rotation convention as web.
old = "dirs=r=>[[0,1],[1,2],[2,3],[3,0]][r]"
new = "dirs=r=>[[0,1],[3,0],[2,3],[1,2]][r]"
if old not in s:
    raise SystemExit('VR valve direction map not found')
s = s.replace(old, new, 1)

# Replace the fixed AR character pose with a mutable local player position.
old = "const arPlayerLocal=new THREE.Vector3(-.3,.12,1.9),arPlayerWorld=new THREE.Vector3(),arPlayerAxis=new THREE.Vector3(0,1,0);function syncArPlayer(){if(xrKind!=='ar'||!root)return;arPlayerWorld.copy(arPlayerLocal).multiplyScalar(arScale).applyAxisAngle(arPlayerAxis,arYaw).add(root.position);player.position.copy(arPlayerWorld);player.scale.setScalar(arScale);player.rotation.y=arYaw;player.visible=arPlaced}"
new = "const arPlayerLocal=new THREE.Vector3(-.3,.12,1.9),arPlayerWorld=new THREE.Vector3(),arPlayerAxis=new THREE.Vector3(0,1,0),arLocalForward=new THREE.Vector3(),arLocalRight=new THREE.Vector3();let arPlayerFacing=0;function syncArPlayer(){if(xrKind!=='ar'||!root)return;arPlayerWorld.copy(arPlayerLocal).multiplyScalar(arScale).applyAxisAngle(arPlayerAxis,arYaw).add(root.position);player.position.copy(arPlayerWorld);player.scale.setScalar(arScale);player.rotation.y=arYaw+arPlayerFacing;player.visible=arPlaced}function resetArPlayer(){arPlayerLocal.set(-.3,.12,1.9);arPlayerFacing=0;syncArPlayer()}function moveArPlayer(dx,dz,dt){const nx=THREE.MathUtils.clamp(arPlayerLocal.x+dx,-7,6.8),nz=THREE.MathUtils.clamp(arPlayerLocal.z+dz,-2.55,2.75);let moved=false;if(!hit(nx,arPlayerLocal.z)){arPlayerLocal.x=nx;moved=true}if(!hit(arPlayerLocal.x,nz)){arPlayerLocal.z=nz;moved=true}if(moved){arPlayerFacing=Math.atan2(dx,dz);syncArPlayer();const sp=Math.hypot(dx,dz)/Math.max(dt,.001);if(model&&sp>.05){walkT+=dt*7;walk(sp)}}}"
if old not in s:
    raise SystemExit('AR player helper block not found')
s = s.replace(old, new, 1)

# Drifting-style placement: preview first, explicit confirm, then freeze the shelter.
old = "const arControls=document.createElement('div');arControls.id='arControls';arControls.innerHTML='<button id=arRotL>↺</button><button id=arMinus>−</button><button id=arPlace>تحديد الموقع</button><button id=arPlus>+</button><button id=arRotR>↻</button>';"
new = "const arControls=document.createElement('div');arControls.id='arControls';arControls.innerHTML='<button id=arRotL>↺</button><button id=arMinus>−</button><button id=arPlace>تثبيت الموقع</button><button id=arPlus>+</button><button id=arRotR>↻</button>';"
if old not in s:
    raise SystemExit('AR controls markup not found')
s = s.replace(old, new, 1)

old = "document.getElementById('arMinus').onclick=()=>setArScale(arScale-.05);document.getElementById('arPlus').onclick=()=>setArScale(arScale+.05);document.getElementById('arRotL').onclick=()=>setArYaw(arYaw-Math.PI/12);document.getElementById('arRotR').onclick=()=>setArYaw(arYaw+Math.PI/12);document.getElementById('arPlace').onclick=()=>{arPlaced=false;arReticle.visible=false;if(root)root.visible=false};function setArScale(v){arScale=THREE.MathUtils.clamp(v,.12,.9);if(root&&xrKind==='ar')root.scale.setScalar(arScale);syncArPlayer()}function setArYaw(v){arYaw=v;if(root&&xrKind==='ar')root.rotation.set(0,arYaw,0);syncArPlayer()}"
new = "document.getElementById('arMinus').onclick=()=>{if(!arPlaced)setArScale(arScale-.05)};document.getElementById('arPlus').onclick=()=>{if(!arPlaced)setArScale(arScale+.05)};document.getElementById('arRotL').onclick=()=>{if(!arPlaced)setArYaw(arYaw-Math.PI/12)};document.getElementById('arRotR').onclick=()=>{if(!arPlaced)setArYaw(arYaw+Math.PI/12)};function setArScale(v){arScale=THREE.MathUtils.clamp(v,.12,.9);if(root&&xrKind==='ar')root.scale.setScalar(arScale);syncArPlayer()}function setArYaw(v){arYaw=v;if(root&&xrKind==='ar')root.rotation.set(0,arYaw,0);syncArPlayer()}function confirmArPlacement(){if(xrKind!=='ar'||!arReticle.visible||!root)return false;const pos=new THREE.Vector3(),q=new THREE.Quaternion(),sc=new THREE.Vector3(),camForward=new THREE.Vector3();arReticle.matrix.decompose(pos,q,sc);xrCamera.getWorldDirection(camForward);camForward.y=0;if(camForward.lengthSq()>.0001){camForward.normalize();arYaw=Math.atan2(camForward.x,camForward.z)}root.position.copy(pos);root.rotation.set(0,arYaw,0);root.scale.setScalar(arScale);root.visible=true;arPlaced=true;resetArPlayer();arReticle.visible=false;document.getElementById('arPlace').textContent='إعادة التحديد';return true}function resetArPlacement(){arPlaced=false;player.visible=false;resetArPlayer();if(root)root.visible=false;arReticle.visible=false;document.getElementById('arPlace').textContent='تثبيت الموقع'}document.getElementById('arPlace').onclick=()=>{if(arPlaced)resetArPlacement();else confirmArPlacement()};"
if old not in s:
    raise SystemExit('AR controls behavior block not found')
s = s.replace(old, new, 1)

# Start AR in placement mode with a hidden player; after placement the shelter remains fixed.
old = "if(xrKind==='ar'){scene.background=null;scene.fog=null;arPlaced=false;arControls.style.display='flex';if(root){root.visible=false;root.scale.setScalar(arScale)}"
new = "if(xrKind==='ar'){scene.background=null;scene.fog=null;arPlaced=false;arControls.style.display='flex';document.getElementById('arPlace').textContent='تثبيت الموقع';resetArPlayer();player.visible=false;if(root){root.visible=false;root.scale.setScalar(arScale)}"
if old not in s:
    raise SystemExit('AR sessionstart block not found')
s = s.replace(old, new, 1)

# Controller trigger confirms placement through the same code path as the UI button.
old = "if(xrKind==='ar'){if(arReticle.visible&&root){const pos=new THREE.Vector3(),q=new THREE.Quaternion(),sc=new THREE.Vector3(),camPos=new THREE.Vector3();arReticle.matrix.decompose(pos,q,sc);xrCamera.getWorldPosition(camPos);arYaw=Math.atan2(camPos.x-pos.x,camPos.z-pos.z);root.position.copy(pos);root.rotation.set(0,arYaw,0);root.scale.setScalar(arScale);root.visible=true;arPlaced=true;syncArPlayer()}return}"
new = "if(xrKind==='ar'){if(!arPlaced)confirmArPlacement();return}"
if old not in s:
    raise SystemExit('AR select placement block not found')
s = s.replace(old, new, 1)

# Preserve local character position across AR room rebuilds, but reset it when entering a new room.
old = "if(xrKind==='ar'){root.scale.setScalar(arScale);root.visible=arPlaced;syncArPlayer()}else{root.visible=true;player.scale.setScalar(1);player.position.set(-.3,.12,1.9)}syncUI()"
new = "if(xrKind==='ar'){root.scale.setScalar(arScale);root.visible=arPlaced;resetArPlayer()}else{root.visible=true;player.scale.setScalar(1);player.position.set(-.3,.12,1.9)}syncUI()"
if old not in s:
    raise SystemExit('AR build block not found')
s = s.replace(old, new, 1)

# Before placement: no gameplay movement. After placement: left stick/joystick moves the character,
# relative to the viewer but converted into the shelter's local coordinate system.
old = "if(xrKind==='ar'){const [sx,sy]=stickAxes(right?.gamepad||left?.gamepad);if(Math.abs(sy)>.18)setArScale(arScale-sy*dt*.28);if(arPlaced&&Math.abs(sx)>.18)setArYaw(arYaw+sx*dt*1.35);return}"
new = "if(xrKind==='ar'){if(!arPlaced)return;const [ax0,ay0]=stickAxes(left?.gamepad||right?.gamepad);let ax=Math.abs(ax0)>.14?ax0:0,ay=Math.abs(ay0)>.14?ay0:0;ax=THREE.MathUtils.clamp(ax+jx,-1,1);ay=THREE.MathUtils.clamp(ay+jy,-1,1);if(Math.abs(ax)<.08&&Math.abs(ay)<.08)return;xrCamera.getWorldDirection(arLocalForward);arLocalForward.y=0;if(arLocalForward.lengthSq()<.0001)return;arLocalForward.normalize().applyAxisAngle(arPlayerAxis,-arYaw);arLocalRight.set(arLocalForward.z,0,-arLocalForward.x);const speed=2.35,dx=(arLocalRight.x*ax+arLocalForward.x*-ay)*speed*dt,dz=(arLocalRight.z*ax+arLocalForward.z*-ay)*speed*dt;moveArPlayer(dx,dz,dt);return}"
if old not in s:
    raise SystemExit('AR xrMove block not found')
s = s.replace(old, new, 1)

p.write_text(s)
