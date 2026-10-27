(function () {
  var bad = /x5sec|punish|验证|滑动|captcha|登录/.test(document.title + ' ' + (document.body ? document.body.innerText.slice(0, 400) : ''));
  var items = Array.prototype.slice.call(document.querySelectorAll('li.sm-offer-item'));
  var rows = items.map(function (li) {
    var a = li.querySelector('a[href*="offer/"]');
    var m = a ? a.href.match(/offer\/(\d{10,13})\.html/) : null;
    var q = function (s) { var e = li.querySelector(s); return e ? e.innerText.trim() : null; };
    var img = li.querySelector('img');
    return { offerId: m ? m[1] : null, price: q('.sm-offer-priceNum'), trade: q('.sm-offer-trade'), title: q('.sm-offer-title'),
             company: q('.sm-offer-company'), shop: (function(){var a=li.querySelector('.sm-offer-companyName');return a?a.getAttribute('href').replace(/^\/\//,'').replace(/\/.*$/,''):null;})(), location: q('.sm-offer-location'), img: img ? (img.src || img.getAttribute('data-src')) : null };
  }).filter(function (r) { return r.offerId; });
  return JSON.stringify({ url: location.href, title: document.title, blocked: bad, n: rows.length, rows: rows });
})();
