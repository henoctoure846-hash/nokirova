// 🌸 NOKIROVA - Logique
JavaScript

// 🌐 URL automatique : local en dev, Render en prod
const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://nokirova-1.onrender.com';
let
sessionId = null;
let
courContent = '';

// ═══════════════════════════════════════════
// 🔧 NAVIGATION
// ═══════════════════════════════════════════
function
afficherPage(nom)
{
    document.querySelectorAll('.page').forEach(p= > p.classList.add('hidden'));
document.getElementById('page-' + nom).classList.remove('hidden');

document.querySelectorAll('.menu-btn').forEach(b= > b.classList.remove('active'));
event?.target?.classList?.add('active');

// Fermer
le
menu
mobile
document.getElementById('sidebar').classList.remove('open');

// Actualiser
profil
if (nom === 'profil')
chargerProfil();
}

function
toggleMenu()
{
    document.getElementById('sidebar').classList.toggle('open');
}

// ═══════════════════════════════════════════
// 🔔 NOTIFICATIONS
// ═══════════════════════════════════════════
function
notif(message, type='success')
{
    const
container = document.getElementById('notifContainer');
const
div = document.createElement('div');
div.className = `notification
notif -${type}
`;
div.textContent = message;
container.appendChild(div);
setTimeout(() = > div.remove(), 2800);
}

// ═══════════════════════════════════════════
// 📥 IMPORT
// ═══════════════════════════════════════════
document.getElementById('fichierInput').addEventListener('change', async (e) = > {
    const
file = e.target.files[0];
if (!file)
return;

const
zone = document.getElementById('zoneImport');
zone.textContent = '⏳ Lecture du fichier... 🔍 Détection automatique de la matière...';

const
formData = new
FormData();
formData.append('fichier', file);

try {
const res = await fetch(`${API_URL} / api / import `, {method: 'POST', body: formData});
const
data = await res.json();

if (data.success)
{
    sessionId = data.session_id;
document.getElementById('nomCoursSidebar').textContent = `${data.matiere}\n${data.nom}
`;
zone.textContent = `✅ Cours
chargé
avec
succès !\n\n🎯 MATIÈRE: ${data.matiere}\n📁 Fichier: ${data.nom}\n📊 Taille: ${data.taille}
caractères\n\n═══ APERÇU ═══\n\n${data.apercu}
`;
notif(`+10
XP - Cours
chargé !`, 'xp');
} else {
    zone.textContent = '❌ ' + data.detail;
}
} catch(err)
{
    zone.textContent = '❌ Erreur : ' + err.message;
}
});

// ═══════════════════════════════════════════
// 📸 OCR
     // ═══════════════════════════════════════════
document.getElementById('imageInput').addEventListener('change', async (e) = > {
const
file = e.target.files[0];
if (!file) return;

const
zone = document.getElementById('zoneOcr');
zone.textContent = '⏳ Lecture de l\'image... 🔍 Analyse par l\'IA... 🧠';

const
formData = new
FormData();
formData.append('image', file);

try {
const res = await fetch(`${API_URL} / api / ocr`, {method: 'POST', body: formData});
const
data = await res.json();
zone.textContent = data.resultat;
notif('+15 XP - Image scannée !', 'xp');
} catch(err)
{
    zone.textContent = '❌ Erreur : ' + err.message;
}
});

// ═══════════════════════════════════════════
// 📝 RÉSUMÉ / 💡 EXPLICATION
                // ═══════════════════════════════════════════
async function
genererResume()
{
if (!sessionId)
{notif('Importe d\'abord un cours !', 'error');
return;}
const
zone = document.getElementById('zoneResume');
zone.textContent = '⏳ NOKIROVA réfléchit... 🧠✨';

try {
const res = await fetch(`${API_URL} / api / resume / ${sessionId}`, {method: 'POST'});
const
data = await res.json();
zone.textContent = data.resume;
notif('+5 XP !', 'xp');
} catch(err)
{zone.textContent = '❌ ' + err.message;}
}

async function
genererExplication()
{
if (!sessionId) {notif('Importe d\'abord un cours !', 'error');
return;}
const
zone = document.getElementById('zoneExplication');
zone.textContent = '⏳ NOKIROVA réfléchit... 🧠✨';

try {
const res = await fetch(`${API_URL} / api / explication / ${sessionId}`, {method: 'POST'});
const
data = await res.json();
zone.textContent = data.explication;
notif('+5 XP !', 'xp');
} catch(err)
{zone.textContent = '❌ ' + err.message;}
}

// ═══════════════════════════════════════════
// 🎯 QCM / ❓ QUESTIONS / 📚 EXAMEN
                           // ═══════════════════════════════════════════
async function
genererQCM()
{
if (!sessionId) {notif('Importe d\'abord un cours !', 'error');
return;}
const
nb = parseInt(document.getElementById('qcmSlider').value);
const
zone = document.getElementById('zoneQcm');
zone.textContent = `⏳ Génération
de ${nb}
QCM... ✨`;

try {
const res = await fetch(`${API_URL} / api / qcm`, {
method: 'POST',
headers: {'Content-Type': 'application/json'},
body: JSON.stringify({session_id: sessionId, nombre: nb})
});
const
data = await res.json();
zone.textContent = data.qcm;
notif(`+${nb * 2}
XP !`, 'xp');
} catch(err)
{zone.textContent = '❌ ' + err.message;}
}

