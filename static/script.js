// static/script.js
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector("[data-menu-toggle]");
  const list = document.querySelector("nav ul");
  if (toggle && list) {
    toggle.addEventListener("click", () => list.classList.toggle("open"));
  }
});
