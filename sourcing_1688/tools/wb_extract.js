(function () {
  // Карточки выдачи WB с блоком MPSTATS: продажи за 30 дней, остаток, динамика, продвижение
  var num = function (s) { return s == null ? null : parseFloat(String(s).replace(/[\s  ]/g, '').replace(',', '.')); };
  var after = function (t, label) {
    var i = t.indexOf(label); if (i < 0) return null;
    var rest = t.slice(i + label.length).split('\n').map(function (x) { return x.trim(); }).filter(Boolean);
    return rest.length ? rest[0] : null;
  };
  var seen = {}, out = [];
  document.querySelectorAll('article').forEach(function (a) {
    var t = a.innerText || '';
    var nm = after(t, 'Артикул');
    if (!nm || seen[nm]) return;
    seen[nm] = 1;
    var lines = t.split('\n').map(function (x) { return x.trim(); }).filter(Boolean);
    var prices = lines.filter(function (x) { return /^\d[\d\s  ]*₽$/.test(x); }).map(num);
    var slash = lines.indexOf('/');
    var link = a.querySelector('a[href*="/catalog/"]');
    var aria = link && link.getAttribute('aria-label') ? link.getAttribute('aria-label').trim() : null;
    var img = a.querySelector('img');
    var ad = /РЕКЛАМА/.test(t);
    out.push({
      nm: nm, brand: slash > 0 ? lines[slash - 1] : null, name: aria || (slash > 0 ? lines[slash + 1] : null),
      price: prices.length ? prices[0] : null, seller: after(t, 'Продавец'),
      orders30: num(after(t, 'Заказы, шт/30 дн.')), rub30: num(after(t, 'Заказы, ₽/30 дн.')),
      stock: num(after(t, 'Остаток, шт.')), dyn: num(after(t, 'Динамика заказов, %')),
      days_in_stock: num(after(t, 'Был в наличии, дней')), promo: after(t, 'Продвижение'),
      rating_cnt: (t.match(/·\s*([\d\s ]+)\s*оцен/) || [])[1] ? num(t.match(/·\s*([\d\s ]+)\s*оцен/)[1]) : null,
      ad_slot: ad, img: img ? img.src : null, url: link ? link.href.split('?')[0] : null
    });
  });
  return JSON.stringify({ url: location.href, n: out.length, rows: out });
})();
