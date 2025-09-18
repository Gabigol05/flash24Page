// Script para mejorar la experiencia en dispositivos móviles
document.addEventListener('DOMContentLoaded', function() {
    // Añadir clase activa a los elementos al tocarlos (para mejorar feedback táctil)
    const interactiveElements = document.querySelectorAll('button, select, a, .alert-item, tr');
    
    interactiveElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.classList.add('touch-active');
        });
        
        element.addEventListener('touchend', function() {
            this.classList.remove('touch-active');
        });
        
        element.addEventListener('touchcancel', function() {
            this.classList.remove('touch-active');
        });
    });
    
    // Mejorar la experiencia con la modal en dispositivos táctiles
    const modalOverlay = document.getElementById('alertModal');
    
    if (modalOverlay) {
        let touchStartY = 0;
        let touchEndY = 0;
        
        modalOverlay.addEventListener('touchstart', function(e) {
            touchStartY = e.changedTouches[0].screenY;
        }, {passive: true});
        
        modalOverlay.addEventListener('touchend', function(e) {
            touchEndY = e.changedTouches[0].screenY;
            
            // Si el usuario hace un gesto de deslizar hacia abajo (más de 50px)
            if (touchEndY - touchStartY > 50 && e.target === this) {
                closeModal();
            }
        }, {passive: true});
    }
});

// Añadir estilos para el feedback táctil
const touchStyle = document.createElement('style');
touchStyle.textContent = `
    .touch-active {
        opacity: 0.8;
        transform: scale(0.98);
        transition: transform 0.1s, opacity 0.1s;
    }
    
    @media (hover: hover) {
        .btn:hover, a:hover, .modal-btn:hover, .alert-item:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
    }
`;
document.head.appendChild(touchStyle);