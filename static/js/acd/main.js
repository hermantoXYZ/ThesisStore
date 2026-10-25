// alert2 auto-close
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert2');
    alerts.forEach(alert => {
        alert.style.transition = "opacity 0.5s ease-out";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
    });
}, 4000);

// Sidebar toggle
const toggleButton = document.getElementById('toggle-sidebar');
const dashboardContainer = document.querySelector('.dashboard-container');
const mainContent = document.querySelector('.main-content');
const sidebar = document.querySelector('.sidebar');

const checkScreenWidth = () => {
    if (window.innerWidth <= 768) {
        dashboardContainer.classList.add('sidebar-collapsed');
    }
};

checkScreenWidth();
window.addEventListener('resize', checkScreenWidth);

toggleButton.addEventListener('click', (e) => {
    e.stopPropagation();
    dashboardContainer.classList.toggle('sidebar-collapsed');
});
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !toggleButton.contains(e.target)) {
            dashboardContainer.classList.add('sidebar-collapsed');
        }
    }
});

// Active menu
const menuItems = document.querySelectorAll('.sidebar-menu li:not(.has-dropdown)');
menuItems.forEach(item => {
    item.addEventListener('click', (e) => {
        // Remove active from all non-dropdown items
        menuItems.forEach(i => i.classList.remove('active'));
        item.classList.add('active');
    });
});

// Active submenu items
const submenuItems = document.querySelectorAll('.sidebar-menu .submenu li');
submenuItems.forEach(item => {
    item.addEventListener('click', (e) => {
        // Remove active from all submenu items
        submenuItems.forEach(i => i.classList.remove('active'));
        item.classList.add('active');
    });
});

// Dropdown menu
const dropdownItems = document.querySelectorAll('.has-dropdown > a');
dropdownItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const parent = item.parentElement;
        
        // Toggle current dropdown
        if (parent.classList.contains('active')) {
            parent.classList.remove('active');
        } else {
            // Close other dropdowns
            dropdownItems.forEach(other => {
                if (other !== item) {
                    other.parentElement.classList.remove('active');
                }
            });
            parent.classList.add('active');
        }
    });
});

// Dark mode
const darkModeToggle = document.querySelector('.ri-contrast-2-fill');
if (localStorage.getItem('darkMode') === 'enabled') {
    document.body.classList.add('dark-mode');
}
darkModeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('darkMode', 'enabled');
    } else {
        localStorage.setItem('darkMode', null);
    }
});

// Notification modal
const notificationButton = document.querySelector('.ri-notification-3-line');
const notificationModal = document.getElementById('notificationModal');
notificationButton.addEventListener('click', (e) => {
    e.stopPropagation();
    notificationModal.classList.toggle('show-notification');
});
document.addEventListener('click', (e) => {
    if (!notificationModal.contains(e.target) && !notificationButton.contains(e.target)) {
        notificationModal.classList.remove('show-notification');
    }
});

// Modal logout
function openModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = "block";
}
function closeModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = "none";
}
window.onclick = function(event) {
    var modals = document.getElementsByClassName('modal-edit');
    for (var i = 0; i < modals.length; i++) {
        if (event.target == modals[i]) {
            modals[i].style.display = "none";
        }
    }
}



// Search filter
let currentPage = 1;
let recordsPerPage = 10; // Default is 10
let totalRecords = 0;
let filteredData = []; // Store filtered data

// Listen for search input
const searchInput = document.getElementById('searchInput');
searchInput.addEventListener('keyup', function () {
    let searchQuery = this.value.toLowerCase();
    filterData(searchQuery);
    displayTable();
    updatePagination();
});

// Listen for records per page change
const recordsPerPageSelect = document.getElementById('recordsPerPage');
recordsPerPageSelect.addEventListener('change', function () {
    recordsPerPage = parseInt(this.value);
    currentPage = 1; // Reset to first page on records per page change
    displayTable();
    updatePagination();
});

