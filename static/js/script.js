document.addEventListener('DOMContentLoaded', function() {

    // --- 물품 선택 (장바구니) 기능 ---
    const itemGrid = document.querySelector('.item-grid');
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
                card.classList.toggle('selected');

                if (selectedItems.has(itemName)) {
                    selectedItems.delete(itemName);
                } else {
                    selectedItems.add(itemName);
                }
                updateCart();
            }
        });
    }

    function updateCart() {
        // 기존 태그 모두 삭제
        cartContainer.innerHTML = '';
        
        if (selectedItems.size === 0) {
            if (cartPlaceholder) {
                cartContainer.appendChild(cartPlaceholder);
            }
        } else {
            selectedItems.forEach(item => {
                const tag = document.createElement('div');
                tag.className = 'cart-item-tag';
                tag.textContent = item;
                cartContainer.appendChild(tag);
            });
        }
        
        // 숨겨진 input 값 업데이트
        selectedItemsInput.value = Array.from(selectedItems).join(',');

        // 대여 버튼 활성화/비활성화
        if (submitButton) {
            submitButton.disabled = selectedItems.size === 0;
        }
    }
    
    // 페이지 로드 시 초기화
    if (itemGrid) {
        updateCart();
    }


    // --- 모바일 햄버거 메뉴 기능 ---
    const hamburgerBtn = document.querySelector('.hamburger-btn');
    const mainNav = document.querySelector('.main-nav');

    if (hamburgerBtn && mainNav) {
        hamburgerBtn.addEventListener('click', () => {
            mainNav.classList.toggle('active');
        });
    }

    // --- 추가된 기능: 반납 처리 모달 ---
    const returnModal = document.getElementById('return-modal');
    const modalCloseBtn = document.querySelector('.modal-close-btn');
    const modalLogIndexInput = document.getElementById('modal-log-index');
    const returnButtons = document.querySelectorAll('.btn-return');

    returnButtons.forEach(button => {
        button.addEventListener('click', function() {
            const logIndex = this.dataset.logIndex;
            modalLogIndexInput.value = logIndex;
            returnModal.style.display = 'flex';
        });
    });

    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', function() {
            returnModal.style.display = 'none';
        });
    }

    if (returnModal) {
        returnModal.addEventListener('click', function(e) {
            // 모달 바깥의 어두운 배경을 클릭하면 닫히도록
            if (e.target === returnModal) {
                returnModal.style.display = 'none';
            }
        });
    }
});