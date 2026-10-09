/* Edmonton Furnace Quotes — form handling.
   No server. The request is composed locally and handed to the visitor's mail app,
   copied to the clipboard, or saved as a file. Nothing is sent until the visitor acts.

   The form must never submit natively. A native submission whose target is the mailto:
   address is what a browser turns into its full-page "the information you're about to
   submit is not secure" warning, and a native POST to the page URL is a 405 on GitHub
   Pages — both lose the lead. So the "Prepare my request email" control is a
   button[type=button] driven from here, and index.html carries no action/method/enctype
   on the form. With JavaScript off the button is hidden and the noscript block's own
   plain mailto: link (a link, never a form submit) is the path. */

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
  var prepBtn = document.getElementById("prepare");
  var saveBtn = document.getElementById("save");
  var longNote = document.getElementById("longNote");
  var sentNote = document.getElementById("sentNote");
  var btnRow = document.querySelector("#result .btn-row");
  var jobSel = document.getElementById("job");

  // Intent hand-off. A visitor who arrived from one of the single-intent pages has already
  // answered "what do you need?" on that page; pre-select it here so the one decision the page
  // already made is not asked a second time. This removes a step on the highest-intent path the
  // site has, and it makes the request carry the job the visitor actually read about. Only the
  // four unambiguous single-intent pages are mapped: repair-or-replace, the quote checklist, the
  // rebates page and the permit page are deliberately left alone, because their readers have not
  // committed to one job and a guess there would be wrong more often than right. It runs once at
  // load, before any choice, and a value the visitor picks is never overwritten (it bails if the
  // select is already set). Nothing here sends anything; it only changes which option is shown.
  var FROM_PAGE_JOB = {
    "no-heat.html": "No heat \u2014 urgent",
    "furnace-repair.html": "Furnace repair",
    "furnace-replacement.html": "Furnace replacement",
    "furnace-tune-up.html": "Furnace tune-up or inspection"
  };
  (function prefillJobFromReferrer() {
    if (!jobSel || jobSel.value) { return; }
    var ref = "";
    try { ref = document.referrer || ""; } catch (e) { ref = ""; }
    var leaf = ref.split("#")[0].split("?")[0].split("/").pop().toLowerCase();
    var want = FROM_PAGE_JOB[leaf];
    if (!want) { return; }
    for (var i = 0; i < jobSel.options.length; i++) {
      if (jobSel.options[i].value === want) { jobSel.value = want; return; }
    }
  })();

  // Some mail apps and phones refuse a mailto: link much past ~2,000 characters and fail
  // silently: the tap appears to do nothing and the lead is lost with no error anywhere.
  // Measured by hand on this site: a homeowner who writes a paragraph about the furnace
  // composes a link of 2,050-2,236 characters, and a phone with no mail app or a desktop
  // with Outlook will not open one that size. The composed request itself is never
  // shortened. Instead, past this length the panel says so and the two controls that need
  // no mail app at all - Copy and Save - come first, so the visitor is not left tapping a
  // control that cannot work.
  var LONG_LINK = 1800;

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
  //
  // The FSA is also checked against the codes that can actually exist: in a Canadian postal code the third
  // character is never D, F, I, O, Q or U, so T5D, T6D and the like are not real codes and are refused here
  // rather than carried in as a request. This keeps the gate exactly the set service-areas.html lists — every
  // code on that page is accepted, and every code that is not (including one that cannot exist) is refused.
  var NOT_IN_FSA = "DFIOQU";
  function inCoverage(postal) {
    var fsa = (postal || "").replace(/\s+/g, "").toUpperCase().slice(0, 3);
    if (!/^[A-Z][0-9][A-Z]$/.test(fsa)) return false;
    if (NOT_IN_FSA.indexOf(fsa.charAt(2)) !== -1) return false;
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

  // Every path into composing the request lands here. Nothing here submits anything:
  // the composed text is placed in the page and offered to the visitor.
  function submitRequest() {
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
    var href = "mailto:" + TO +
      "?subject=" + encodeURIComponent(msg.subject) +
      "&body=" + encodeURIComponent(msg.body);
    mailLink.href = href;

    // The request the contractor receives is never trimmed to fit a link. The link is what
    // has to give: past LONG_LINK the mail-app handoff is the unreliable path, so say so and
    // put Copy and Save first - by moving the control in the DOM, not by CSS order, so that
    // what a screen reader and the Tab key walk is the same order the page shows.
    var tooLong = href.length > LONG_LINK;
    result.classList.toggle("long", tooLong);
    if (sentNote) { sentNote.hidden = tooLong; }
    if (longNote) {
      longNote.hidden = !tooLong;
      // The one sentence the visitor has to act on: the control names are in bold so the
      // two that work are unmistakable. Only the measured link length is interpolated.
      longNote.innerHTML = tooLong ? "Your request is long \u2014 " +
        href.length.toLocaleString("en-CA") + " characters as an email link. Some email apps and phones will " +
        "not open a link that size, and the tap does nothing. Nothing has been sent yet: use " +
        "<b>Copy the request</b> or <b>Save the request to a file</b>, then send it to " + TO +
        " \u2014 both carry this same request and cannot fail this way." : "";
    }
    if (btnRow) {
      if (tooLong) { btnRow.appendChild(mailLink); }
      else { btnRow.insertBefore(mailLink, btnRow.firstChild); }
    }

    result.classList.add("on");
    out.scrollIntoView({ block: "nearest" });
    copyNote.textContent = "";
  }

  // The control, the form's submit event and the Enter key all land in submitRequest,
  // and each one is stopped from becoming a real (insecure) form submission.
  if (prepBtn) { prepBtn.addEventListener("click", submitRequest); }
  form.addEventListener("submit", function (e) { e.preventDefault(); submitRequest(); });
  form.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && e.target && e.target.tagName !== "TEXTAREA") {
      e.preventDefault(); submitRequest();
    }
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

  // A third delivery path, independent of both the mail app and the clipboard: the visitor
  // leaves with the composed request as a plain .txt they can email or hand over any way.
  if (saveBtn) {
    saveBtn.addEventListener("click", function () {
      var text = out.value;
      try {
        var blob = new Blob([text], { type: "text/plain;charset=utf-8" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = "furnace-request.txt";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
        copyNote.textContent = "Saved as furnace-request.txt — email it to " + TO + " whenever you like.";
      } catch (e) {
        copyNote.textContent = "Could not save the file. Select the text above, copy it, and email it to " + TO + ".";
      }
    });
  }
})();
