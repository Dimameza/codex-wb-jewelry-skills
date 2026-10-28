(function () {
  var t = document.body ? document.body.innerText : '';
  var bad = /x5sec|punish|验证码|滑动验证|请登录|captcha/i.test(document.title + ' ' + t.slice(0, 600));
  function sect(key, n) { var i = t.indexOf(key); return i < 0 ? null : t.slice(i, i + (n || 600)); }
  var html = document.documentElement.innerHTML;
  function rx(re) { var m = html.match(re); return m ? m[1] : null; }
  var imgs = Array.prototype.slice.call(document.querySelectorAll('img')).map(function (i) { return i.src || ''; })
    .filter(function (s) { return /cbu01\.alicdn\.com\/img\/ibank/.test(s); }).slice(0, 8);
  return JSON.stringify({
    url: location.href, title: document.title, blocked: bad,
    price_block: sect('价格', 260),
    weights: sect('商品件重尺', 1500),
    material: (t.match(/材质\s*\n?\s*([^\n]{1,30})/) || [])[1] || null,
    sold: (t.match(/已售\s*([^\n]{1,20})/) || [])[1] || null,
    begin_amount: rx(/"beginAmount"\s*:\s*"?(\d+)/),
    sku_price_scale: rx(/"skuPriceScale"\s*:\s*"([^"]{1,200})"/),
    price_ranges: rx(/"priceRange(?:s|List)?"\s*:\s*(\[[^\]]{1,400}\])/),
    badges: (html.match(/O1CN014ntq3r24nkFVzJqfW|O1CN01OBjMFF1f96iPN27qq|O1CN01Ev234b26zJUUSp7eQ/g) || []),
    repeat_rate: (t.match(/回头率\s*([^\n]{1,10})/) || [])[1] || null,
    shop: (html.match(/https?:\/\/([a-z0-9]+)\.1688\.com/) || [])[1] || null,
    colors: sect('颜色', 500),
    images: imgs
  });
})();
