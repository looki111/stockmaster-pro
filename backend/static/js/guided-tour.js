// StockMaster Pro - Guided Tour System

class GuidedTour {
    constructor() {
        this.currentStep = 0;
        this.steps = [
            {
                target: '[data-tour="dashboard"]',
                title: '{{ "لوحة التحكم" if lang == "ar" else "Dashboard" }}',
                content: '{{ "نظرة عامة على أداء متجرك" if lang == "ar" else "Overview of your store performance" }}',
                placement: 'bottom'
            },
            {
                target: '[data-tour="products"]',
                title: '{{ "المنتجات" if lang == "ar" else "Products" }}',
                content: '{{ "إدارة منتجاتك وإضافة منتجات جديدة" if lang == "ar" else "Manage your products and add new ones" }}',
                placement: 'right'
            },
            {
                target: '[data-tour="orders"]',
                title: '{{ "الطلبات" if lang == "ar" else "Orders" }}',
                content: '{{ "عرض وإدارة طلبات العملاء" if lang == "ar" else "View and manage customer orders" }}',
                placement: 'left'
            },
            {
                target: '[data-tour="inventory"]',
                title: '{{ "المخزون" if lang == "ar" else "Inventory" }}',
                content: '{{ "تتبع مخزونك وتلقي تنبيهات عند انخفاضه" if lang == "ar" else "Track your inventory and get alerts when low" }}',
                placement: 'right'
            },
            {
                target: '[data-tour="reports"]',
                title: '{{ "التقارير" if lang == "ar" else "Reports" }}',
                content: '{{ "تحليل أداء متجرك واتخاذ قرارات أفضل" if lang == "ar" else "Analyze your store performance and make better decisions" }}',
                placement: 'left'
            },
            {
                target: '[data-tour="settings"]',
                title: '{{ "الإعدادات" if lang == "ar" else "Settings" }}',
                content: '{{ "تخصيص إعدادات المتجر والصلاحيات" if lang == "ar" else "Customize store settings and permissions" }}',
                placement: 'top'
            }
        ];
        
        this.tourElement = null;
        this.overlay = null;
        this.init();
    }
    
    init() {
        // Create tour container
        this.tourElement = document.createElement('div');
        this.tourElement.className = 'guided-tour hidden';
        document.body.appendChild(this.tourElement);
        
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'tour-overlay hidden';
        document.body.appendChild(this.overlay);
        
        // Add tour button to navbar
        const tourButton = document.createElement('button');
        tourButton.className = 'btn-secondary ml-4';
        tourButton.innerHTML = '<i class="ri-question-line"></i> {{ "جولة تعليمية" if lang == "ar" else "Take Tour" }}';
        tourButton.onclick = () => this.start();
        document.querySelector('.navbar-actions').appendChild(tourButton);
    }
    
    start() {
        this.currentStep = 0;
        this.showStep();
        this.overlay.classList.remove('hidden');
    }
    
    end() {
        this.tourElement.classList.add('hidden');
        this.overlay.classList.add('hidden');
        localStorage.setItem('tour_completed', 'true');
    }
    
    showStep() {
        const step = this.steps[this.currentStep];
        const target = document.querySelector(step.target);
        
        if (!target) {
            this.next();
            return;
        }
        
        // Position tour element
        const rect = target.getBoundingClientRect();
        this.tourElement.style.top = `${rect.bottom + window.scrollY + 10}px`;
        this.tourElement.style.left = `${rect.left + window.scrollX}px`;
        
        // Update content
        this.tourElement.innerHTML = `
            <div class="tour-content">
                <h3 class="text-lg font-semibold mb-2">${step.title}</h3>
                <p class="text-gray-600 dark:text-gray-400 mb-4">${step.content}</p>
                <div class="flex justify-between items-center">
                    <div class="flex space-x-2">
                        ${this.steps.map((_, index) => `
                            <div class="w-2 h-2 rounded-full ${index === this.currentStep ? 'bg-primary-600' : 'bg-gray-300'}"></div>
                        `).join('')}
                    </div>
                    <div class="flex space-x-2">
                        <button class="btn-secondary" onclick="guidedTour.previous()">
                            {{ "السابق" if lang == "ar" else "Previous" }}
                        </button>
                        <button class="btn-gradient" onclick="guidedTour.next()">
                            ${this.currentStep === this.steps.length - 1 ? 
                                '{{ "إنهاء" if lang == "ar" else "Finish" }}' : 
                                '{{ "التالي" if lang == "ar" else "Next" }}'}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        this.tourElement.classList.remove('hidden');
        
        // Highlight target
        target.classList.add('tour-highlight');
    }
    
    next() {
        const currentTarget = document.querySelector(this.steps[this.currentStep].target);
        if (currentTarget) {
            currentTarget.classList.remove('tour-highlight');
        }
        
        this.currentStep++;
        
        if (this.currentStep >= this.steps.length) {
            this.end();
        } else {
            this.showStep();
        }
    }
    
    previous() {
        const currentTarget = document.querySelector(this.steps[this.currentStep].target);
        if (currentTarget) {
            currentTarget.classList.remove('tour-highlight');
        }
        
        this.currentStep--;
        
        if (this.currentStep < 0) {
            this.currentStep = 0;
        }
        
        this.showStep();
    }
}

// Initialize guided tour
const guidedTour = new GuidedTour();

// Check if tour should start automatically
document.addEventListener('DOMContentLoaded', function() {
    if (!localStorage.getItem('tour_completed')) {
        setTimeout(() => guidedTour.start(), 1000);
    }
}); 