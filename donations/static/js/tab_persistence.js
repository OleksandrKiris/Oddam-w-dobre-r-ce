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
