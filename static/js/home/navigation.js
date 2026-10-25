document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('.navbar');
    const heroSlider = document.querySelector('.hero-slider');
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    const searchToggle = document.querySelector('.mobile-search-toggle');
    const searchContainer = document.querySelector('.search-container');
    const searchOverlay = document.querySelector('.search-overlay');

    // Navbar Scroll Effect
    function checkScroll() {
        if (!navbar) return;
        
        if (heroSlider) {
            // Check if user scrolled OR if mobile menu is open
            const isMenuOpen = navLinks && navLinks.classList.contains('active');
            if (window.scrollY > 50 || isMenuOpen) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
            document.body.classList.remove('has-solid-navbar');
        } else {
            // Always solid on subpages
            navbar.classList.add('navbar-solid');
            document.body.classList.add('has-solid-navbar');
        }
    }

    // Run scroll check on load and scroll
    checkScroll();
    window.addEventListener('scroll', checkScroll);

    // Mobile Nav Toggle
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            // Close search if it's open
            if (searchContainer && searchContainer.classList.contains('active')) {
                searchContainer.classList.remove('active');
                if (searchOverlay) searchOverlay.classList.remove('active');
                if (searchToggle) {
                    const icon = searchToggle.querySelector('i');
                    if (icon) {
                        icon.classList.remove('ri-close-line');
                        icon.classList.add('ri-search-line');
                    }
                }
            }
            // Toggle nav menu
            navLinks.classList.toggle('active');
            const icon = navToggle.querySelector('i');
            if (icon) {
                icon.classList.toggle('ri-menu-line');
                icon.classList.toggle('ri-close-line');
            }
            
            // Re-check scroll state so background turns solid when mobile menu is open
            checkScroll();
        });
    }

    // Mobile Search Toggle
    if (searchToggle && searchContainer) {
        searchToggle.addEventListener('click', () => {
            // Close nav menu if it's open
            if (navLinks && navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                if (navToggle) {
                    const icon = navToggle.querySelector('i');
                    if (icon) {
                        icon.classList.remove('ri-close-line');
                        icon.classList.add('ri-menu-line');
                    }
                }
            }
            // Toggle search
            searchContainer.classList.toggle('active');
            if (searchOverlay) searchOverlay.classList.toggle('active');
            const icon = searchToggle.querySelector('i');
            if (icon) {
                icon.classList.toggle('ri-search-line');
                icon.classList.toggle('ri-close-line');
            }
            
            // Re-check scroll state so background turns solid when search is open on mobile
            checkScroll();
        });
    }

    if (searchOverlay) {
        searchOverlay.addEventListener('click', () => {
            if (searchContainer) searchContainer.classList.remove('active');
            searchOverlay.classList.remove('active');
            if (searchToggle) {
                const icon = searchToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('ri-close-line');
                    icon.classList.add('ri-search-line');
                }
            }
            checkScroll();
        });
    }
});
