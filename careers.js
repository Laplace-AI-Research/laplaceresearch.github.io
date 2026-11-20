/* Laplace Research — careers: role buttons and the application form.
   The form posts to a form relay (Web3Forms by default) identified only by an
   access key, so no recipient address appears in the page. */
(function () {
  "use strict";

  var form = document.getElementById("apply-form");
  if (!form) return;

  var status = document.getElementById("form-status");
  var submit = form.querySelector('button[type="submit"]');
  var role = form.querySelector('[name="role"]');
  var key = form.querySelector('[name="access_key"]');
  var configured = key && key.value && key.value.indexOf("ACCESS_KEY") === -1;

  /* "Apply for this role" fills in the role and moves to the form */
  document.querySelectorAll("[data-role]").forEach(function (button) {
    button.addEventListener("click", function () {
      role.value = button.getAttribute("data-role");
      document.getElementById("apply").scrollIntoView({ behavior: "smooth", block: "start" });
      window.setTimeout(function () {
        form.querySelector('[name="name"]').focus({ preventScroll: true });
      }, 450);
    });
  });

  function say(message, kind) {
    status.textContent = message;
    status.dataset.kind = kind || "";
  }

  function fieldError(input, message) {
    var field = input.closest(".field");
    var note = field.querySelector(".field-error");
    if (!note) {
      note = document.createElement("p");
      note.className = "field-error";
      note.id = input.id + "-error";
      field.appendChild(note);
    }
    note.textContent = message;
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", note.id);
  }

  function clearErrors() {
    form.querySelectorAll(".field-error").forEach(function (n) { n.remove(); });
    form.querySelectorAll("[aria-invalid]").forEach(function (i) {
      i.removeAttribute("aria-invalid");
      i.removeAttribute("aria-describedby");
    });
  }

  function validate() {
    clearErrors();
    var first = null;
    form.querySelectorAll("[required]").forEach(function (input) {
      var value = input.value.trim();
      var message = "";
      if (!value) message = "Please fill this in.";
      else if (input.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) message = "Please enter a valid email address.";
      else if (input.type === "url" && !/^https?:\/\/\S+\.\S+/.test(value)) message = "Please enter a full link starting with https://";
      if (message) {
        fieldError(input, message);
        first = first || input;
      }
    });
    if (first) first.focus();
    return !first;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (!validate()) {
      say("Please check the highlighted fields.", "error");
      return;
    }
    if (form.querySelector('[name="botcheck"]').checked) return; // likely a bot

    if (!configured) {
      say("Applications can’t be submitted online right now. Please write to inquiries@laplaceresearch.org.", "error");
      return;
    }

    var data = {};
    new FormData(form).forEach(function (value, name) {
      if (name !== "botcheck") data[name] = typeof value === "string" ? value.trim() : value;
    });
    data.subject = "Application: " + data.role + " (" + data.name + ")";
    data.replyto = data.email;

    submit.disabled = true;
    say("Sending…");

    fetch(form.dataset.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(data),
    })
      .then(function (response) {
        return response.json().catch(function () { return {}; }).then(function (body) {
          if (!response.ok || body.success === false) throw new Error(body.message || "Request failed");
        });
      })
      .then(function () {
        form.reset();
        say("Thank you. Your application has been received, and we’ll be in touch.", "ok");
      })
      .catch(function () {
        say("Something went wrong sending your application. Please try again in a moment.", "error");
      })
      .then(function () {
        submit.disabled = false;
      });
  });
})();
