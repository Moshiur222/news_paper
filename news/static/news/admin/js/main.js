/**
 * AdminDek - Modern Admin Dashboard
 * Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initSidebar();
    initMobileMenu();
    initDropdowns();
    initTooltips();
    initAnimations();
    initSearch();
    initThemeSwitcher();
});

/**
 * Sidebar Toggle
 */
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            // Save state to localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
        
        // Check saved state
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.classList.add('collapsed');
        }
    }
}

/**
 * Mobile Menu
 */
function initMobileMenu() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    // Create overlay element
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            // For mobile, toggle the sidebar differently
            if (window.innerWidth <= 1024) {
                sidebar.classList.toggle('active');
                overlay.classList.toggle('active');
            }
        });
        
        // Close sidebar when clicking overlay
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
        
        // Close sidebar on window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 1024) {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            }
        });
    }
}

/**
 * Dropdown Menus
 */
function initDropdowns() {
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('.dropdown');
        
        dropdowns.forEach(dropdown => {
            const trigger = dropdown.querySelector('.dropdown-toggle, .notification-btn, .message-btn');
            const menu = dropdown.querySelector('.dropdown-menu, .notification-dropdown, .message-dropdown');
            
            if (trigger && menu) {
                if (!dropdown.contains(e.target)) {
                    menu.classList.remove('active');
                }
            }
        });
    });
    
    // Toggle dropdowns on click
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = this.closest('.dropdown');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            // Close other dropdowns
            document.querySelectorAll('.dropdown-menu.active').forEach(m => {
                if (m !== menu) m.classList.remove('active');
            });
            
            menu.classList.toggle('active');
        });
    });
}

/**
 * Tooltips
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = this.getAttribute('data-tooltip');
            // Tooltip functionality is handled via CSS
        });
    });
}

/**
 * Animations on Scroll
 */
function initAnimations() {
    // Add animation classes when elements come into view
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fadeIn');
                
                // Add stagger animation to children
                const children = entry.target.querySelectorAll(':scope > *');
                children.forEach((child, index) => {
                    child.style.animationDelay = `${index * 0.1}s`;
                    child.classList.add('animate-slideInUp');
                });
            }
        });
    }, observerOptions);
    
    // Observe cards
    const cards = document.querySelectorAll('.stat-card, .chart-card, .table-card, .progress-card');
    cards.forEach(card => {
        observer.observe(card);
    });
}

/**
 * Search Functionality
 */
function initSearch() {
    const searchInput = document.querySelector('.search-box input');
    
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            
            // If you have a data table, filter it
            const table = document.querySelector('.data-table');
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    }
}

/**
 * Notification Mark as Read
 */
function markAllNotificationsRead() {
    const markAllLink = document.querySelector('.dropdown-header a');
    
    if (markAllLink) {
        markAllLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            const unreadItems = document.querySelectorAll('.notification-item.unread');
            unreadItems.forEach(item => {
                item.classList.remove('unread');
            });
        });
    }
}

// Initialize mark all read functionality
markAllNotificationsRead();

/**
 * Active Menu Item
 */
function setActiveMenuItem() {
    const menuLinks = document.querySelectorAll('.menu-link');
    const currentPath = window.location.pathname;
    
    menuLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || href === '#') {
            // Remove active from all
            document.querySelector('.menu-item.active')?.classList.remove('active');
            // Add active to parent
            link.closest('.menu-item')?.classList.add('active');
        }
    });
}

// Call on load
setActiveMenuItem();

/**
 * Number Counter Animation
 */
function animateCounters() {
    const counters = document.querySelectorAll('.stat-content h3');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace(/,/g, ''));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const updateCounter = () => {
            current += step;
            if (current < target) {
                counter.textContent = Math.floor(current).toLocaleString();
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target.toLocaleString();
            }
        };
        
        // Start animation when element is in view
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                updateCounter();
                observer.unobserve(counter);
            }
        });
        
        observer.observe(counter);
    });
}

// Initialize counter animation
animateCounters();

/**
 * Mobile Submenu Toggle
 */
function initMobileSubmenu() {
    const menuItems = document.querySelectorAll('.has-submenu');
    
    menuItems.forEach(item => {
        const link = item.querySelector('.menu-link');
        const submenu = item.querySelector('.submenu');
        
        if (link && submenu) {
            link.addEventListener('click', function(e) {
                if (window.innerWidth <= 1024) {
                    e.preventDefault();
                    submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
                }
            });
        }
    });
}

