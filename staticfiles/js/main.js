document.addEventListener('DOMContentLoaded', function () {

  const roleTabs = document.querySelectorAll('.role-tab');
  const roleInput = document.getElementById('role-input');
  const roleFieldGroups = document.querySelectorAll('.role-fields');
  const accentMap = {
    agriculteur: '#3D7A2B',
    acheteur: '#C45C2A',
    transporteur: '#2E7FB5',
  };

  function activateRole(role) {
    roleTabs.forEach(tab => tab.classList.toggle('is-active', tab.dataset.role === role));
    roleFieldGroups.forEach(group => group.classList.toggle('is-visible', group.dataset.roleFields === role));
    if (roleInput) roleInput.value = role;
    if (accentMap[role]) document.documentElement.style.setProperty('--accent-current', accentMap[role]);
  }

  if (roleTabs.length) {
    activateRole((roleInput && roleInput.value) || 'acheteur');
    roleTabs.forEach(tab => tab.addEventListener('click', () => activateRole(tab.dataset.role)));
  }

  document.querySelectorAll('.password-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.toggleFor);
      if (!input) return;
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.textContent = isHidden ? 'Masquer' : 'Afficher';
    });
  });

  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
    });
  }

});