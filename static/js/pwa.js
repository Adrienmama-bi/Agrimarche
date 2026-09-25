/**
 * PWA AgriMarché — Gestion installation et Service Worker
 */

// ============================================================
// ENREGISTREMENT DU SERVICE WORKER
// ============================================================
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/static/sw.js', { scope: '/' })
      .then(function(registration) {
        console.log('[AgriMarché PWA] Service Worker enregistré :', registration.scope);

        // Vérifier les mises à jour
        registration.addEventListener('updatefound', function() {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', function() {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              _afficherBanniereMAJ();
            }
          });
        });
      })
      .catch(function(err) {
        console.warn('[AgriMarché PWA] Échec enregistrement SW :', err);
      });
  });
}

// ============================================================
// BANNIÈRE D'INSTALLATION (bouton "Installer l'app")
// ============================================================
let deferredPrompt = null;

window.addEventListener('beforeinstallprompt', function(e) {
  e.preventDefault();
  deferredPrompt = e;
  _afficherBanniereInstallation();
});

function _afficherBanniereInstallation() {
  const banniere = document.getElementById('pwa-install-banner');
  if (banniere) {
    banniere.style.display = 'flex';
    return;
  }

  const div = document.createElement('div');
  div.id = 'pwa-install-banner';
  div.innerHTML = `
    <div style="
      position: fixed;
      bottom: 80px;
      left: 50%;
      transform: translateX(-50%);
      background: #0B1F0E;
      color: white;
      border: 1.5px solid #7AE600;
      border-radius: 12px;
      padding: 14px 20px;
      display: flex;
      align-items: center;
      gap: 14px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      z-index: 9999;
      max-width: 360px;
      width: calc(100% - 32px);
      font-family: sans-serif;
    ">
      <div style="font-size: 32px; flex-shrink:0;">🌿</div>
      <div style="flex:1;">
        <div style="font-weight:700; font-size:14px; color:#7AE600;">
          Installer AgriMarché
        </div>
        <div style="font-size:12px; color:rgba(255,255,255,0.6); margin-top:2px;">
          Accédez à l'app directement depuis votre écran d'accueil
        </div>
      </div>
      <div style="display:flex; gap:8px; flex-direction:column;">
        <button onclick="installerPWA()" style="
          background:#7AE600; color:#0B1F0E; border:none;
          padding:8px 14px; border-radius:6px; font-weight:700;
          font-size:12px; cursor:pointer; white-space:nowrap;
        ">Installer</button>
        <button onclick="fermerBanniere()" style="
          background:transparent; color:rgba(255,255,255,0.4);
          border:1px solid rgba(255,255,255,0.2);
          padding:6px 10px; border-radius:6px; font-size:11px; cursor:pointer;
        ">Plus tard</button>
      </div>
    </div>
  `;
  document.body.appendChild(div);
}

function installerPWA() {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  deferredPrompt.userChoice.then(function(result) {
    if (result.outcome === 'accepted') {
      console.log('[AgriMarché PWA] Installée !');
      fermerBanniere();
    }
    deferredPrompt = null;
  });
}

function fermerBanniere() {
  const banniere = document.getElementById('pwa-install-banner');
  if (banniere) banniere.remove();
  localStorage.setItem('pwa-banniere-fermee', Date.now());
}

// Ne pas ré-afficher si fermée récemment (3 jours)
window.addEventListener('DOMContentLoaded', function() {
  const fermee = localStorage.getItem('pwa-banniere-fermee');
  if (fermee && Date.now() - parseInt(fermee) < 3 * 24 * 3600 * 1000) {
    deferredPrompt = null;
  }
});

// Confirmation que l'app est installée
window.addEventListener('appinstalled', function() {
  console.log('[AgriMarché PWA] Application installée avec succès');
  deferredPrompt = null;
  const banniere = document.getElementById('pwa-install-banner');
  if (banniere) banniere.remove();

  // Petit message de confirmation
  const msg = document.createElement('div');
  msg.innerHTML = `
    <div style="
      position:fixed; top:20px; left:50%; transform:translateX(-50%);
      background:#7AE600; color:#0B1F0E; padding:12px 20px;
      border-radius:8px; font-weight:700; font-size:14px;
      z-index:9999; box-shadow:0 4px 16px rgba(0,0,0,0.3);
    ">✓ AgriMarché installé sur votre appareil !</div>
  `;
  document.body.appendChild(msg);
  setTimeout(function() { msg.remove(); }, 4000);
});

// ============================================================
// BANNIÈRE MISE À JOUR
// ============================================================
function _afficherBanniereMAJ() {
  const div = document.createElement('div');
  div.innerHTML = `
    <div style="
      position:fixed; top:0; left:0; right:0;
      background:#0B1F0E; color:white; padding:12px 20px;
      display:flex; align-items:center; justify-content:space-between;
      z-index:9999; border-bottom:2px solid #7AE600;
      font-family:sans-serif; font-size:13px;
    ">
      <span>🌿 Une nouvelle version d'AgriMarché est disponible</span>
      <button onclick="location.reload()" style="
        background:#7AE600; color:#0B1F0E; border:none;
        padding:8px 16px; border-radius:6px; font-weight:700;
        font-size:12px; cursor:pointer;
      ">Mettre à jour</button>
    </div>
  `;
  document.body.appendChild(div);
}

// ============================================================
// INDICATEUR CONNEXION
// ============================================================
function _mettreAJourIndicateurConnexion() {
  const indicateur = document.getElementById('connexion-status');
  if (!indicateur) return;

  if (navigator.onLine) {
    indicateur.style.display = 'none';
  } else {
    indicateur.style.display = 'flex';
  }
}

window.addEventListener('online', function() {
  _mettreAJourIndicateurConnexion();
  console.log('[AgriMarché PWA] Connexion rétablie');
});

window.addEventListener('offline', function() {
  _mettreAJourIndicateurConnexion();
  console.log('[AgriMarché PWA] Connexion perdue');
});