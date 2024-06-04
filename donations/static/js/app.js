document.addEventListener("DOMContentLoaded", function() {
  /**
   * HomePage - Help section
   */
  class Help {
    constructor($el) {
      this.$el = $el;
      this.$buttonsContainer = $el.querySelector(".help--buttons");
      this.$slidesContainers = $el.querySelectorAll(".help--slides");
      this.currentSlide = this.$buttonsContainer.querySelector(".active").parentElement.dataset.id;
      this.init();
    }

    init() {
      this.events();
    }

    events() {
      /**
       * Slide buttons
       */
      this.$buttonsContainer.addEventListener("click", e => {
        if (e.target.classList.contains("btn")) {
          this.changeSlide(e);
        }
      });

      /**
       * Pagination buttons
       */
      this.$el.addEventListener("click", e => {
        if (e.target.classList.contains("btn") && e.target.parentElement.parentElement.classList.contains("help--slides-pagination")) {
          this.changePage(e);
        }
      });
    }

    changeSlide(e) {
      e.preventDefault();
      const $btn = e.target;

      // Buttons Active class change
      [...this.$buttonsContainer.children].forEach(btn => btn.firstElementChild.classList.remove("active"));
      $btn.classList.add("active");

      // Current slide
      this.currentSlide = $btn.parentElement.dataset.id;

      // Slides active class change
      this.$slidesContainers.forEach(el => {
        el.classList.remove("active");

        if (el.dataset.id === this.currentSlide) {
          el.classList.add("active");
        }
      });
    }

    /**
     * TODO: callback to page change event
     */
    changePage(e) {
      e.preventDefault();
      const page = e.target.dataset.page;

      console.log(page);
    }
  }
  const helpSection = document.querySelector(".help");
  if (helpSection !== null) {
    new Help(helpSection);
  }

  /**
   * Form Select
   */
  class FormSelect {
    constructor($el) {
      this.$el = $el;
      this.options = [...$el.children];
      this.init();
    }

    init() {
      this.createElements();
      this.addEvents();
      this.$el.parentElement.removeChild(this.$el);
    }

    createElements() {
      // Input for value
      this.valueInput = document.createElement("input");
      this.valueInput.type = "text";
      this.valueInput.name = this.$el.name;

      // Dropdown container
      this.dropdown = document.createElement("div");
      this.dropdown.classList.add("dropdown");

      // List container
      this.ul = document.createElement("ul");

      // All list options
      this.options.forEach((el, i) => {
        const li = document.createElement("li");
        li.dataset.value = el.value;
        li.innerText = el.innerText;

        if (i === 0) {
          // First clickable option
          this.current = document.createElement("div");
          this.current.innerText = el.innerText;
          this.dropdown.appendChild(this.current);
          this.valueInput.value = el.value;
          li.classList.add("selected");
        }

        this.ul.appendChild(li);
      });

      this.dropdown.appendChild(this.ul);
      this.dropdown.appendChild(this.valueInput);
      this.$el.parentElement.appendChild(this.dropdown);
    }

    addEvents() {
      this.dropdown.addEventListener("click", e => {
        const target = e.target;
        this.dropdown.classList.toggle("selecting");

        // Save new value only when clicked on li
        if (target.tagName === "LI") {
          this.valueInput.value = target.dataset.value;
          this.current.innerText = target.innerText;
        }
      });
    }
  }
  document.querySelectorAll(".form-group--dropdown select").forEach(el => {
    new FormSelect(el);
  });

  /**
   * Hide elements when clicked on document
   */
  document.addEventListener("click", function(e) {
    const target = e.target;
    const tagName = target.tagName;

    if (target.classList.contains("dropdown")) return false;

    if (tagName === "LI" && target.parentElement.parentElement.classList.contains("dropdown")) {
      return false;
    }

    if (tagName === "DIV" && target.parentElement.classList.contains("dropdown")) {
      return false;
    }

    document.querySelectorAll(".form-group--dropdown .dropdown").forEach(el => {
      el.classList.remove("selecting");
    });
  });

  /**
   * Switching between form steps
   */
  class FormSteps {
    constructor(form) {
      this.$form = form;
      this.$next = form.querySelectorAll(".next-step");
      this.$prev = form.querySelectorAll(".prev-step");
      this.$step = form.querySelector(".form--steps-counter span");
      this.currentStep = 1;

      this.$stepInstructions = form.querySelectorAll(".form--steps-instructions p");
      const $stepForms = form.querySelectorAll("form > div");
      this.slides = [...this.$stepInstructions, ...$stepForms];

      this.init();
    }

    /**
     * Init all methods
     */
    init() {
      this.events();
      this.updateForm();
    }

    /**
     * All events that are happening in form
     */
    events() {
      // Next step
      this.$next.forEach(btn => {
        btn.addEventListener("click", e => {
          e.preventDefault();
          this.currentStep++;
          this.updateForm();
        });
      });

      // Previous step
      this.$prev.forEach(btn => {
        btn.addEventListener("click", e => {
          e.preventDefault();
          this.currentStep--;
          this.updateForm();
        });
      });

      // Form submit
      this.$form.querySelector("form").addEventListener("submit", e => this.submit(e));

      // Filter institutions by selected categories
      document.querySelectorAll('.category-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
          this.filterInstitutions();
        });
      });
    }

    updateForm() {
      this.$step.innerText = this.currentStep;

      // TODO: Validation

      this.slides.forEach(slide => {
        slide.classList.remove("active");

        if (slide.dataset.step === this.currentStep) {
          slide.classList.add("active");
        }
      });

      this.$stepInstructions[0].parentElement.parentElement.hidden = this.currentStep >= 6;
      this.$step.parentElement.hidden = this.currentStep >= 6;

      // TODO: get data from inputs and show them in summary
      if (this.currentStep === 5) {
        this.showSummary();
      }
    }

    filterInstitutions() {
      const selectedCategories = [...document.querySelectorAll('.category-checkbox:checked')].map(cb => parseInt(cb.value));
      console.log("Selected categories:", selectedCategories); // Debugging line
      document.querySelectorAll('.institution').forEach(inst => {
        const instCategories = inst.dataset.categories ? inst.dataset.categories.split(',').map(Number) : [];
        console.log("Institution categories:", instCategories); // Debugging line
        const match = selectedCategories.every(cat => instCategories.includes(cat));
        inst.style.display = match ? 'block' : 'none';
        console.log(`Institution ${inst.dataset.categories} ${match ? "matches" : "does not match"}`); // Debugging line
      });
    }

    showSummary() {
      [...document.querySelectorAll('.category-checkbox:checked')].map(cb => cb.nextElementSibling.innerText).join(', ');
      const selectedInstitutionElement = document.querySelector('input[name="organization"]:checked');
      const selectedInstitution = selectedInstitutionElement ? selectedInstitutionElement.nextElementSibling.querySelector('.title').innerText : '';

      const summaryItems = [
        { selector: '.summary .icon-bag + .summary--text', text: `${document.querySelector('input[name="bags"]').value} worki ubrań` },
        { selector: '.summary .icon-hand + .summary--text', text: `Dla fundacji ${selectedInstitution}` },
        { selector: '.summary .address', text: document.querySelector('input[name="address"]').value },
        { selector: '.summary .city', text: document.querySelector('input[name="city"]').value },
        { selector: '.summary .postcode', text: document.querySelector('input[name="postcode"]').value },
        { selector: '.summary .phone', text: document.querySelector('input[name="phone"]').value },
        { selector: '.summary .date', text: document.querySelector('input[name="date"]').value },
        { selector: '.summary .time', text: document.querySelector('input[name="time"]').value },
        { selector: '.summary .more_info', text: document.querySelector('textarea[name="more_info"]').value || 'Brak uwag' }
      ];

      summaryItems.forEach(item => {
        const element = document.querySelector(item.selector);
        if (element) {
          element.innerText = item.text;
        }
      });
    }

    submit(e) {
      e.preventDefault();
      this.currentStep++;
      this.updateForm();
      if (this.currentStep > 5) {
        this.$form.querySelector('form').submit();
      }
    }
  }
  const form = document.querySelector(".form--steps");
  if (form !== null) {
    new FormSteps(form);
  }
});


