// script.js

document.addEventListener("DOMContentLoaded", () => {
  console.log("JavaScript loaded!");

  // Example: simple button click handler
  const button = document.getElementById("actionButton");
  if (button) {
    button.addEventListener("click", () => {
      alert("Button was clicked!");
    });
  }
});
