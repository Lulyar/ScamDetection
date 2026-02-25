/* ===== Pengiriman Formulir ===== */
function submitForm() {
    const textarea = document.getElementById('sms-input');
    const text = textarea.value.trim();
    const resultContainer = document.getElementById('result-container');
    const analyzeBtn = document.getElementById('analyze-btn');

    if (!text) {
        resultContainer.innerHTML = `
            <div class="result-card">
                <div class="result-icon">⚠️</div>
                <div class="result-title">Input Kosong</div>
                <div class="result-desc">Silakan masukkan teks SMS terlebih dahulu.</div>
            </div>
        `;
        return false;
    }

    // Tampilkan status memuat
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '⏳ Menganalisis...';
    resultContainer.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <div>ScamDetect AI sedang menganalisis pesan Anda...</div>
        </div>
    `;

    // Kirim permintaan ke API Flask
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        resultContainer.innerHTML = `
            <div class="result-card">
                <div class="result-icon">${data.icon}</div>
                <div class="result-title">${data.label}</div>
                <div class="result-desc">${data.description}</div>
            </div>
        `;
    })
    .catch(error => {
        resultContainer.innerHTML = `
            <div class="result-card">
                <div class="result-title">Terjadi Kesalahan</div>
                <div class="result-desc">${error.message}</div>
            </div>
        `;
    })
    .finally(() => {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🔍 Analisis Pesan';
    });

    return false;
}

/* ===== DOMContentLoaded — Inisialisasi Semua Fitur ===== */
window.addEventListener('DOMContentLoaded', function() {

    // --- Tombol Analisis ---
    const btn = document.getElementById('analyze-btn');
    if (btn) {
        btn.addEventListener('click', submitForm);
    }

    // --- Overlay Pemuatan ---
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        setTimeout(function() {
            overlay.classList.add('hidden');
        }, 1800);
    }

    // --- Menu Hamburger ---
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navbar-menu');
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('open');
        });
        // Tutup menu saat tautan diklik
        navMenu.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navMenu.classList.remove('open');
            });
        });
    }

    // --- Efek Tampil saat Scroll (IntersectionObserver) ---
    const revealElements = document.querySelectorAll('.scroll-reveal');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });

        revealElements.forEach(function(el) {
            observer.observe(el);
        });
    } else {
        // Fallback: tampilkan semua elemen langsung
        revealElements.forEach(function(el) {
            el.classList.add('revealed');
        });
    }

    // --- Status Aktif Navbar saat Scroll ---
    const sections = document.querySelectorAll('[id]');
    const navLinks = document.querySelectorAll('.navbar-link');

    function updateActiveLink() {
        const scrollY = window.scrollY + 100;
        let currentId = '';

        sections.forEach(function(section) {
            const top = section.offsetTop;
            const height = section.offsetHeight;
            if (scrollY >= top && scrollY < top + height) {
                currentId = section.getAttribute('id');
            }
        });

        navLinks.forEach(function(link) {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + currentId) {
                link.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', updateActiveLink);
    updateActiveLink();
});
