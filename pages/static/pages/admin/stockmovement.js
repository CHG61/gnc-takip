// pages/static/pages/admin/stockmovement.js
(function() {
  function setReasonChoices() {
    var typeEl = document.getElementById("id_move_type");
    var reasonEl = document.getElementById("id_reason");
    if (!typeEl || !reasonEl) return;

    var moveType = typeEl.value; // "IN" / "OUT" / ""
    var choices = [];

    if (moveType === "IN") {
      choices = [
        ["Satın Alma", "Satın Alma"],
        ["Üretim", "Üretim"],
        ["İade", "İade"],
        ["Düzeltme", "Düzeltme"]
      ];
    } else if (moveType === "OUT") {
      choices = [
        ["Satış", "Satış"],
        ["Kullanım", "Kullanım"],
        ["Hasar", "Hasar"],
        ["Kayıp", "Kayıp"],
        ["Transfer", "Transfer"],
        ["Fire", "Fire"],
        ["Düzeltme", "Düzeltme"]
      ];
    } else {
      choices = [["", "--- Seçiniz ---"]];
    }

    // mevcutları sil
    while (reasonEl.options.length) reasonEl.remove(0);
    // yeni seçenekleri ekle
    choices.forEach(function(ch) {
      var opt = document.createElement("option");
      opt.value = ch[0];
      opt.text  = ch[1];
      reasonEl.add(opt);
    });
  }

  document.addEventListener("DOMContentLoaded", function() {
    setReasonChoices();
    var typeEl = document.getElementById("id_move_type");
    if (typeEl) {
      typeEl.addEventListener("change", setReasonChoices);
    }
  });
})();
