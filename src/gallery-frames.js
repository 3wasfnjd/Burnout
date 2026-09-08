import * as THREE from 'three';

const PHOTOS=[
 './assets/gallery/photo01.jpg','./assets/gallery/photo02.jpg','./assets/gallery/photo03.jpg','./assets/gallery/photo04.jpg','./assets/gallery/photo05.jpg',
 './assets/gallery/photo06.jpg','./assets/gallery/photo07.jpg','./assets/gallery/photo08.jpg','./assets/gallery/photo09.jpg','./assets/gallery/photo10.jpg'
];

const loader=new THREE.TextureLoader();
const texCache=new Map();
function getTexture(url){
  if(texCache.has(url)) return texCache.get(url);
  const t=loader.load(url);
  t.colorSpace=THREE.SRGBColorSpace;
  t.anisotropy=4;
  texCache.set(url,t);
  return t;
}

function framedPhoto(root,url,x,y,z,scale=1){
  const g=new THREE.Group();
  const w=.92*scale,h=1.12*scale,frame=.105*scale;
  const wood=new THREE.MeshStandardMaterial({color:0x6b4327,roughness:.72,metalness:.03});
  const inner=new THREE.MeshStandardMaterial({color:0x241811,roughness:.9});
  const back=new THREE.Mesh(new THREE.BoxGeometry(w+frame*2,h+frame*2,.12*scale),wood);
  back.castShadow=true;back.receiveShadow=true;g.add(back);
  const recess=new THREE.Mesh(new THREE.BoxGeometry(w+.035*scale,h+.035*scale,.028*scale),inner);
  recess.position.z=.072*scale;g.add(recess);
  const photo=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:getTexture(url),toneMapped:false}));
  photo.position.z=.09*scale;g.add(photo);
  g.position.set(x,y,z);
  root.add(g);
  return g;
}

function seeded(room,n){
  let x=(room+1)*0x9e3779b1+n*0x85ebca6b;
  x^=x>>>16;x=Math.imul(x,0x7feb352d);x^=x>>>15;x=Math.imul(x,0x846ca68b);x^=x>>>16;
  return (x>>>0)/4294967296;
}

export function addRandomGallery(root,roomIndex){
  if(!root)return;
  const count=roomIndex===0||roomIndex===4||roomIndex===9?2:1;
  const slots=[-5.6,-4.0,-2.25,-.45,1.35,2.9];
  const used=new Set();
  for(let j=0;j<count;j++){
    let p=Math.floor(seeded(roomIndex,j+3)*PHOTOS.length);
    while(used.has(p))p=(p+1)%PHOTOS.length;
    used.add(p);
    const s=slots[Math.floor(seeded(roomIndex,j+20)*slots.length)];
    const y=2.15+seeded(roomIndex,j+40)*.75;
    const sc=.86+seeded(roomIndex,j+60)*.18;
    framedPhoto(root,PHOTOS[p],s,y,-3.02,sc);
  }
}
