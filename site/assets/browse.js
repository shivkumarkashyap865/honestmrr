
(function(){
  var q=document.getElementById('q'),cat=document.getElementById('cat'),sale=document.getElementById('sale'),sort=document.getElementById('sort'),grid=document.getElementById('grid');
  function apply(){
    var items=Array.prototype.slice.call(grid.children);
    var qs=(q.value||'').toLowerCase(),cs=cat.value||'',ss=sale.value||'';
    items.forEach(function(el){
      var ok=(!qs||el.dataset.name.indexOf(qs)>-1)&&(!cs||el.dataset.cat===cs)&&(!ss||el.dataset.sale===ss);
      el.style.display=ok?'':'none';
    });
    var key=sort.value;
    items.sort(function(a,b){return parseFloat(b.dataset[key])-parseFloat(a.dataset[key]);});
    items.forEach(function(el){grid.appendChild(el);});
  }
  [q,cat,sale,sort].forEach(function(el){el.addEventListener('input',apply);el.addEventListener('change',apply);});
})();
