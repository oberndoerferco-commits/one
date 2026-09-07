(function(){
  /* Oberndörfer Milano: one card per colour. A product with colour swatches gets a second
     card for each further colour, showing that colour's photograph and linking to its variant. */
  function split(card){
    if(card.dataset.obmSplit) return; card.dataset.obmSplit='1';
    var li=card.closest('li'); if(!li) return;
    var inputs=card.querySelectorAll('swatches-variant-picker-component input[type=radio]');
    if(inputs.length<2) return;
    var anchor=li;
    for(var i=1;i<inputs.length;i++){
      var inp=inputs[i], mediaId=inp.getAttribute('data-option-media-id'), variantId=inp.getAttribute('data-variant-id');
      if(!mediaId||!variantId) continue;
      var clone=li.cloneNode(true);
      clone.id=li.id+'-c'+i;
      var c=clone.querySelector('product-card'); if(!c) continue;
      /* cloneNode drops declarative shadow roots; rebuild them from the originals */
      var ol=li.querySelectorAll('overflow-list'), cl=clone.querySelectorAll('overflow-list');
      for(var k=0;k<ol.length&&k<cl.length;k++){ if(ol[k].shadowRoot&&!cl[k].shadowRoot){ try{ cl[k].attachShadow({mode:'open'}).innerHTML=ol[k].shadowRoot.innerHTML; }catch(e){} } }
      c.dataset.obmSplit='1'; c.dataset.obmClone='1'; c.id=c.id+'-c'+i;
      var scroller=clone.querySelector('slideshow-slides');
      var slides=scroller?Array.prototype.slice.call(scroller.querySelectorAll('slideshow-slide')):[];
      var target=null; slides.forEach(function(s){ if(s.getAttribute('slide-id')===mediaId) target=s; });
      if(!target||!scroller) continue;
      /* the colour's own photographs first: the front, then whatever follows it up to the next colour */
      var group=[target], n=target.nextElementSibling;
      while(n && !n.hasAttribute('variant-image')){ group.push(n); n=n.nextElementSibling; }
      slides.forEach(function(s){ if(s.hasAttribute('variant-image')){ s.hidden = group.indexOf(s)<0; } s.setAttribute('aria-hidden','true'); });
      group.slice().reverse().forEach(function(s){ scroller.insertBefore(s, scroller.firstChild); });
      target.hidden=false; target.setAttribute('aria-hidden','false');
      var comp=clone.querySelector('slideshow-component'); if(comp) comp.setAttribute('initial-slide','0');
      var hover=clone.querySelector('.card-gallery__hover-image .product-media');
      var back=group[1]&&group[1].querySelector('.product-media');
      if(hover){ if(back){ hover.replaceWith(back.cloneNode(true)); } else { hover.parentElement.remove(); } }
      /* links go to this colour */
      Array.prototype.forEach.call(clone.querySelectorAll('a[href]'), function(a){
        try{ var u=new URL(a.getAttribute('href'), location.origin); u.searchParams.set('variant', variantId); a.setAttribute('href', u.pathname+u.search); }catch(e){}
      });
      var cin=clone.querySelectorAll('swatches-variant-picker-component input[type=radio]');
      Array.prototype.forEach.call(cin, function(x,k){ x.checked=(k===i); if(k===i) x.setAttribute('checked',''); else x.removeAttribute('checked'); });
      c.removeAttribute('data-no-swatch-selected');
      anchor.insertAdjacentElement('afterend', clone); anchor=clone;
    }
  }
  function run(){ document.querySelectorAll('.product-grid product-card:not([data-obm-split])').forEach(split); }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', run); else run();
  new MutationObserver(function(){ run(); }).observe(document.documentElement,{childList:true,subtree:true});
})();
