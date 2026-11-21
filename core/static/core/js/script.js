(() => {
    const toggle = document.querySelector(".menu-toggle");
    const navigation = document.querySelector("#main-nav");
    if (!toggle || !navigation) return;

    toggle.addEventListener("click", () => {
        const isOpen = navigation.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", String(isOpen));
    });

    navigation.addEventListener("click", (event) => {
        if (event.target.closest("a") && window.matchMedia("(max-width: 900px)").matches) {
            navigation.classList.remove("is-open");
            toggle.setAttribute("aria-expanded", "false");
        }
    });
})();