// Function to filter data based on search query
function filterData(query) {
    filteredData = [...document.querySelectorAll('.student-table tbody tr')].filter(row => {
        let cells = row.getElementsByTagName('td');
        let found = false;
        for (let cell of cells) {
            if (cell.textContent.toLowerCase().indexOf(query) > -1) {
                found = true;
                break;
            }
        }
        return found;
    });
    totalRecords = filteredData.length;
}

// Function to display data in the table
function displayTable() {
    const start = (currentPage - 1) * recordsPerPage;
    const end = start + recordsPerPage;

    // Hide all rows
    document.querySelectorAll('.student-table tbody tr').forEach(row => {
        row.style.display = 'none';
    });

    // Show only the filtered data for the current page
    filteredData.slice(start, end).forEach(row => {
        row.style.display = '';
    });
}

// Function to update pagination buttons
function updatePagination() {
    const totalPages = Math.ceil(totalRecords / recordsPerPage);
    const paginationDiv = document.getElementById('pagination');
    const prevButton = document.getElementById('prev');
    const nextButton = document.getElementById('next');
    const pageNumberDiv = document.getElementById('pageNumber');

    // Update page number
    pageNumberDiv.textContent = currentPage;

    // Enable or disable Prev button
    prevButton.disabled = currentPage === 1;

    // Enable or disable Next button
    nextButton.disabled = currentPage === totalPages;

    // Show the correct number of pages
    paginationDiv.innerHTML = `
        <button id="prev" class="pagination-btn" onclick="changePage(currentPage - 1)" ${currentPage === 1 ? 'disabled' : ''}>Prev</button>
        <span id="pageNumber" class="page-number">${currentPage}</span>
        <button id="next" class="pagination-btn" onclick="changePage(currentPage + 1)" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>
    `;
}

// Function to change page
function changePage(page) {
    currentPage = page;
    displayTable();
    updatePagination();
}

// Initialize the table
document.addEventListener('DOMContentLoaded', function () {
    filterData(''); // Initial filter (no search query)
    displayTable();
    updatePagination();
});



function updateNotificationCount() {
        fetch("{% url 'acd:notif_prodi' %}")
            .then(response => response.json())
            .then(data => {
                const count = data.count;
                const notifElement = document.querySelector('.notif-count');

                if (count > 0) {
                    notifElement.textContent = count > 9 ? '9+' : count;
                    notifElement.style.display = 'inline-block';
                } else {
                    notifElement.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Gagal memuat notifikasi:', error);
            });
    }

    document.addEventListener('DOMContentLoaded', function() {
        updateNotificationCount();
        setInterval(updateNotificationCount, 10000); // tiap 10 detik
    });

    function updateNotificationModal() {
        fetch("{% url 'acd:notif_prodi' %}")
            .then(response => response.json())
            .then(data => {
                const notifList = document.querySelector('.notification-list');
                notifList.innerHTML = ''; // Kosongkan daftar notifikasi
    
                data.data.forEach(item => {
                    const notifItem = `
                        <div class="notification-item">
                            <img src="/${item.avatar}" alt="User Avatar" class="notification-avatar">
                            <div class="notification-content">
                                <p><strong>${item.mhs}</strong> ${item.jenis_layanan}</p>
                                <span class="notification-time">${item.date_in}</span>
                            </div>
                        </div>
                    `;
                    notifList.innerHTML += notifItem;
                });
    
                const notifCount = document.querySelector('.notif-count');
                if (data.count > 0) {
                    notifCount.textContent = data.count > 9 ? '9+' : data.count;
                    notifCount.style.display = 'inline-block';
                } else {
                    notifCount.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Gagal memuat notifikasi:', error);
            });
    }
    
    document.addEventListener('DOMContentLoaded', function() {
        updateNotificationModal();
        setInterval(updateNotificationModal, 10000); // Perbarui setiap 10 detik
    });



