const menuToggle = document.querySelector(".menu-toggle");
const sidebar = document.querySelector("#sidebar");

if (menuToggle && sidebar) {
  menuToggle.addEventListener("click", () => {
    const expanded = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!expanded));
    sidebar.classList.toggle("is-open", !expanded);
  });
}

document.addEventListener("submit", (event) => {
  const form = event.target;
  if (form instanceof HTMLFormElement && form.dataset.confirm) {
    if (!window.confirm(form.dataset.confirm)) {
      event.preventDefault();
    }
  }
});
