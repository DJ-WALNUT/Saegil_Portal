window.addEventListener('load', () => {
    // --- 1. 스크립트 시작 확인 ---
    console.log("✅ 스크립트 파일이 로드되었습니다. (window.onload)");

    const sliderContent = document.querySelector('.scroll-content');
    const parentContainer = document.querySelector('.scroll-container');

    // --- 2. HTML 요소 확인 ---
    console.log("👉 .scroll-content 요소:", sliderContent);
    console.log("👉 .scroll-container 요소:", parentContainer);

    if (!sliderContent || !parentContainer) {
        console.error("❌ 스크롤에 필요한 HTML 요소를 찾지 못했습니다. 클래스 이름을 확인하세요.");
        return;
    }

    let currentPosition = 0;
    let isDown = false;
    let startX;
    let initialPosition;
    let autoScrollTimer;
    const scrollSpeed = 0.5;

    const updatePosition = () => {
        const halfWidth = sliderContent.scrollWidth / 2;
        if (currentPosition <= -halfWidth) {
            currentPosition += halfWidth;
        }
        sliderContent.style.transform = `translateX(${currentPosition}px)`;
    };

    const autoScroll = () => {
        // --- 5. 자동 스크롤 확인 ---
        // 이 메시지가 계속 출력되어야 합니다.
        console.log("📜 자동 스크롤 실행 중...");
        currentPosition -= scrollSpeed;
        updatePosition();
    };

    const startAutoScroll = () => {
        clearInterval(autoScrollTimer);
        autoScrollTimer = setInterval(autoScroll, 10);
        console.log("🚀 자동 스크롤을 시작합니다.");
    };

    const stopAutoScroll = () => {
        clearInterval(autoScrollTimer);
        console.log("🛑 자동 스크롤을 중지합니다.");
    };

    const start = (e) => {
        // --- 3. 드래그 시작 확인 ---
        console.log("🖱️ 드래그가 시작되었습니다 (start 이벤트).");
        stopAutoScroll();
        isDown = true;
        sliderContent.style.transition = 'none';
        startX = e.pageX || e.touches[0].pageX;
        initialPosition = currentPosition;
    };

    const end = () => {
        if (!isDown) return; // 드래그 시작도 안했는데 end 이벤트가 발생하는 것을 방지
        console.log("🖐️ 드래그가 종료되었습니다 (end 이벤트).");
        isDown = false;
        sliderContent.style.transition = 'transform 0.3s ease';
        setTimeout(startAutoScroll, 3000);
    };

    const move = (e) => {
        if (!isDown) return;
        // --- 4. 드래그 중 움직임 확인 ---
        console.log("💨 드래그 중입니다 (move 이벤트).");
        e.preventDefault();
        const currentX = e.pageX || e.touches[0].pageX;
        const walk = currentX - startX;
        currentPosition = initialPosition + walk;
        updatePosition();
    };

    parentContainer.addEventListener('mousedown', start);
    parentContainer.addEventListener('mouseleave', end);
    parentContainer.addEventListener('mouseup', end);
    parentContainer.addEventListener('mousemove', move);

    parentContainer.addEventListener('touchstart', start, { passive: false });
    parentContainer.addEventListener('touchend', end);
    parentContainer.addEventListener('touchmove', move, { passive: false });

    startAutoScroll();
});