async function
genererQuestions()
{
if (!sessionId) {notif('Importe d\'abord un cours !', 'error');
return;}
const
nb = parseInt(document.getElementById('questSlider').value);
const
zone = document.getElementById('zoneQuestions');
zone.textContent = '⏳ Génération...';

try {
const res = await fetch(`${API_URL} / api / questions`, {
method: 'POST',
headers: {'Content-Type': 'application/json'},
body: JSON.stringify({session_id: sessionId, nombre: nb})
});
const
data = await res.json();
zone.textContent = data.questions;
notif(`+${nb * 2}
XP !`, 'xp');
} catch(err)
{zone.textContent = '❌ ' + err.message;}
}

async function
genererExamen()
{
if (!sessionId) {notif('Importe d\'abord un cours !', 'error');
return;}
const
nb = parseInt(document.getElementById('nbExSelect').value);
const
niveau = document.getElementById('niveauSelect').value;
const
zone = document.getElementById('zoneExamen');
zone.textContent = `⏳ Génération
de ${nb}
exercices...
`;

try {
const res = await fetch(`${API_URL} / api / examen`, {
method: 'POST',
headers: {'Content-Type': 'application/json'},
body: JSON.stringify({session_id: sessionId, nombre: nb, niveau: niveau})
});
const
data = await res.json();
zone.textContent = data.exercices;
notif(`+${nb * 5}
XP !`, 'xp');
} catch(err)
{zone.textContent = '❌ ' + err.message;}
}

// ═══════════════════════════════════════════
// 💬 CHAT
     // ═══════════════════════════════════════════
async function
envoyerQuestion()
{
const
question = document.getElementById('questionChat').value.trim();
if (!question) {notif('Tape une question !', 'error');
return;}

const
zone = document.getElementById('zoneChat');
zone.textContent = '⏳ NOKIROVA réfléchit... 🧠✨';

try {
const res = await fetch(`${API_URL} / api / chat`, {
method: 'POST',
headers: {'Content-Type': 'application/json'},
body: JSON.stringify({question: question})
});
const
data = await res.json();
zone.textContent = data.reponse;
notif('+5 XP !', 'xp');
} catch(err)
{zone.textContent = '❌ ' + err.message;}
}

// ═══════════════════════════════════════════
// 🎧 AUDIO
     // ═══════════════════════════════════════════
async function
creerAudio()
{
const
texte = document.getElementById('texteAudio').value.trim();
if (!texte) {notif('Tape du texte d\'abord !', 'error');
return;}

const
voix = document.getElementById('voixSelect').value;
const
zone = document.getElementById('zoneAudio');
zone.textContent = '⏳ Création de l\'audio...';

try {
const res = await fetch(`${API_URL} / api / audio`, {
method: 'POST',
headers: {'Content-Type': 'application/json'},
body: JSON.stringify({texte: texte, voix: voix})
});
const
data = await res.json();
zone.innerHTML = `✅ Audio
créé ! < br > < br > < audio
controls
src = "${API_URL}${data.url}"
style = "width:100%" > < / audio > `;
notif('+8 XP - Audio créé !', 'xp');
} catch(err)
{zone.textContent = '❌ ' + err.message;}
}

function
remplirAvecCours()
{
if (!sessionId) {notif('Importe d\'abord un cours !', 'error');
return;}
notif('Texte du cours chargé !', 'success');
}

// ═══════════════════════════════════════════
// 🏆 PROFIL
     // ═══════════════════════════════════════════
async function
chargerProfil()
{
try {
const res = await fetch(`${API_URL} / api / profil`);
const data = await res.json();
const s = data.stats;

document.getElementById('statNiveau').textContent = `Niveau ${s.niveau}`;
document.getElementById('statXp').textContent = `${s.xp} XP`;
document.getElementById('statStreak').textContent = `${s.streak} jour(s)`;
document.getElementById('statCours').textContent = s.cours_importes;

document.getElementById('profilTitre').textContent = data.titre;
document.getElementById('profilNiveau').textContent = s.niveau;
document.getElementById('profilXp').textContent = s.xp;
document.getElementById('profilStreak').textContent = s.streak;
document.getElementById('profilCours').textContent = s.cours_importes;
document.getElementById('profilQuestions').textContent = s.questions_posees;
document.getElementById('profilAudios').textContent = s.audios_crees;
document.getElementById('profilQcm').textContent = s.qcm_reussis;

const xpActuel = s.xp % 100;
document.getElementById('progressFill').style.width = xpActuel + '%';
document.getElementById('progressTexte').textContent = `🎯 ${xpActuel} / 100 XP vers niveau ${s.niveau + 1}`;

const container = document.getElementById('badgesContainer');
if (data.badges.length > 0) {
container.innerHTML = data.badges.map(b = >
` < div


class ="badge-item" > < p class ="nom" > ${b.emoji} ${b.nom} < / p > < p class ="desc" > ${b.description} < / p > < / div > `

).join('');
}
} catch(err)
{console.error('Erreur profil:', err);}
}

// ═══════════════════════════════════════════
// 📄 EXPORT
PDF
// ═══════════════════════════════════════════
async function
exporterPDF(type, zoneId)
{
    const
contenu = document.getElementById(zoneId).textContent;
if (!contenu | | contenu.includes('👆') | | contenu.includes('⚠️')) {
    notif('Génère du contenu d\'abord !', 'error');
return;
}

const
formData = new
FormData();
formData.append('contenu', contenu);
formData.append('titre', `NOKIROVA ${type}
`);
formData.append('nom', type);

try {
const res = await fetch(`${API_URL} / api / pdf`, {method: 'POST', body: formData});
const
data = await res.json();
notif('📄 PDF créé !', 'success');
} catch(err)
{notif('Erreur PDF', 'error');}
}

// ═══════════════════════════════════════════
// 🚀 DÉMARRAGE
     // ═══════════════════════════════════════════
chargerProfil();
console.log('🌸 NOKIROVA Web démarré !');