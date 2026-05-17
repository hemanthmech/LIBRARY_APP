/**
 * main.js — LibraTrack frontend JavaScript
 *
 * Progressive enhancement: all core functionality works without JS.
 * This file adds convenience interactions only.
 */

"use strict";

/**
 * Auto-dismiss flash messages after 5 seconds.
 * Uses Bootstrap's Alert API for a smooth fade-out.
 */
function autoDismissAlerts() {
  const alerts = document.querySelectorAll(".alert.alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });
}

/**
 * Highlight the current navigation link by matching the URL pathname.
 */
function highlightActiveNav() {
  const currentPath = window.location.pathname;
  document.querySelectorAll(".navbar-nav .nav-link").forEach(function (link) {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}

// Run on DOM ready
document.addEventListener("DOMContentLoaded", function () {
  autoDismissAlerts();
  highlightActiveNav();
});
