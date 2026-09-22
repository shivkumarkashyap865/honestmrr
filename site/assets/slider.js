
(function(){
  var stage=document.getElementById('s3d');
  if(!stage) return;
  var cards=Array.prototype.slice.call(stage.children);
  var n=cards.length, active=0, timer=null;
  function layout(){
    cards.forEach(function(el,i){
      var off=i-active;
      if(off>n/2) off-=n;
      if(off<-n/2) off+=n;
      var a=Math.abs(off);
      el.style.transform='translateX('+(off*58)+'%) translateZ('+(-a*175)+'px) rotateY('+(-off*34)+'deg)';
      el.style.opacity=a>2?0:1-a*0.22;
      el.style.zIndex=String(100-a);
      el.style.pointerEvents=a>2?'none':'auto';
    });
  }
  function go(d){active=(active+d+n)%n;layout();}
  function restart(){if(timer)clearInterval(timer);timer=setInterval(function(){go(1);},3800);}
  document.getElementById('s3prev').addEventListener('click',function(){go(-1);restart();});
  document.getElementById('s3next').addEventListener('click',function(){go(1);restart();});
  var sx=null;
  stage.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;},{passive:true});
  stage.addEventListener('touchend',function(e){
    if(sx===null)return;
    var dx=e.changedTouches[0].clientX-sx;
    if(Math.abs(dx)>40) go(dx<0?1:-1);
    sx=null;restart();
  },{passive:true});
  stage.addEventListener('mouseenter',function(){if(timer)clearInterval(timer);});
  stage.addEventListener('mouseleave',restart);
  layout();restart();
})();
