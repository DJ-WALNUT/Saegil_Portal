document.addEventListener('DOMContentLoaded', function() {
    const categoryContainer = document.querySelector('.category-container');
    const pages = document.querySelectorAll('.category-page');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const currentCounter = document.querySelector('.current-page');
    const totalCounter = document.querySelector('.total-pages');

    if (!categoryContainer || pages.length === 0) {
        // 카테고리 페이지가 없으면 스크립트 실행 중단
        if (prevBtn) prevBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'none';
        return;
    }

    let currentPage = 0;
    const totalPages = pages.length;

    totalCounter.textContent = totalPages;
    updatePagination();

    function updatePagination() {
        currentCounter.textContent = currentPage + 1;
        prevBtn.disabled = currentPage === 0;
        nextBtn.disabled = currentPage === totalPages - 1;
        
        // 버튼 활성화/비활성화 시 색상 변경
        prevBtn.style.color = currentPage === 0 ? '#dee2e6' : '';
        nextBtn.style.color = currentPage === totalPages - 1 ? '#dee2e6' : '';
    }

    nextBtn.addEventListener('click', () => {
        if (currentPage < totalPages - 1) {
            currentPage++;
            const pageOffset = pages[currentPage].offsetLeft;
            categoryContainer.scrollTo({ left: pageOffset, behavior: 'smooth' });
            updatePagination();
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentPage > 0) {
            currentPage--;
            const pageOffset = pages[currentPage].offsetLeft;
            categoryContainer.scrollTo({ left: pageOffset, behavior: 'smooth' });
            updatePagination();
        }
    });

    // --- 물품 선택 (장바구니) 기능 ---
    const itemGrid = document.querySelector('.item-selection-section');
    const cartContainer = document.getElementById('cart-items');
    const selectedItemsInput = document.getElementById('selected-items-input');
    const submitButton = document.getElementById('submit-btn');
    const cartPlaceholder = document.querySelector('.cart-placeholder');

    let selectedItems = new Set();

    if (itemGrid) {
        itemGrid.addEventListener('click', function(e) {
            const card = e.target.closest('.item-card');
            if (card) {
                const itemName = card.dataset.itemName;
                const isSelected = selectedItems.has(itemName);
                
                // 선택 상태 토글
                card.classList.toggle('selected', !isSelected);

                if (isSelected) {
                    selectedItems.delete(itemName);
                } else {
                    selectedItems.add(itemName);
                }
                updateCart();
            }
        });
    }
    
    function updateCart() {
        if (!cartContainer || !selectedItemsInput) return;
        cartContainer.innerHTML = '';
        if (selectedItems.size === 0) {
            if (cartPlaceholder) cartContainer.appendChild(cartPlaceholder);
        } else {
            selectedItems.forEach(item => {
                const tag = document.createElement('div');
                tag.className = 'cart-item-tag';
                tag.textContent = item;
                cartContainer.appendChild(tag);
            });
        }
        selectedItemsInput.value = Array.from(selectedItems).join(',');
        if (submitButton) submitButton.disabled = selectedItems.size === 0;
    }
    
    if (itemGrid) updateCart();
});