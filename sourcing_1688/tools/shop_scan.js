// Сканер витрин 1688 (22.10.2026), на основе discovery/scanner_multi.js (13.09).
// Вставляется в любую открытую витрину (нужен window.lib.mtop). Работает асинхронно в странице:
//   __scan(code, memberId) ставит в очередь; __st() — состояние; __dump(code, minS30) — JSON строк.
// Продажи ↓ (tradenumdown) с ранней остановкой: накопленные продажи последнего товара страницы < STOP_VS;
// затем новинки (timedown) до 4 страниц или до товара старше 60 дней — у новых накопленные продажи малы.
(function () {
  var W = window;
  W.__R = W.__R || {}; W.__Q = W.__Q || [];
  W.__put = function (key, val) { var e = document.getElementById('__o_' + key); if (!e) { e = document.createElement('pre'); e.id = '__o_' + key; e.style.display = 'none'; document.documentElement.appendChild(e); } e.textContent = val; };
  var STOP_VS = 50, PAUSE = 5000;
  var wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  var vs = function (v) { if (v == null) return 0; var m = String(v).match(/([\d.]+)\s*(万)?/); return m ? Math.round(parseFloat(m[1]) * (m[2] ? 10000 : 1)) : 0; };
  W.__req = async function (mem, sortType, pn) {
    var params = { memberId: mem, appdata: { sortType: sortType, sellerRecommendFilter: false, mixFilter: false, tradenumFilter: false, quantityBegin: null, pageNum: pn, count: 30 } };
    for (var t = 0; t < 3; t++) {
      try {
        var res = await W.lib.mtop.request({ api: 'mtop.alibaba.alisite.cbu.server.ModuleAsyncService', v: '1.0',
          data: { componentKey: 'Wp_pc_common_offerlist', params: JSON.stringify(params) }, type: 'POST', dataType: 'jsonp', ecode: 0, timeout: 20000 });
        var ct = res && res.data && res.data.content;
        if (ct && ct.offerList) return ct;
      } catch (e) { W.__lastErr = String(e && (e.ret || e.message || e)).slice(0, 200); }
      await wait(5000);
    }
    return null;
  };
  var take = function (S, L, pn, src) {
    L.forEach(function (o) {
      var id = String(o.id); if (S.rows[id]) return;
      var img = ''; try { var u = JSON.stringify(o.offerImages).match(/ibank\/[^"\\]+?\.(?:jpg|jpeg|png|webp)/i); img = u ? 'https://cbu01.alicdn.com/img/' + u[0] : ''; } catch (e) {}
      S.rows[id] = { id: id, p: parseFloat(o.offerPrice) || 0, s30: o.thirtySaleQuantity || 0, vs: vs(o.vagueSaleQuantity),
        booked: o.bookedCount || 0, created: o.gmtCreate || 0, t: o.subject || '', img: img, page: pn, src: src };
    });
  };
  W.__scanOne = async function (code) {
    var S = W.__R[code]; S.state = 'run'; S.rows = S.rows || {}; S.pages = 0;
    for (var pn = 1; pn <= 133; pn++) {
      var ct = await W.__req(S.mem, 'tradenumdown', pn);
      if (!ct) { S.err = 'trade p' + pn + ' ' + (W.__lastErr || ''); break; }
      S.total = ct.offerCount; var L = ct.offerList || []; take(S, L, pn, 'trade'); S.pages++; S.last = pn;
      if (L.length < 30 || (L.length && vs(L[L.length - 1].vagueSaleQuantity) < STOP_VS)) break;
      await wait(PAUSE + Math.random() * 1200);
    }
    var cutoff = Date.now() - 60 * 864e5;
    for (var pn2 = 1; pn2 <= 4 && !S.err; pn2++) {
      await wait(PAUSE + Math.random() * 1200);
      var c2 = await W.__req(S.mem, 'timedown', pn2);
      if (!c2) break;
      var L2 = c2.offerList || []; take(S, L2, pn2, 'new'); S.pages++;
      if (L2.length < 30 || L2.every(function (o) { return (o.gmtCreate || 0) < cutoff; })) break;
    }
    S.state = S.err ? 'err' : 'done';
  };
  W.__runQ = async function () {
    if (W.__qrun) return; W.__qrun = true;
    while (W.__Q.length) { var c = W.__Q.shift(); try { await W.__scanOne(c); } catch (e) { W.__R[c].state = "fail"; W.__R[c].err = String(e).slice(0, 200); } await wait(20000); }
    W.__qrun = false;
  };
  W.__scan = function (code, mem) { if (!W.__R[code]) { W.__R[code] = { code: code, mem: mem, state: 'queued' }; W.__Q.push(code); } W.__runQ(); return 'queued ' + code; };
  W.__st = function () { return W.__put('st', JSON.stringify(Object.keys(W.__R).map(function (c) { var S = W.__R[c]; return [c, S.state, S.pages || 0, S.total || 0, S.rows ? Object.keys(S.rows).length : 0, S.err || '']; }))); };
  W.__dump = function (code, minS30) {
    var S = W.__R[code]; var rows = Object.keys(S.rows || {}).map(function (k) { return S.rows[k]; })
      .filter(function (r) { return r.s30 >= (minS30 || 0) || r.src === 'new'; });
    W.__put('dump', JSON.stringify({ code: code, mem: S.mem, total: S.total, pages: S.pages, err: S.err || null, rows: rows }));
  };
  W.__put('init', 'shop_scan ok, lib.mtop=' + !!(W.lib && W.lib.mtop));
})();
