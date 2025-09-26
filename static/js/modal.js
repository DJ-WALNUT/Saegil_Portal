document.addEventListener('DOMContentLoaded', function() {
    // --- 반납 처리 모달 ---
    const returnModal = document.getElementById('return-modal');
    if (returnModal) {
        const returnBtns = document.querySelectorAll('.btn-return');
        returnBtns.forEach(button => {
            button.addEventListener('click', function() {
                const logIndex = this.dataset.logIndex;
                returnModal.querySelector('#modal-log-index').value = logIndex;
                returnModal.style.display = 'flex';
            });
        });
        returnModal.querySelector('.modal-close-btn').addEventListener('click', () => returnModal.style.display = 'none');
    }

    // --- 대여 수락 모달 ---
    const approveModal = document.getElementById('approve-modal');
    if (approveModal) {
        const approveBtns = document.querySelectorAll('.btn-approve');
        approveBtns.forEach(button => {
            button.addEventListener('click', function() {
                const logIndex = this.dataset.logIndex;
                approveModal.querySelector('#modal-log-index').value = logIndex;
                approveModal.style.display = 'flex';
            });
        });
        approveModal.querySelector('.modal-close-btn').addEventListener('click', () => approveModal.style.display = 'none');
    }

    // 모달 외부 클릭 시 닫기
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-overlay')) {
            e.target.style.display = 'none';
        }
    });
});