initMobileSubmenu();

/**
 * Chart Resize Handler
 */
function handleChartResize() {
    let resizeTimer;
    
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Trigger custom event for charts to resize
            window.dispatchEvent(new CustomEvent('chartResize'));
        }, 250);
    });
}

handleChartResize();

/**
 * Keyboard Navigation
 */
function initKeyboardNav() {
    document.addEventListener('keydown', function(e) {
        // Escape to close dropdowns and sidebar on mobile
        if (e.key === 'Escape') {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            
            if (window.innerWidth <= 1024 && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            }
            
            // Close dropdowns
            document.querySelectorAll('.dropdown-menu.active, .notification-dropdown.active').forEach(menu => {
                menu.classList.remove('active');
            });
        }
    });
}

initKeyboardNav();

/**
 * Progress Bar Animation
 */
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill, .browser-fill');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.style.width;
                bar.style.width = '0';
                
                setTimeout(() => {
                    bar.style.width = width;
                }, 100);
                
                observer.unobserve(bar);
            }
        });
    });
    
    progressBars.forEach(bar => {
        observer.observe(bar);
    });
}

animateProgressBars();

/**
 * Table Row Hover Effect
 */
function initTableHover() {
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('click', function() {
            // Optional: Add click handler for table rows
            console.log('Row clicked:', this);
        });
    });
}

initTableHover();

// theme switcher utilities
/**
 * Apply selected theme by setting data-theme attribute.
 */
function applyTheme(theme) {
    document.documentElement.removeAttribute('data-theme');
    if (theme && theme !== 'light') {
        document.documentElement.setAttribute('data-theme', theme);
    }
}

/**
 * Mark current choice in dropdown menu.
 */
function updateThemeMenu() {
    const selected = localStorage.getItem('selectedTheme') || 'light';
    document.querySelectorAll('.theme-option[data-theme]').forEach(link => {
        link.classList.toggle('active', link.dataset.theme === selected);
    });
}

/**
 * Wire up theme picker and restore last setting.
 */
function initThemeSwitcher() {
    const themeBtn = document.getElementById('themeToggle');
    const themeDropdown = document.querySelector('.theme-dropdown');
    const themeOptions = document.querySelectorAll('.theme-option[data-theme]');
    
    // Toggle dropdown on button click
    if (themeBtn && themeDropdown) {
        themeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            themeDropdown.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!themeDropdown.contains(e.target)) {
                themeDropdown.classList.remove('active');
            }
        });
    }
    
    // Theme selection
    themeOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            const theme = this.dataset.theme;
            applyTheme(theme);
            localStorage.setItem('selectedTheme', theme);
            updateThemeMenu();
            
            // Close dropdown after selection
            if (themeDropdown) {
                themeDropdown.classList.remove('active');
            }
        });
    });

    // load saved or fall back to system preference
    let saved = localStorage.getItem('selectedTheme');
    if (!saved) {
        saved = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    applyTheme(saved);
    updateThemeMenu();
}

/**
 * User Dropdown Position Fix
 */
function fixUserDropdownPosition() {
    const userDropdown = document.querySelector('.user-dropdown');
    const headerUser = document.querySelector('.header-user');
    
    if (userDropdown && headerUser) {
        const dropdownRect = userDropdown.getBoundingClientRect();
        
        if (dropdownRect.right > window.innerWidth) {
            userDropdown.style.left = 'auto';
            userDropdown.style.right = '0';
        }
    }
}

// Fix on resize
window.addEventListener('resize', fixUserDropdownPosition);

/**
 * Loading State
 */
function setLoading(element, isLoading) {
    if (isLoading) {
        element.classList.add('loading');
        element.style.position = 'relative';
        
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.style.position = 'absolute';
        spinner.style.top = '50%';
        spinner.style.left = '50%';
        spinner.style.transform = 'translate(-50%, -50%)';
        
        element.appendChild(spinner);
    } else {
        element.classList.remove('loading');
        const spinner = element.querySelector('.spinner');
        if (spinner) spinner.remove();
    }
}

// Export functions for global use
window.AdminDek = {
    setLoading,
    animateCounters,
    animateProgressBars
};
