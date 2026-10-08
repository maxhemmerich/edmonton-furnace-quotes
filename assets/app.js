/* Edmonton Furnace Quotes — form handling.
   No server. The request is composed locally and handed to the visitor's mail app,
   or copied to the clipboard. Nothing is sent until the visitor acts. */

(function () {
  "use strict";

  var TO = "maxhemmerich@gmail.com";
  var form = document.getElementById("qform");
  if (!form) return;

  var err = document.getElementById("err");
  var result = document.getElementById("result");
  var out = document.getElementById("out");
  var mailLink = document.getElementById("mailto");
  var copyBtn = document.getElementById("copy");
  var copyNote = document.getElementById("copyNote");

  function fail(msg, where) {
    err.textContent = msg;
    err.classList.add("on");
    if (where) { where.focus(); }
    return false;
  }

  function clearErr() {
    err.textContent = "";
    err.classList.remove("on");
  }

  function clean(v) { return (v || "").replace(/\s+/g, " ").trim(); }

  // Coverage gate — the same rule contractors.html states ("The postal code is in your coverage area"):
  // Edmonton T5A–T6X plus T7X, T8A, T8B, T8N, T9E. A request from outside these can never be a billable
  // lead, so it is refused at the field with the reason, not accepted and quietly dropped.
  function inCoverage(postal) {
    var fsa = (postal || "").replace(/\s+/g, "").toUpperCase().slice(0, 3);
    if (!/^[A-Z][0-9][A-Z]$/.test(fsa)) return false;
    if (/^T5[A-Z]$/.test(fsa)) return true;
    if (/^T6[A-X]$/.test(fsa)) return true;
    return ["T7X", "T8A", "T8B", "T8N", "T9E"].indexOf(fsa) !== -1;
  }

  function validate(d) {
    if (d.name.length < 2) return fail("Add your name so the contractor knows who they are calling.", document.getElementById("name"));
    var digits = d.phone.replace(/[^0-9]/g, "");
    if (digits.length < 10) return fail("That phone number looks short. Include the area code.", document.getElementById("phone"));
    if (!/^[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d$/.test(d.postal)) return fail("Postal code should look like T5K 1A1.", document.getElementById("postal"));
    if (!inCoverage(d.postal)) return fail("That postal code is outside our coverage area — we cover Edmonton only, T5A–T6X plus T7X, T8A, T8B, T8N, T9E. A request from outside those codes cannot be routed to an Edmonton heating contractor.", document.getElementById("postal"));
    if (!d.job) return fail("Pick what you need done.", document.getElementById("job"));
    if (d.details.length < 10) return fail("Add a line about what the furnace is doing — that is what gets you a real price.", document.getElementById("details"));
    if (!d.consent) return fail("Tick the consent box so we are allowed to pass the request on.", document.getElementById("consent"));
    return true;
  }

  function build(d) {
    var fsa = d.postal.slice(0, 3).toUpperCase();
    var subject = "Furnace quote request — " + fsa + " — " + d.name;
    var lines = [
      "NEW QUOTE REQUEST — Edmonton Furnace Quotes",
      "",
      "Name:        " + d.name,
      "Phone:       " + d.phone,
      "Email:       " + (d.email || "(none given)"),
      "Postal code: " + d.postal.toUpperCase() + "   (area " + fsa + ")",
      "Job:         " + d.job,
      "Timing:      " + d.when,
      "",
      "What the furnace is doing:",
      d.details,
      "",
      "---",
      "Consent: the homeowner ticked the box allowing this request to be passed to",
      "Edmonton heating contractors for the purpose of quoting the work.",
      "Composed: " + new Date().toLocaleString("en-CA", { timeZone: "America/Edmonton" }) + " (Edmonton)",
      "Source:   " + location.href
    ];
    return { subject: subject, body: lines.join("\n") };
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    clearErr();

    var d = {
      name: clean(document.getElementById("name").value),
      phone: clean(document.getElementById("phone").value),
      email: clean(document.getElementById("email").value),
      postal: clean(document.getElementById("postal").value),
      job: document.getElementById("job").value,
      when: document.getElementById("when").value,
      details: document.getElementById("details").value.trim(),
      consent: document.getElementById("consent").checked
    };

    if (!validate(d)) { result.classList.remove("on"); return; }

    var msg = build(d);
    out.value = "To: " + TO + "\nSubject: " + msg.subject + "\n\n" + msg.body;
    mailLink.href = "mailto:" + TO +
      "?subject=" + encodeURIComponent(msg.subject) +
      "&body=" + encodeURIComponent(msg.body);

    result.classList.add("on");
    out.scrollIntoView({ block: "nearest" });
    copyNote.textContent = "";
  });

  copyBtn.addEventListener("click", function () {
    var text = out.value;
    function done() { copyNote.textContent = "Copied. Paste it into an email to " + TO + " and send."; }
    function manual() {
      out.removeAttribute("readonly");
      out.select();
      try { document.execCommand("copy"); done(); } catch (e2) {
        copyNote.textContent = "Select the text above, copy, and email it to " + TO + ".";
      }
      out.setAttribute("readonly", "readonly");
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, manual);
    } else { manual(); }
  });
})();