document.addEventListener('DOMContentLoaded', function () {
  const tabButtons = document.querySelectorAll('.help--buttons a');
  const tabs = document.querySelectorAll('.help--slides');
  let activeTab = sessionStorage.getItem('activeTab') || 'foundations';

  function showTab(target) {
    tabs.forEach(tab => {
      if (tab.dataset.id === target) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
    tabButtons.forEach(btn => {
      if (btn.dataset.target === target) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  showTab(activeTab);

  tabButtons.forEach(button => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      const target = event.target.dataset.target;
      sessionStorage.setItem('activeTab', target);
      showTab(target);
      activeTab = target; // обновление активной вкладки
    });
  });

  const paginationLinks = document.querySelectorAll('.pagination a');
  paginationLinks.forEach(link => {
    link.addEventListener('click', (event) => {
      const url = new URL(event.target.href);
      url.searchParams.set('activeTab', activeTab);
      event.target.href = url.toString();
    });
  });
});


// static/js/app.js
document.addEventListener("DOMContentLoaded", function() {
    // Show dropdown menu on hover
    const dropdown = document.querySelector('.dropdown');
    if (dropdown) {
        dropdown.addEventListener('mouseenter', () => {
            dropdown.querySelector('.dropdown-content').style.display = 'block';
        });
        dropdown.addEventListener('mouseleave', () => {
            dropdown.querySelector('.dropdown-content').style.display = 'none';
        });
    }
});
