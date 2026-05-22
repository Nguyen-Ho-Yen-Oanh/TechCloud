// Mobile menu toggle
const menuBtn = document.getElementById('menuBtn');
const navMenu = document.getElementById('navMenu');

if (menuBtn) {
    menuBtn.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });
}

// Close menu when clicking on link
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
    });
});

// Format currency VND
function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN', { 
        style: 'currency', 
        currency: 'VND',
        maximumFractionDigits: 0
    }).format(price);
}

// Format date
function formatDate(date) {
    if (!date) return 'N/A';
    return new Date(date).toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Check warranty status
function getWarrantyStatus(warrantyEndDate) {
    const today = new Date();
    const end = new Date(warrantyEndDate);
    const daysLeft = Math.ceil((end - today) / (1000 * 60 * 60 * 24));
    
    if (daysLeft > 30) {
        return { 
            text: 'Còn bảo hành', 
            class: 'badge-active', 
            icon: 'fa-check-circle',
            message: `Còn ${Math.floor(daysLeft / 30)} tháng ${daysLeft % 30} ngày bảo hành`
        };
    } else if (daysLeft > 0) {
        return { 
            text: 'Sắp hết bảo hành', 
            class: 'badge-warning', 
            icon: 'fa-exclamation-triangle',
            message: `Còn ${daysLeft} ngày bảo hành, vui lòng gia hạn sớm!`
        };
    } else {
        return { 
            text: 'Hết bảo hành', 
            class: 'badge-expired', 
            icon: 'fa-times-circle',
            message: 'Sản phẩm đã hết thời hạn bảo hành'
        };
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();
        
        const statsHtml = `
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-box"></i></div>
                <div class="stat-number">${data.total_products}</div>
                <div class="stat-label">Sản phẩm đang bảo hành</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-users"></i></div>
                <div class="stat-number">${data.total_customers}</div>
                <div class="stat-label">Khách hàng</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
                <div class="stat-number">${data.active_warranty}</div>
                <div class="stat-label">Đang bảo hành</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-tag"></i></div>
                <div class="stat-number">${data.total_brands}</div>
                <div class="stat-label">Thương hiệu</div>
            </div>
        `;
        
        document.getElementById('statsSection').innerHTML = statsHtml;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Check warranty function
async function checkWarranty() {
    const serial = document.getElementById('serialInput').value.trim();
    
    if (!serial) {
        alert('Vui lòng nhập IMEI/Serial Number!');
        return;
    }
    
    // Show loader
    document.getElementById('loader').style.display = 'block';
    document.getElementById('resultSection').innerHTML = '';
    
    try {
        const response = await fetch('/check_warranty', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `serial=${encodeURIComponent(serial)}`
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else {
            showResult(data);
        }
    } catch (error) {
        showError('Có lỗi xảy ra, vui lòng thử lại sau!');
    } finally {
        document.getElementById('loader').style.display = 'none';
    }
}

// Show result
function showResult(data) {
    const warrantyStatus = getWarrantyStatus(data.warranty_end_date);
    
    const html = `
        <div class="result-card">
            <div class="result-header">
                <h3>
                    <i class="fas ${warrantyStatus.icon}"></i>
                    KẾT QUẢ TRA CỨU BẢO HÀNH
                </h3>
            </div>
            <div class="result-content">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-mobile-alt"></i> Sản phẩm</div>
                        <div class="info-value"><strong>${data.product_name || 'N/A'}</strong></div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-trademark"></i> Thương hiệu</div>
                        <div class="info-value">${data.brand || 'N/A'} ${data.model ? `- ${data.model}` : ''}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-palette"></i> Màu sắc / Dung lượng</div>
                        <div class="info-value">${data.color || 'N/A'} | ${data.storage || 'N/A'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-user"></i> Khách hàng</div>
                        <div class="info-value"><strong>${data.customer_name || 'N/A'}</strong></div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-phone"></i> Số điện thoại</div>
                        <div class="info-value">${data.customer_phone || 'N/A'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-envelope"></i> Email</div>
                        <div class="info-value">${data.customer_email || 'N/A'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-calendar-alt"></i> Ngày mua</div>
                        <div class="info-value">${formatDate(data.purchase_date)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-calendar-check"></i> Hết hạn bảo hành</div>
                        <div class="info-value">${formatDate(data.warranty_end_date)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-money-bill-wave"></i> Giá trị sản phẩm</div>
                        <div class="info-value"><strong>${formatPrice(data.price)}</strong></div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-store"></i> Nơi mua hàng</div>
                        <div class="info-value">${data.store_location || 'N/A'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-shield-alt"></i> Trạng thái</div>
                        <div class="info-value">
                            <div class="warranty-badge ${warrantyStatus.class}">
                                <i class="fas ${warrantyStatus.icon}"></i>
                                ${warrantyStatus.text}
                            </div>
                            <p style="margin-top: 10px; font-size: 0.85rem; color: #666;">
                                ${warrantyStatus.message}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('resultSection').innerHTML = html;
    
    // Scroll to result
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Show error
function showError(message) {
    const html = `
        <div class="error-message">
            <i class="fas fa-exclamation-circle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
            <p style="font-size: 1.1rem; font-weight: 600;">${message}</p>
            <p style="margin-top: 10px;">Vui lòng kiểm tra lại IMEI/Serial Number</p>
            <p style="margin-top: 10px; font-size: 0.85rem;">🔍 Gợi ý: IPHONE15-ABC123, LAPTOP-DELL-XPS15, IPAD-PRO-M4</p>
        </div>
    `;
    document.getElementById('resultSection').innerHTML = html;
}

// Enter key support
document.getElementById('serialInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        checkWarranty();
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Load stats on page load
loadStats();