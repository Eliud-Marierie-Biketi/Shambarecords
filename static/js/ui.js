document.addEventListener('DOMContentLoaded', () => {
  const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
  const sidebarCloseControls = document.querySelectorAll('[data-sidebar-close]');
  const sidebar = document.querySelector('.sidebar');
  const backdrop = document.querySelector('.sidebar-backdrop');
  const dropdownButtons = document.querySelectorAll('[data-dropdown-toggle]');

  const setSidebarState = (isOpen) => {
    document.body.classList.toggle('sidebar-open', isOpen);
    if (sidebar) {
      sidebar.classList.toggle('is-open', isOpen);
    }
    if (backdrop) {
      backdrop.classList.toggle('is-open', isOpen);
      backdrop.setAttribute('aria-hidden', String(!isOpen));
    }
  };

  const closeSidebar = () => setSidebarState(false);

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      setSidebarState(!document.body.classList.contains('sidebar-open'));
    });
  }

  sidebarCloseControls.forEach((control) => {
    control.addEventListener('click', closeSidebar);
  });

  if (sidebar) {
    sidebar.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        if (window.matchMedia('(max-width: 1100px)').matches) {
          closeSidebar();
        }
      });
    });
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeSidebar();
    }
  });

  dropdownButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
      const dropdown = event.currentTarget.closest('.dropdown');
      if (dropdown) {
        dropdown.classList.toggle('is-open');
      }
    });
  });

  document.addEventListener('click', (event) => {
    document.querySelectorAll('.dropdown.is-open').forEach((dropdown) => {
      if (!dropdown.contains(event.target)) {
        dropdown.classList.remove('is-open');
      }
    });
  });

  setSidebarState(false);
});
