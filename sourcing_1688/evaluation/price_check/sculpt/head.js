(function(){var t=document.body.innerText;var m=t.match(/За 30 дней\s*\n\s*([\d\s  ]+)\n/);var g=t.match(/([\d\s  ]+)\s+товар/);
return JSON.stringify({freq30:m?parseInt(m[1].replace(/\D/g,'')):null,total:g?parseInt(g[1].replace(/\D/g,'')):null});})();
