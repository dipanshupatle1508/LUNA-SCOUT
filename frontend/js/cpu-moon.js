'use strict';
// General camera ray / sphere rendering used when WebGL is unavailable.
window.createCpuMoon=function(canvas,THREE){
 const ctx=canvas.getContext('2d'),layer=document.createElement('canvas'),lc=layer.getContext('2d');let tex=null,last='',w=0,h=0,lastFrame=0;
 return{setTexture(image){const c=document.createElement('canvas');c.width=image.width;c.height=image.height;const g=c.getContext('2d');g.drawImage(image,0,0);tex={data:g.getImageData(0,0,c.width,c.height).data,w:c.width,h:c.height};last='';},setSize(width,height){const scale=Math.min(1,560/Math.max(width,height));w=Math.max(1,Math.round(width*scale));h=Math.max(1,Math.round(height*scale));canvas.width=layer.width=w;canvas.height=layer.height=h;last='';},render(camera,group,sky){
 const now=performance.now();if(now-lastFrame<65)return;lastFrame=now;const sample=sky?.sample(),light=sample?sample.sun.clone().applyQuaternion(group.quaternion).normalize():new THREE.Vector3(-3,4,5).normalize();
 const key=group.quaternion.toArray().concat(camera.position.toArray(),camera.quaternion.toArray(),light.toArray()).map(n=>n.toFixed(4)).join(',')+(sky?Math.floor(sky.time/60000):'');if(key===last)return;last=key;
 const img=lc.createImageData(w,h),out=img.data,inv=group.quaternion.clone().invert(),tan=Math.tan(camera.fov*Math.PI/360),aspect=camera.aspect,c=camera.position,c2=c.lengthSq(),ray=new THREE.Vector3(),v=new THREE.Vector3();
 for(let y=0;y<h;y++){const ry=(1-2*(y+.5)/h)*tan;for(let x=0;x<w;x++){const rx=(2*(x+.5)/w-1)*tan*aspect;ray.set(rx,ry,-1).normalize().applyQuaternion(camera.quaternion);const b=c.dot(ray),disc=b*b-c2+1;if(disc<0)continue;const t=-b-Math.sqrt(disc);if(t<=0)continue;v.copy(ray).multiplyScalar(t).add(c);const shade=Math.pow(.02+Math.max(0,v.dot(light)),.65)*.73;v.applyQuaternion(inv);const j=(y*w+x)*4;let r=145,g=145,bb=145;if(tex){const u=((Math.atan2(-v.z,v.x)/Math.PI+1)*.5*tex.w)%tex.w,yy=Math.acos(Math.max(-1,Math.min(1,v.y)))/Math.PI*(tex.h-1),i=(Math.floor(yy)*tex.w+Math.floor(u))*4;r=tex.data[i];g=tex.data[i+1];bb=tex.data[i+2];}out[j]=Math.min(255,r*shade);out[j+1]=Math.min(255,g*shade);out[j+2]=Math.min(255,bb*shade);out[j+3]=255;}}
 ctx.clearRect(0,0,w,h);if(sky)sky.drawBackground(ctx,camera,group.quaternion,w,h);lc.putImageData(img,0,0);ctx.drawImage(layer,0,0);
 }};
};
