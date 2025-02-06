function _defineProperty(obj, key, value) {
  if (key in obj) {
      Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true });
  } else {
      obj[key] = value;
  }
  return obj;
}

const ANIMATION_DURATION = 300;
const SIDEBAR_EL = document.getElementById("sidebar");
const SUB_MENU_ELS = document.querySelectorAll(".menu > ul > .menu-item.sub-menu");
const FIRST_SUB_MENUS_BTN = document.querySelectorAll(".menu > ul > .menu-item.sub-menu > a");
const INNER_SUB_MENUS_BTN = document.querySelectorAll(".menu > ul > .menu-item.sub-menu .menu-item.sub-menu > a");

class PopperObject {
  constructor(reference, popperTarget) {
      _defineProperty(this, "instance", null);
      _defineProperty(this, "reference", null);
      _defineProperty(this, "popperTarget", null);
      this.init(reference, popperTarget);
  }

  init(reference, popperTarget) {
      this.reference = reference;
      this.popperTarget = popperTarget;
      this.instance = Popper.createPopper(this.reference, this.popperTarget, {
          placement: "right",
          strategy: "fixed",
          resize: true,
          modifiers: [
              {
                  name: "computeStyles",
                  options: { adaptive: false }
              },
              {
                  name: "flip",
                  options: { fallbackPlacements: ["left", "right"] }
              }
          ]
      });

      document.addEventListener("click", (e) => this.clicker(e, this.popperTarget, this.reference), false);

      const ro = new ResizeObserver(() => {
          this.instance.update();
      });

      ro.observe(this.popperTarget);
      ro.observe(this.reference);
  }

  clicker(event, popperTarget, reference) {
      if (SIDEBAR_EL.classList.contains("collapsed") && !popperTarget.contains(event.target) && !reference.contains(event.target)) {
          this.hide();
      }
  }

  hide() {
      this.instance.state.elements.popper.style.visibility = "hidden";
  }
}

class Poppers {
  constructor() {
      _defineProperty(this, "subMenuPoppers", []);
      this.init();
  }

  init() {
      SUB_MENU_ELS.forEach(element => {
          this.subMenuPoppers.push(new PopperObject(element, element.lastElementChild));
          this.closePoppers();
      });
  }

  togglePopper(target) {
      target.style.visibility = target.style.visibility === "hidden" ? "visible" : "hidden";
  }

  updatePoppers() {
      this.subMenuPoppers.forEach(element => {
          element.instance.state.elements.popper.style.display = "none";
          element.instance.update();
      });
  }

  closePoppers() {
      this.subMenuPoppers.forEach(element => {
          element.hide();
      });
  }
}

const PoppersInstance = new Poppers();

const updatePoppersTimeout = () => {
  setTimeout(() => {
      PoppersInstance.updatePoppers();
  }, ANIMATION_DURATION);
};

// Verifica se os elementos existem antes de adicionar os event listeners
const btnCollapse = document.getElementById("btn-collapse");
if (btnCollapse) {
  btnCollapse.addEventListener("click", () => {
      SIDEBAR_EL.classList.toggle("collapsed");
      PoppersInstance.closePoppers();
      if (SIDEBAR_EL.classList.contains("collapsed")) {
          FIRST_SUB_MENUS_BTN.forEach(element => element.parentElement.classList.remove("open"));
      }
      updatePoppersTimeout();
  });
}

const btnToggle = document.getElementById("btn-toggle");
if (btnToggle) {
  btnToggle.addEventListener("click", () => {
      SIDEBAR_EL.classList.toggle("toggled");
      updatePoppersTimeout();
  });
}

const overlay = document.getElementById("overlay");
if (overlay) {
  overlay.addEventListener("click", () => {
      SIDEBAR_EL.classList.toggle("toggled");
  });
}

const defaultOpenMenus = document.querySelectorAll(".menu-item.sub-menu.open");
defaultOpenMenus.forEach(element => {
  element.lastElementChild.style.display = "block";
});

FIRST_SUB_MENUS_BTN.forEach(element => {
  element.addEventListener("click", () => {
      if (SIDEBAR_EL.classList.contains("collapsed")) {
          PoppersInstance.togglePopper(element.nextElementSibling);
      } else {
          const parentMenu = element.closest(".menu.open-current-submenu");
          if (parentMenu) {
              parentMenu.querySelectorAll(":scope > ul > .menu-item.sub-menu > a").forEach(el => {
                  if (window.getComputedStyle(el.nextElementSibling).display !== "none") {
                      slideUp(el.nextElementSibling);
                  }
              });
          }
          slideToggle(element.nextElementSibling);
      }
  });
});

INNER_SUB_MENUS_BTN.forEach(element => {
  element.addEventListener("click", () => {
      slideToggle(element.nextElementSibling);
  });
});
