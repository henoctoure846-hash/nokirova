// PWA Installation Handler - NOKIROVA 🌸

let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  console.log('✅ PWA installable détectée');

  const installBtn = document.getElementById('installPwaBtn');
  if (installBtn) {
    installBtn.style.display = 'flex';
    installBtn.addEventListener('click', () => {
      installBtn.style.display = 'none';
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('✅ PWA installée');
        }
        deferredPrompt = null;
      });
    });
  }
});

window.addEventListener('appinstalled', () => {
  console.log('🎉 PWA installée avec succès');
});

if (window.matchMedia('(display-mode: standalone)').matches) {
  console.log('📱 NOKIROVA en mode PWA');
}

// Bannière d'invitation mobile
const showInstallBanner = () => {
  const banner = document.getElementById('pwaBanner');
  if (banner && !localStorage.getItem('pwaBannerClosed')) {
    setTimeout(() => {
      banner.style.display = 'flex';
    }, 3000);
  }
};

if (window.matchMedia('(max-width: 768px)').matches && !window.matchMedia('(display-mode: standalone)').matches) {
  showInstallBanner();
}

function closePwaBanner() {
  const banner = document.getElementById('pwaBanner');
  if (banner) {
    banner.style.display = 'none';
    localStorage.setItem('pwaBannerClosed', 'true');
  }
}

// Ajouter la bannière si elle n'existe pas
if (!document.getElementById('pwaBanner')) {
  const style = document.createElement('style');
  style.textContent = `
    .pwa-install-banner {
      position: fixed;
      bottom: 20px;
      left: 20px;
      right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 20px;
      padding: 15px 20px;
      display: none;
      align-items: center;
      justify-content: space-between;
      gap: 15px;
      z-index: 1000;
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
      animation: slideUp 0.5s ease;
    }
    @keyframes slideUp {
      from { transform: translateY(100px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    .pwa-install-banner-content {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
    }
    .pwa-install-banner-icon { font-size: 32px; }
    .pwa-install-banner-text h4 { margin: 0; font-size: 16px; }
    .pwa-install-banner-text p { margin: 4px 0 0; font-size: 12px; opacity: 0.9; }
    .pwa-install-btn {
      background: white;
      color: #764ba2;
      border: none;
      padding: 10px 20px;
      border-radius: 30px;
      font-weight: bold;
      cursor: pointer;
    }
    .pwa-close-btn {
      background: rgba(255,255,255,0.2);
      border: none;
      color: white;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      cursor: pointer;
      font-size: 18px;
    }
  `;
  document.head.appendChild(style);

  const bannerHtml = `
    <div id="pwaBanner" class="pwa-install-banner">
      <div class="pwa-install-banner-content">
        <div class="pwa-install-banner-icon">📱</div>
        <div class="pwa-install-banner-text">
          <h4>Installe NOKIROVA</h4>
          <p>Révise plus vite avec l'application</p>
        </div>
      </div>
      <button id="installPwaBtnBanner" class="pwa-install-btn">Installer</button>
      <button class="pwa-close-btn" onclick="closePwaBanner()">✕</button>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', bannerHtml);

  const bannerInstallBtn = document.getElementById('installPwaBtnBanner');
  if (bannerInstallBtn) {
    bannerInstallBtn.addEventListener('click', () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === 'accepted') {
            document.getElementById('pwaBanner')?.remove();
          }
          deferredPrompt = null;
        });
      }
    });
  }
}